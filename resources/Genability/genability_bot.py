import os
import shutil
import sys
import time
import traceback
import re

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
from PIL import Image

load_dotenv()

sys.path.append(os.getenv("RESOURCES"))

from customlogging import logger
from ChromeScreenshot.screenshot import Screenshot


class UnableToLogin(Exception):
    pass


def get_rate_info(
    driver: webdriver,
    wait: WebDriverWait,
    utility_id: str,
    zip_code: str,
    utility_name: str,
    screenshot_folder: str,
) -> int:
    """
    Get Rate Information from Genability for given ID and Zip Code
    :param driver: Selenium Webdriver
    :param wait: WebDriver wait
    :param utility_id: Utility Company ID
    :param zip_code: Zip Code
    :param utility_name: Utility Name from Excel List
    :param screenshot_folder: Folder where Screenshots should be stored
    :return: 0 if successful -1 if unsuccessful
    """
    try:
        screenshot_path = os.path.join(screenshot_folder, utility_name + ".png")
        found_rate_id = False

        # Search For Utility Company with ID, ZipCode and Country Set as United States
        driver.get("https://dash.genability.com/explorer/utilities")

        wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/input")
            )
        )

        search_bar = driver.find_element(
            By.XPATH, "/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/input"
        )
        search_bar.send_keys(utility_id)

        # zip_code_input = driver.find_element(
        #     By.XPATH, "/html/body/div[1]/div[3]/div/div/div[1]/div[2]/div[1]/input"
        # )
        # zip_code_input.send_keys(zip_code)

        country_drop_down = driver.find_element(
            By.XPATH, "/html/body/div[1]/div[3]/div/div/div[1]/div[2]/div[2]"
        )
        country_drop_down.click()

        wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, """//*[@id="ui-select-choices-row-0-0"]""")
            )
        )
        united_states = driver.find_element(
            By.XPATH, """//*[@id="ui-select-choices-row-0-0"]"""
        )
        united_states.click()

        time.sleep(5)

        # Iterate through Table rows to get item which matches our Utility Companies ID

        try:
            wait.until(
                ec.element_to_be_clickable(
                    (
                        By.XPATH,
                        """/html/body/div[1]/div[3]/div/div/div[4]/div/p""",
                    )
                )
            )

            search_results = driver.find_element(
                By.XPATH, """/html/body/div[1]/div[3]/div/div/div[4]/div/p"""
            )
            search_results_text = search_results.text.strip()
        except TimeoutException:
            logger.info(
                f"No Results found for {utility_name} with ID {utility_id} and Zip Code {zip_code}"
            )
            return -1
        except NoSuchElementException:
            logger.info(
                f"No Results found for {utility_name} with ID {utility_id} and Zip Code {zip_code}"
            )
            return -1

        pattern = r"(\d+)\s-\s(\d+)\sof\s(\d+)\sUtilities"
        mo = re.search(pattern, search_results_text)

        if mo:
            first, page_number, total_number = mo.groups()
            logger.info(
                f"total results: {total_number}, number of results in current page: {page_number}"
            )
        else:
            logger.info(f"No result found for id:{utility_id} with zip:{zip_code}")
            return -1
        if page_number == 0:
            logger.info(
                f"No Results found for {utility_name} with ID {utility_id} and Zip Code {zip_code}"
            )
            return -1
        page_number = int(page_number) + 1

        for row in range(1, page_number):
            id_element = driver.find_element(
                By.XPATH,
                f"/html/body/div[1]/div[3]/div/div/table/tbody/tr[{row}]/td[3]",
            )
            id_number = id_element.text.strip()

            if id_number == utility_id:
                logger.info("Found rate id, navigating to Utility Summary Page")
                id_element.click()
                found_rate_id = True
                break

        if not found_rate_id:
            logger.info(
                f"Unable to find rate id for id:{utility_id} with zip:{zip_code}"
            )
            return -1

        # Go to Utility Summary Page > Tariffs > Residential Tariff > Calculator

        wait.until(
            ec.text_to_be_present_in_element(
                (By.XPATH, """/html/body/div[1]/div[3]/div[2]/div/h1"""),
                "Utility Summary",
            )
        )

        tariff_link = driver.find_element(
            By.XPATH, """/html/body/div[1]/div[3]/div[2]/ul/li[2]/ul/li[1]/a"""
        )
        logger.info("Navigating to Tariff Page")
        tariff_link.click()

        wait.until(
            ec.text_to_be_present_in_element(
                (By.XPATH, """/html/body/div[1]/div[3]/div[2]/div/h1"""),
                "Tariffs",
            )
        )

        wait.until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    """/html/body/div[1]/div[3]/div[2]/div/table/tbody/tr[1]/td[4]""",
                )
            )
        )

        residential_link = driver.find_element(
            By.XPATH,
            """/html/body/div[1]/div[3]/div[2]/div/table/tbody/tr[1]/td[4]""",
        )

        if residential_link.text.strip() not in [
            "Residential",
            "Residential - Single",
            "Domestic",
            "Residential and Religious",
        ]:
            raise Exception(
                "element residential_link does not point towards Residential Tariff"
            )
        logger.info("Navigating to Residential Tariff Summary")
        residential_link.click()

        wait.until(
            ec.text_to_be_present_in_element(
                (
                    By.XPATH,
                    """/html/body/div[1]/div[3]/div[2]/div/div[1]/div[1]/div/h1""",
                ),
                "Tariff Summary",
            )
        )

        calculater_link = driver.find_element(
            By.XPATH, """/html/body/div[1]/div[3]/div[2]/ul/li[3]/ul/li"""
        )
        logger.info("Navigating to Calculator")
        calculater_link.click()

        # Calculate Rate and Take Screenshot

        wait.until(
            ec.text_to_be_present_in_element(
                (By.XPATH, """/html/body/div[1]/div[3]/div[2]/div/div[1]/div/div/h1"""),
                "Calculator",
            )
        )

        wait.until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    """/html/body/div[1]/div[3]/div[2]/div/div[1]/gen-calculator/div/div[1]/div[5]/a""",
                )
            )
        )

        calculate_button = driver.find_element(
            By.XPATH,
            """/html/body/div[1]/div[3]/div[2]/div/div[1]/gen-calculator/div/div[1]/div[5]/a""",
        )
        logger.info("Calculating Rate")
        actions = ActionChains(driver)
        actions.move_to_element(calculate_button).click().perform()

        wait.until(
            ec.text_to_be_present_in_element(
                (
                    By.XPATH,
                    """/html/body/div[1]/div[3]/div[2]/div/div[1]/gen-calculator/div/div[3]/h2""",
                ),
                "Result Details",
            )
        )

        logger.info("Taking Screenshot")
        screenshot = Screenshot()
        screenshot.screenshot_zoom_out(driver, screenshot_path)
        if os.path.exists(screenshot_path):
            return 0
        else:
            logger.info("Failed to take Screenshot")
            return -1

    except Exception as error:
        logger.info("Bot ran into exception while getting rate info")
        logger.info(error)
        logger.info(traceback.print_exc())
        return -1


def login(driver: webdriver, wait: WebDriverWait) -> int:
    """
    :param driver: Selenium Webdriver
    :param wait: Webdriver wait
    :return: 0 if successful -1 if unsuccessful
    """
    try:
        driver.get("https://dash.genability.com/explorer/utilities")

        try:
            wait.until(ec.presence_of_element_located((By.XPATH, "/html/body/div[2]")))

            logger.info("Logging into Genability")
            wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[2]/form/div[1]/input")
                )
            )
            email = driver.find_element(By.XPATH, "/html/body/div[2]/form/div[1]/input")
            email.send_keys(os.getenv("GENABILITY_USERNAME"))

            password = driver.find_element(
                By.XPATH, "/html/body/div[2]/form/div[2]/input"
            )
            password.send_keys(os.getenv("GENABILITY_PASSWORD"))

            login_button = driver.find_element(
                By.XPATH, "/html/body/div[2]/form/button"
            )
            login_button.click()

            return 0

        except TimeoutException:
            logger.info("Already Logged into Genability")
            return 0
    except Exception as error:
        logger.info("Ran into the following error while logging in")
        logger.info(error)
        logger.info(str(traceback.print_exc()))
        return -1


def image_to_pdf(input_folder: str, output_path: str) -> int:
    """
    Complies Images in the given directory into a single PDF file
    :param input_folder: file path of directory where screenshots are stored
    :param output_path: file name with path of where you want to store your file
    :return: 0 if successful -1 if unsuccessful
    """
    try:
        logger.info(f"Converting images in {input_folder} to PDF")
        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        image_list = []
        # Iterate through all files in the folder
        for file_name in os.listdir(input_folder):
            if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                logger.info(f"Appending {file_name} to image list")
                image_path = os.path.join(input_folder, file_name)
                image = Image.open(image_path)
                image.convert("RGB")
                image_list.append(image)

        pdf = image_list[0]
        pdf.save(output_path, save_all=True, append_images=image_list[1:])

    except Exception as error:
        logger.info("Error while converting to PDF")
        logger.info(error)
        return -1


def clear_data_files(screenshots_dir, output_pdf_file):
    """
    Clears the Genability/Data/Screenshot folder as well as the output.pdf file.
    Args:
        screenshots_dir: file path of screenshot directory
        output_pdf_file: file path of output pdf file with file name

    Returns: None

    """
    if os.path.exists(screenshots_dir):
        logger.info(f"Removing {screenshots_dir}")
        shutil.rmtree(screenshots_dir)
        os.mkdir(screenshots_dir)

    if os.path.exists(output_pdf_file):
        logger.info(f"Removing {output_pdf_file}")
        os.remove(output_pdf_file)


def genability_bot():
    """
    Run Genability Bot by calling this function
    """
    try:
        current_directory = os.getenv("GENABILITY_DIR")
        data_directory = os.path.join(current_directory, "data")
        screenshots_folder = os.path.join(data_directory, "Screenshots")
        utility_list_path = os.path.join(data_directory, "Genability Utility List.xlsx")
        output_pdf_file = os.path.join(data_directory, "Genability Utility Rates.pdf")
        cookies = os.path.join(current_directory, "cookies")
        logger.info("Beep Boop, Hello World!!!. Starting Genability Bot :D")
        logger.info("Reading Genability Utility List.xlsx")

        clear_data_files(screenshots_folder, output_pdf_file)

        utility_list = pd.read_excel(utility_list_path)
        utility_list_count = int(utility_list.shape[0])
        utility_list["Status"] = ""

        chrome_options = Options()
        prefs = {"download.default_directory": data_directory}
        chrome_options.add_experimental_option("prefs", prefs)
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"--user-data-dir={cookies}")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )
        wait = WebDriverWait(
            driver,
            60,
            1,
            [
                ElementNotInteractableException,
                ElementClickInterceptedException,
                NoSuchElementException,
            ],
        )
        logged_in = login(driver, wait)
        if logged_in == -1:
            raise UnableToLogin("Unable to log in with the provided credentials.")

        # get_rate_info(driver, wait, "1510", "18621", "UGI Electric", screenshots_folder)
        for index in range(utility_list_count):
            utility_id = str(utility_list["ID"][index])
            utility_name = str(utility_list["SFDC Name"][index])
            zip_code = str(utility_list["Zip Code"][index])
            logger.info(f"Getting Rate info for {utility_name}")
            retry = 5
            rate = get_rate_info(
                driver, wait, utility_id, zip_code, utility_name, screenshots_folder
            )
            while rate != 0 and retry != 0:
                rate = get_rate_info(
                    driver, wait, utility_id, zip_code, utility_name, screenshots_folder
                )
                retry -= 1
            if rate == 0:
                utility_list.loc[index, "Status"] = "Done"
            else:
                utility_list.loc[index, "Status"] = "Failed"
            utility_list.to_excel(os.path.join(data_directory, "report.xlsx"))

        image_to_pdf(screenshots_folder, output_pdf_file)

    except Exception as error:
        logger.info("Bot Ran into Exception")
        logger.info(error)
        logger.info(traceback.print_exc())
        driver.quit()

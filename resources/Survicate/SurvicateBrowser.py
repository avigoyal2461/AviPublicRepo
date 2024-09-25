import os
import sys

sys.path.append(os.environ['autobot_modules'])
# from browser import Browser, task
import time
from customlogging import logger
from Config import SURVICATE_USERNAME, SURVICATE_PASSWORD
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException


class SurvicateBrowser:
    """Login function"""
    def __init__(self, driver):
        self.driver = driver
        self.LOGIN_URL = r'https://panel.survicate.com/signin/'

    def Login(self):
        self.driver.get(self.LOGIN_URL)
        self.driver.maximize_window()
        time.sleep(5)
        try:
            logger.info("Survicate Reports Automation – Started login process.")

            WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.XPATH, '//input[@data-test-id="input" and @type="text"]'))
            ).send_keys(SURVICATE_USERNAME)
            WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.XPATH, '//input[@data-test-id="input" and @type="password"]'))
            ).send_keys(SURVICATE_PASSWORD)
            time.sleep(8)
            WebDriverWait(self.driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@class="s-new-button color-brand l-block"]'))
            ).click()
            time.sleep(10)
            header_div = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'Header_fefebfd381'))
            )
            assert header_div.is_displayed(), "Login was not successful."
            logger.info("Survicate Reports Automation – Login Successful")
            #self.Logout()
        except TimeoutException:
            raise TimeoutException("Timeout exception occurred during the login process.")
        except Exception as error:
            # logger.info(error)
            # self.driver.close()
            # self.driver.quit()
            raise

    def Logout(self):
        """Logout function"""
        try:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//div[@class="s-dropdown relative l-inline-block Dropdown_d9552876d0 air-left-half air-right" and @data-test-id="groupingContainer"]/button'))
                ).click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button[text()="Logout"]'))
                ).click()
                logger.info("Survicate Reports Automation – Logging Out from the Survicate Site.")
            except:
                pass
            self.driver.close()
            self.driver.quit()
        except Exception as error:
            logger.exception(f"Survicate Reports Automation – {error}")
            self.driver.close()
            self.driver.quit()
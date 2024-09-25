# Resource Folder Import
from copy import error
import os
import sys
sys.path.append(os.environ['autobot_modules'])

from config import SALES_API_KEY, SALES_USERNAME, SALES_PASSWORD, INSTALLS_API_KEY, INSTALLS_USERNAME, INSTALLS_PASSWORD, SITECAPTURE_BASE_URL
# Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
# from SiteCapture.config import username, password
from Configs.chromedriver_config import driver_path
from Salesforce.utilities import create_task as create_salesforce_task
from Files.FileHandler import FileHandler
from ContractCreation.Contract import Contract
import time
import os
import zipfile
from customlogging import logger


os_user_name = os.environ['USERNAME']
login_url = r'https://trinity-sales.sitecapture.com/login/auth'

class SiteCaptureResponse:
    def __init__(self, status, data={}, error=False) -> None:
        self.status = status
        self.data = data
        self.error = error

class SiteCapturePortal:
    def __init__(self):
        self.vars = {}
        self.site_capture_url = 'https://trinity-sales.sitecapture.com/login/auth'
        self.driver = None
        self.download_folder = f'C:\\Users\\{os_user_name}\\Desktop\\autobot\\SiteCapture\\downloads'
        self.file_handler = FileHandler()

    def reinit_drivers(self):
        try:
            self.driver.quit()
        except:
            logger.info("Couldn't find or close drivers...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"user-data-dir=C:\\Users\\{os_user_name}\\AppData\\Local\\Google\\Chrome\\User Data\\SiteCapture")  # this is the directory for the cookies
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)
        self.driver.implicitly_wait(10)

    def download_pictures(self, task) -> SiteCaptureResponse:
        """Downloads all photos for a given task."""
        try:
            self.reinit_drivers()
            self.driver.get(self.site_capture_url)
            try:
                self.login()
            except:
                logger.info('Already logged in...')
            found_sc = self.search_task(task)
            if not found_sc:
                logger.info('Exiting SC download, failed...')
                self.close()
                return SiteCaptureResponse('not found', error=True)
            zip_file = self.download_photos()
            path = self.unzip_file(zip_file, suffix=' - LOI')
            self.close()
            return SiteCaptureResponse('ok', data={'path':path})
        except Exception as e:
            logger.error(e)
            self.close()
            return SiteCaptureResponse('error', data={'error':e}, error=True)

    def download_pictures_for_contract(self, contract):
        """Downloads all photos for a contract."""
        try:
            self.reinit_drivers()
            self.driver.get(self.site_capture_url)
            try:
                self.login()
            except:
                logger.info('Already logged in...')
            found_sc = self.search_using_contract(contract)
            if not found_sc:
                logger.info('Exiting SC download, failed...')
                self.close()
                return 'not found'
            zip_file = self.download_photos()
            path = self.unzip_file(zip_file, suffix=' - LOI')
            self.close()
            return path
        except Exception as e:
            logger.error(e)
            self.close()
            return None

    def login(self):
        self.driver.find_element_by_id('username').send_keys(SALES_USERNAME)
        self.driver.find_element_by_id('password').send_keys(SALES_PASSWORD)
        self.driver.find_element_by_css_selector('a[name="sign-in"]').click()

    def search_sitecapture(self, query):
        logger.info(f'Searching for sitecapture using query: {query}')
        form_elem = self.driver.find_element_by_class_name('form-search')
        form_elem.find_element_by_css_selector('input[ng-model="fn.globalSearchText"]').send_keys(query)
        form_elem.find_element_by_css_selector('input[type="submit"]').click()
        time.sleep(3)

    def search_using_contract(self, contract):
            query = contract.direct_lead
            if 'DL-' in query:
                query = query.replace('DL-', '')
            self.search_sitecapture(query)
            last_name = contract.last_name.lower()
            if not self.select_last_name(last_name):
                address = contract.street_address
                self.search_for_address(address)
                found_result = self.select_last_name(last_name)
                if not found_result:
                    return False
            return True

    def search_task(self, task):
            query = task.directLead
            if 'DL-' in query:
                query = query.replace('DL-', '')
            self.search_sitecapture(query)
            last_name = task.lastName.lower()
            if not self.select_last_name(last_name):
                address = task.streetAddress
                self.search_for_address(address)
                found_result = self.select_last_name(last_name)
                if not found_result:
                    return False
            return True

    def select_last_name(self, last_name) -> bool:
        """
        Selects the site capture with the matching last name.
        """
        try:
            time.sleep(10)
            results = self.driver.find_elements_by_class_name('typeDesc') #  Fails if not results are found
        except:
            return False
        for result in results:
            result_name = result.find_element_by_css_selector('a').text.lower()
            logger.info(f'Found last name in SC: {result_name} and last name in SF: {last_name}')
            if last_name in result_name:
                result.find_element_by_css_selector('a').click()
                return True
        logger.info('No results found for site capture')
        return False

    def search_for_address(self, address):
        street_split = address.split(' ')
        query = street_split[:2]
        first_two_addr = ' '.join(query)
        logger.info(f'Searching for DL using backup: {first_two_addr}')
        form_elem = self.driver.find_element_by_class_name('form-search')
        input_box_elem = form_elem.find_element_by_css_selector('input[type="text"]')
        input_box_elem.send_keys(Keys.CONTROL, 'a')
        input_box_elem.send_keys(Keys.BACKSPACE)
        input_box_elem.send_keys(first_two_addr)
        form_elem.find_element_by_css_selector('input[type="submit"]').click()
        time.sleep(5)



    def select_first_result(self):
        """Attempts to select the first result found. If no results are found, returns False"""
        listed_elems = self.driver.find_elements_by_class_name('typeDesc')
        if not listed_elems:
            logger.info('No results found.')
            return False
        else:
            listed_elems[0].find_element_by_css_selector('a').click()
            return True

    def download_photos(self, subfolders=False):
        """Opens the download modal and downloads full quality photos for the current sitecapture page."""
        self.driver.find_element_by_css_selector('a[title="More options..."]').click()
        time.sleep(1)

        # self.driver.find_element_by_css_selector('a[ng-click="showImageZipModal()"]').click()
        self.driver.find_element_by_xpath("//*[contains(text(), 'Download Zip File...')]").click()
        time.sleep(1.5)

        # Include originals checkbox
        originals_box = self.driver.find_element_by_css_selector('input[ng-model="imagezip.originals"]')
        if not originals_box.is_selected():
            originals_box.click()

        # Create folders checkbox
        create_folders_box = self.driver.find_element_by_css_selector('input[ng-model="imagezip.folders"]')
        if subfolders:
            if not create_folders_box.is_selected():
                create_folders_box.click()
        else:
            if create_folders_box.is_selected():
                create_folders_box.click()

        time.sleep(1)
        # Download Button
        self.driver.find_element_by_css_selector('a[ng-click="hideImageZipModal()"]').click()

        # Wait for Download
        customer_name = self.driver.find_element_by_css_selector('h1').text.strip()
        customer_name = customer_name.replace('(', '') # Parentheses are removed from the download name by sitecapture
        customer_name = customer_name.replace(')', '')
        download_path = self.download_folder + '\\' + customer_name + '.zip'
        counter = 0
        while not os.path.exists(download_path):
            time.sleep(3)
            counter += 1
            if counter > 20:
                break
        return self.file_handler.get_newest_path_in_folder(self.download_folder)
        

    def get_newest_path_in_folder(self, folder_path):
        folder_files = os.listdir(folder_path)
        logger.info(folder_files)
        file_names = [os.path.abspath(os.path.join(folder_path, file_name)) for file_name in folder_files]
        logger.info(file_names)
        sorted_file_names = sorted(file_names, key=os.path.getmtime, reverse=True)
        file_name = sorted_file_names[0]
        logger.info(file_name)
        return os.path.join(folder_path, file_name)

    def unzip_file(self, file_path, suffix=''):
        """
        Extracts all files to folder named as zip file. Deletes zip file. Sets photo download path to new folder.
        """
        destination_folder_path = file_path.replace('.zip', '')
        destination_folder_path = destination_folder_path  + suffix
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(destination_folder_path)
        os.remove(file_path)
        logger.info('Extracted and deleted zip file...')
        return destination_folder_path
        


    def close(self):
        try:
            self.driver.quit()
        except:
            logger.info('Driver already quit or not found...')


if __name__ == '__main__':
    tc = Contract("0063g000008qY7eAAE")
    sc = SiteCapturePortal()
    sc.download_pictures_for_contract(tc)
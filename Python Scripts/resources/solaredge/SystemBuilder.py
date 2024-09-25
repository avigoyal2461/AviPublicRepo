# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from Configs.chromedriver_config import driver_path
from BotUpdate.Update import update_bot_status
OS_USERNAME = os.environ['username']


class SystemBuilder():
    """"""
    def __init__(self):
        self.driver = None
        self.name_search = None
        self.january_production = None
        self.february_production = None
        self.march_production = None
        self.april_production = None
        self.may_production = None
        self.june_production = None
        self.july_production = None
        self.august_production = None
        self.september_production = None
        self.october_production = None
        self.november_production = None
        self.december_production = None

    def reinit_drivers(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\SystemBuilder")  # this is the directory for the cookies
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)

    
    def close(self):
        try:
            self.driver.quit()
        except:
            print('Driver already closed...')

    def set_site_data(self, site_info):
        try:
            self.name_search = site_info["name"]
            self.january_production = site_info["jan"].split('.')[0]
            self.february_production = site_info["feb"].split('.')[0]
            self.march_production = site_info["mar"].split('.')[0]
            self.april_production = site_info["apr"].split('.')[0]
            self.may_production = site_info["may"].split('.')[0]
            self.june_production = site_info["jun"].split('.')[0]
            self.july_production = site_info["jul"].split('.')[0]
            self.august_production = site_info["aug"].split('.')[0]
            self.september_production = site_info["sep"].split('.')[0]
            self.october_production = site_info["oct"].split('.')[0]
            self.november_production = site_info["nov"].split('.')[0]
            self.december_production = site_info["dec"].split('.')[0]
            print('Site info set...')
            return True
        except:
            print('Invalid site info...')
            return False

    def build_from_json(self, site_info):
        try:
            return self.build_from_json_inside(site_info)
        except Exception as e:
            print(e)
            self.close()
    
    def build_from_json_inside(self, site_info):
        self.reinit_drivers()
        if not self.set_site_data(site_info):
            self.close()
        self.driver.get("https://monitoring.solaredge.com/solaredge-web/p/home")
        print("GET success, waiting 10 seconds to load elements...")
        time.sleep(5)
        while self.driver.current_url == r'https://monitoring.solaredge.com/solaredge-web/p/login':
            print('Not logged in, sleeping...')
            update_bot_status('bot1', 'Not Logged In')
            time.sleep(30)
        update_bot_status('bot1', f'Building System For: {self.name_search}')
        time.sleep(10)
        
        # Input search
        try:
            self.driver.find_element_by_css_selector('input[name="filter"]').click()
            self.driver.find_element_by_css_selector('input[name="filter"]').send_keys(Keys.CONTROL + "a")
            self.driver.find_element_by_css_selector('input[name="filter"]').send_keys(Keys.DELETE)
            self.driver.find_element_by_css_selector('input[name="filter"]').send_keys(self.name_search)
            self.driver.find_element_by_css_selector('input[name="filter"]').send_keys(Keys.ENTER)
            time.sleep(6)
        except:
            self.close()
            print('Unable to find search box...')
            return False

        # Select first result
        try:
            search_results = self.driver.find_elements_by_class_name('x-grid3-row-table')
            if not search_results:
                print('No search results found...')
                self.close()
                return True
            site_link_elem = search_results[0].find_element_by_class_name('se-link')
            print(site_link_elem.text)
            site_link_elem.click()
            time.sleep(10)
        except:
            print('Unable to select search results...')
            self.close()
            return False

        # Get Admin Performance tab
        # Convert url from .../{site_id}/#/dashboard To .../{site_id}/#/admin/performance
        try:
            current_url = self.driver.current_url
            new_url = current_url.replace('dashboard', r'admin/performance')
            self.driver.get(new_url)
            time.sleep(6)
        except:
            print('Unable to get performance tab URL...')
            self.close()
            return False

        # Select Estimated Energy Tab
        try:
            self.driver.find_element_by_id('se-admin-performance-tab__se-expected-energy-tab').click()
            time.sleep(1)
            self.driver.find_element_by_css_selector('input[name="isFeatureEnabled"]').click()
            time.sleep(3)
        except:
            print('Unable to open production input...')
            self.close()
            return False

        # Input production values
        try:
            self.driver.find_element(By.NAME, "Jan").send_keys(self.january_production)
            self.driver.find_element(By.NAME, "Feb").send_keys(self.february_production)
            self.driver.find_element(By.NAME, "Mar").send_keys(self.march_production)
            self.driver.find_element(By.NAME, "Apr").send_keys(self.april_production)
            self.driver.find_element(By.NAME, "May").send_keys(self.may_production)
            self.driver.find_element(By.NAME, "Jun").send_keys(self.june_production)
            self.driver.find_element(By.NAME, "Jul").send_keys(self.july_production)
            self.driver.find_element(By.NAME, "Aug").send_keys(self.august_production)
            self.driver.find_element(By.NAME, "Sep").send_keys(self.september_production)
            self.driver.find_element(By.NAME, "Oct").send_keys(self.october_production)
            self.driver.find_element(By.NAME, "Nov").send_keys(self.november_production)
            self.driver.find_element(By.NAME, "Dec").send_keys(self.december_production)
        except:
            print('Input production values failure, system already built...')
            self.close()
            return True

        # Submit production values
        try:
            save_elems = self.driver.find_elements_by_xpath('//button[text()="Save"]')
            save_elems[-1].click()
            time.sleep(4)
        except:
            print('Production value submit button failure...')
            self.close()
            return False

        time.sleep(3)
        # Close
        self.driver.quit()
        print('System build successfully...')
        return True

if __name__ == "__main__":
	builder = SystemBuilder()
	builder.build_from_json({'test':'2134'})

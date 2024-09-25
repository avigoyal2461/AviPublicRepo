import os
import sys
sys.path.append(os.environ['autobot_modules'])
#from browser import Browser, task
import time
from customlogging import logger
from config import SPOTIO_USERNAME, SPOTIO_PASSWORD
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# SPOTIO_USERNAME = 'bryan.bigica@trinitysolarsystems.com'
# SPOTIO_PASSWORD = 'Trinity2020'

# class SpotioBrowser(Browser):
    
#     USER_EXPORT_URL = r'https://app.spotio2.com/settings/users'

#     def __init__(self, user):
#         super().__init__(user=user)
#         self.LOGIN_URL = r'https://app.spotio2.com/login'

#     def login(self):
#         self.driver.get(self.LOGIN_URL)
#         self.driver.find_element_by_css_selector('input[name="email"]').send_keys(SPOTIO_USERNAME)
#         self.driver.find_element_by_css_selector('input[name="password"]').send_keys(SPOTIO_PASSWORD)
#         self.driver.find_element_by_class_name('sign-content_button').click()

#     @task
#     def export_user_csv(self) -> str:
#         """
#         Exports the user csv from spotio. Downloads to folder and returns path to file.
#         """
#         self.login()
#         return ""

class Spotio:  
    def __init__(self, driver):
        self.driver = driver 
        self.LOGIN_URL = r'https://app.spotio2.com/login'      

    def Login(self):            
            self.driver.get(self.LOGIN_URL) 
            self.driver.maximize_window()
            time.sleep(5) 
            try:
                WebDriverWait(self.driver, 200).until(
                    EC.presence_of_element_located((By.NAME, "email"))).send_keys(SPOTIO_USERNAME) 
                WebDriverWait(self.driver, 100).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'sign-content_button'))).click()
                time.sleep(8)  
                WebDriverWait(self.driver, 200).until(
                    EC.presence_of_element_located((By.NAME, "password"))).send_keys(SPOTIO_PASSWORD)
                WebDriverWait(self.driver, 100).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'sign-content_button'))).click() 
                time.sleep(8)  
                logger.info("Spotio Login Successful")       
            except Exception as error:               
                self.driver.close()
                self.driver.quit()
                return "Spotio Login Failure"
    
    def Logout(self):
        try:
            account = WebDriverWait(self.driver, 100).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "header-user_name")))
            account.click()
            time.sleep(3)
            logout = WebDriverWait(self.driver, 100).until(
                                EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Logout']")))
            logout.click()
            time.sleep(5)
            self.driver.close()
            self.driver.quit()
            logger.info("Logging Out from Spotio after successful User Offboarding")
        except Exception as error:
            logger.exception(f"{error}")
            self.driver.close()
            self.driver.quit()
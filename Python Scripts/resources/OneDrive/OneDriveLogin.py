from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import sys
import os
sys.path.append(os.environ['autobot_modules'])
from config import MICROSOFT_USERNAME, MICROSOFT_PASSWORD
print(MICROSOFT_PASSWORD)

class Login():
    def login(driver):
        #username
        try:
            username = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="i0116"]')))
            username.send_keys(MICROSOFT_USERNAME)
            #clicks next
            driver.find_element(by=By.XPATH, value='//*[@id="idSIButton9"]').click()
            time.sleep(5)
        except:
            print("Passing the username")
            pass
        # time.sleep(2)

        # #clicks next
        # driver.find_element(by=By.XPATH, value='//*[@id="idSIButton9"]').click()
        # time.sleep(5)

        #password
        try:
            password = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#i0118')))
            time.sleep(5)
            password.send_keys(MICROSOFT_PASSWORD)
            time.sleep(5)
        except:
            print("Could not input password")

        #sign in
        try:    
            driver.find_element(by=By.XPATH, value='//*[@id="idSIButton9"]').click()
        except:
            print("Already logged in")

        time.sleep(10)
        #if page text has "stay signed in.. "
        try:
            page_text = driver.find_element(by=By.CSS_SELECTOR, value='body').text
            if "Stay signed in?" in page_text:
                driver.find_element(by=By.XPATH, value='//*[@id="idBtn_Back"]').click()
        except:
            print("Logging in...")
            pass

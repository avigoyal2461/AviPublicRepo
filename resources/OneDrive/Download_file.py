from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import sys
sys.path.append(os.environ['autobot_modules'])
OS_USERNAME = os.environ['USERNAME']

try:
    from OneDriveLogin import Login
except:
    from OneDrive.OneDriveLogin import Login
import glob

class OneDriveDownloads():
    def __init__(self):
        self.driver = None
    
    def download_file(self, url, download_path, file):
        prefs = {'download.default_directory' : download_path,
                        "download.prompt_for_download": False, #To auto download the file
                        "download.directory_upgrade": True,
                        "plugins.always_open_pdf_externally": True,
                        #removes the requirement to run a virus scan
                        "safebrowsing.disable_download_protection": True,
                        "savefile.default_directory": download_path
                    }
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(
                    f"--user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\OneDrive")
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        files = len(glob.glob(f"{download_path}/*xlsx"))

        self.driver.get(url)
        Login.login(self.driver)
        # self.driver.get(url)
        time.sleep(10)
        self.driver.maximize_window()
        #find sheet by text by iterating through all sheets
        sheet_counter = 1
        while True:
            try:
                # sheet = self.driver.find_element(by=By.XPATH, value=f'//*[@id="appRoot"]/div/div[2]/div/div/div/div[2]/div[2]/main/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div[{sheet_counter}]').text
                sheet = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="appRoot"]/div/div[2]/div/div/div/div[2]/div[2]/main/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div[{sheet_counter}]'))).text
                print(f"Searching for sheet, currently on: {sheet}")
                if file in sheet:
                    print("Found Desired sheet")
                    break
                else:
                    print("Appending Counter")
                    sheet_counter += 1
            except:
                break
            
        #when sheet is found, click the circle to download
        self.driver.find_element(by=By.XPATH, value=f'//*[@id="appRoot"]/div/div[2]/div/div/div/div[2]/div[2]/main/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div[{sheet_counter}]/div/div/div/div[1]/div').click()
        
        download = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Download']")))
        download.click()

        download_quit = 0
        while True:

                new_len_file = len(glob.glob(f"{download_path}/*xlsx"))
                if files == new_len_file:
                    time.sleep(5)
                    print("Waiting on Download")
                    download_quit += 1
                    if download_quit == 100:
                        download.click()

                        download_quit = 0
                else:
                    self.downloaded_file = glob.glob(f"{download_path}/*xlsx")
                    if isinstance(self.downloaded_file, list):
                        self.downloaded_file = max(self.downloaded_file, key=os.path.getctime)

                        #self.downloaded_file = self.downloaded_file[0]
                    # self.driver.quit()
                    print("Download Complete")
                    time.sleep(3)
                    self.downloaded = True
                    break

        self.driver.quit()
        return self.downloaded_file

if __name__ == "__main__":
    a = OneDriveDownloads()
    print(a.download_file(url=r"https://trinitysolarsys-my.sharepoint.com/personal/joshuabeach_trinity-solar_com/_layouts/15/onedrive.aspx", download_path=r"C:\Users\AviGoyal\Desktop\PythonCode", file="Corporate Sales Calendar"))
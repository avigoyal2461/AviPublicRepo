from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

OS_USERNAME = os.environ['USERNAME']

class chromedrivertests():
    def __init__(self):
        #init will run as soon as we run the code, this will set objects to use through different methods( main one we want to set is chromedriver )
        download_path = "PATH TO HOLD DOWNLOADS"
        #prefs will be used as rules for chrome, not always needed but useful to force chrome to do what we want
        prefs = {'download.default_directory' : download_path,
                "download.prompt_for_download": False, #To auto download the file
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
                "safebrowsing.disable_download_protection": True
            }
        #signifies that we will use the prefs above, can be used to add a number of options, these are documented with selenium's site
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument(
                    f"--user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\Salesforce")
        #initializes the driver, self.driver can be used in any method we set
        # self.driver = webdriver.Chrome(executable_path=r"CHROMEDRIVER.EXE PATH", options=chrome_options)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
    def get_website(self):
        self.driver.get("https://dash.genability.com/explorer/tariffs/522/calculator")
        
    def wait_for_element(self):
        element = WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, 'XPATH TO AN ELEMENT')))
        #we can do any number of these to the element:
        # element.click()
        # element.send_keys(Keys.ENTER)
        # element.text - if we do this, we can print it like : print(element)

    def click_without_waiting(self):
        element = self.driver.find_element(by=By.XPATH, value='XPATH HERE')
        #as above, we can do any of these to the element as well
        # element.click()
        # element.send_keys(Keys.ENTER)
        # element.text - if we do this, we can print it like : print(element)

if __name__ == "__main__":
    a = chromedrivertests()
    a.get_website()
    # time.sleep(20)
    a.driver.find_element(by=By.XPATH, value='/html/body/div[2]/form/div[1]/input').send_keys("powerautomateteam@trinity-solar.com")
    a.driver.find_element(by=By.XPATH, value='/html/body/div[2]/form/div[2]/input').send_keys("pA951753!")
    a.driver.find_element(by=By.XPATH, value='/html/body/div[2]/form/button').click()
    time.sleep(5)
    a.driver.get("https://dash.genability.com/explorer/tariffs/522/calculator")
    try:
        time.sleep(2)
        a.driver.find_element("xpath", '/html/body/div[1]/div[3]/div[2]/div/div[1]/gen-calculator/div/div[1]/div[5]/a').click()
        print("Click calc")
    except:
        print("Mnaully click please")
        time.sleep(10)
        pass #/html/body/div[1]/div[3]/div[1]/div

    # element = a.driver.find_element('XPATH', '/html/body')
    # element_png = element.screenshot_as_png
    # with open("screenshot1.png", "wb") as file:
    #     file.write(element_png)
    # ele=a.driver.find_element("xpath", '/html/body')
    # print(ele.size['height'])
    # total_height = ele.size["height"]+1000
    # print(total_height)
    # a.driver.set_window_size(1920, total_height)
    # time.sleep(2)
    # a.driver.save_screenshot("screenshot1.png")
#get window size
    # a.driver.maximize_window()
    
    # S = lambda X: a.driver.execute_script('return document.body.parentNode.scroll'+X)
    # print(S)
    # print("scrolled window")
    # a.driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment                                                                                                                
    # a.driver.find_element(by=By.CSS_SELECTOR, value='body').screenshot('web_screenshot.png')
    # element = a.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[3]/div[2]/div/div[1]/gen-calculator/div/div[3]/div[2]/gen-table-ledger/table/tbody')
    # a.driver.execute_script("document.getElementByXPATH('/html/body/div[1]/div[3]/div[2]/div/div[1]/gen-calculator/div/div[3]/div[2]/gen-table-ledger/table/tbody').scrollIntoView();")
    # s = a.driver.get_window_size()
    # print(s)
    #obtain browser height and width
    # a.driver.find_element(by=By.CSS_SELECTOR, value='body').send_keys(Keys.PAGE_DOWN)
    # time.sleep(2)
    # w = a.driver.execute_script('return document.body.parentNode.scrollWidth')
    # h = a.driver.execute_script('return document.body.parentNode.scrollHeight')
    # h = int(h)
    # h += 10000
    # while h < 2000:
    #     h += 1
    #     print(h)
    # a.driver.execute_script("arguments[0].scrollIntoView();", element)
    #set to new window size
    # print(f"sizes: {w}, {h}")
    # a.driver.set_window_size(w, h)
    #obtain screenshot of page within body tag
    a.driver.maximize_window()
    time.sleep(5)
    a.driver.execute_script("document.body.style.zoom='50%'")
    a.driver.find_element(by=By.CSS_SELECTOR, value='body').screenshot("tariff.png")

    from PIL import Image
    image_1 = Image.open('tariff.png')
    im_1 = image_1.convert('RGB')
    im_1.save('tariff.pdf')
    time.sleep(2)
    a.driver.get("https://dash.genability.com/explorer/tariffs/522/calculator")

    # a.driver.set_window_size(s['width'], s['height'])


    # a.driver.quit()
    # a.wait_for_element()


        

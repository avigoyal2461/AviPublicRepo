# Resource Folder Import
import sys
import os
sys.path.append(os.environ['autobot_modules'])

from AutobotEmail.Outlook import outlook
try:
    from Salesforce.utilities import create_task
except:
    pass
from Sharepoint.connection import SharepointConnection
from Files.FileHandler import FileHandler
from Configs.chromedriver_config import driver_path
# from Sunnova.config import password, username
from config import SUNNOVA_USERNAME, SUNNOVA_PASSWORD
from customlogging import logger
import re
import time
#import fitz
import glob
import tabula
import shutil
import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

from selenium.common.exceptions import TimeoutException
# sys.path.append(os.environ['autobot_modules'])

# Imports
try:
    from models.alchemy_contract_creation_models import session
except ImportError:
    pass


OS_USERNAME = os.environ['USERNAME']
CREDIT_STATUS = 1
TITLE_URL_SUFFIX = 'titlecheck'
USAGE_URL_SUFFIX = 'usage'
SYSTEM_URL_SUFFIX = 'systemdesigns'
CREDIT_URL_SUFFIX = 'creditverification'
QUOTE_URL_SUFFIX = 'quotes'
UTILITY = 0
CURRENT_RATE_PLAN = 1
PROPOSED_RATE_PLAN = 2
UTILITY_ESCALATION = 3
USAGE_PERIOD = 4
ANNUAL_USAGE = 5
MODULE_MANUFACTURER = 0
MODULE_MODEL = 1
MODULE_QUANTITY = 2
INVERTER_MANUFACTURER = 3
INVERTER_MODEL = 4
INVERTER_QUANTITY = 5
RACKING = 6
MONITOR_MANUFACTURER = 7
MONITOR_MODEL = 8
SYSTEM_OTHER = 9
SHADE_TILT = 10
SHADE_AZIMUTH = 11
SHADE_AVAILABILITY = 12


class SunnovaResponse:
    """
    Holds response data.
    """

    def __init__(self, status, data={}, error=None):
        self.status = status
        self.data = data
        self.error = error

    def addData(self, data):
        self.data.update(data)

    def setStatus(self, status):
        self.status = status


class SunnovaPortal:
    """
    A wrapper for the sunnova portal. Should be treated like an API with long response times. Returns Sunnova Response objects.
    """

    def __init__(self):
        self.vars = {}
        self.start_url = 'https: //google.com'
        self.open_leads_url = 'https://sunnovaenergy.force.com/partnerconnect/s/open-leads#/openleads'
        self.home_url = 'https://sunnovaenergy.force.com/partnerconnect/s/#/dashboard'
        self.login_url = 'https://sunnovaenergy.force.com/partnerconnect/login'
        self.driver = None
        self.file_handler = FileHandler()
        self.download_folder = f'C:\\Users\\{OS_USERNAME}\\Downloads'
        self.main_window = None
        self.driver_path = r"C:\Users\RPAadmin\Desktop\automation\api\chromedriver.exe"
        self.outlook = outlook
        self.sharepoint = SharepointConnection()

    def reinit_drivers(self, prefs=None):
        self.close()
        chrome_options = webdriver.ChromeOptions()
        try:
            chrome_options.add_argument(
                f"--user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\Salesforce")
        except:
            pass
        if prefs:
            chrome_options.add_experimental_option('prefs', prefs)
            
            chrome_options.add_argument('--kiosk-printing')
            chrome_options.add_experimental_option("detach", True)
            print("Selected Download Folder")

            # self.driver = webdriver.Chrome(executable_path=self.driver_path, chrome_options=chrome_options)
            # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # else:
            # self.driver = webdriver.Chrome(executable_path=self.driver_path)
            # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install(), options=chrome_options)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        self.driver.implicitly_wait(10)
        self.main_window = self.driver.current_window_handle
        return self.driver

    # PARTNER SOLUTIONS
    def download_from_sharepoint(self, url=None, file=None, folder_path=None, unzip_path=None):
        """
        Downloads the invoice zip file from sharepoint, have to denote as a zip here otherwise it will not work
        """

        self.sharepoint.getFile(url=url, file=file, path=folder_path)

        try:
            unzip_path = os.path.join(unzip_path)

            unzip_path = os.path.normpath(unzip_path)

            os.mkdir(unzip_path)
        except:
            print("Path Already Created")

        if unzip_path != None:
            self.sharepoint.unzipFolder(folder_path, unzip_path)

        return True
    
    def Trueup_Invoice(self, folder_path, updater, completer):
        """
        Uploads given sunnova invoice to the Opportunity
        """
        # self.function = "Trueup_Invoice"
        # self.name = f"bot_{self.function}"
   
        try:
            invoice_paths = glob.glob(fr"{folder_path}\*")

            invoice_path = invoice_paths[0]
        except:
            invoice_path = invoice_paths
        file = invoice_path
        
        self.reinit_drivers()
        self.login()

        print(file)
        success_count = 0
        fail_count = 0
        full_counter = 0
        # final_ids = []
        # posted_or_failed = []
        # cols = ["Sunnova ID", "Uploaded"]
        #only one file now
        df = tabula.read_pdf(file, pages=1)[0]
        dfs = tabula.read_pdf(file, pages='all')
        for df in dfs:
            print(df)
            first_val = df.columns[6]
            first_val_uploaded = False
            print(f"First val / column header = {first_val}")
            counter = 0

            while True:
                try:
                    if not first_val_uploaded:
                        try:
                            print("Uploading First val")
                            # first_val_uploaded = True
                            updater("Uploading", first_val)
                            # self.bot_update.update_bot_status(self.name, f"Uploading {first_val}")

                            self.selectSystemProject(first_val)
                            time.sleep(5)
                            upload = self.upload_trueup_invoice(first_val)
                            if upload:
                                success_count += 1
                                completer(first_val)
                            else:
                                fail_count += 1
                            full_counter += 1
                        except:
                            print("Skipping First value")
                            pass
                        first_val_uploaded = True
                    else:
                        value = df[first_val].iloc[counter]
                        print(value)
                        # self.bot_update.update_bot_status(self.name, f"Uploading {value}")
                        self.selectSystemProject(value)
                        time.sleep(5)
                        updater("Uploading", value)
                        try:
                            upload = self.upload_trueup_invoice(value)
                        except:
                            upload = False

                        if upload:
                            success_count += 1
                            completer(value)
                        else:
                            fail_count += 1
                        full_counter += 1
                        counter += 1
                except:
                    print("Finished Parsing Invoice Sheet")
                # print("loop")
                    break
        # quit()
        self.close()
        
        time.sleep(5)
        try:
            shutil.rmtree(invoice_path, ignore_errors=True)
            print("Removed Invoice Path to clear up queue")
        except:
            print("second try")
            os.rmdir(invoice_path)
            pass

        return success_count, fail_count, full_counter
    
    def System_Invoice(self, folder_path, updater, completer):
        """
        Uploads given sunnova invoice to the Opportunity
        """
        prefs = {"download.prompt_for_download": False, #To auto download the file
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
                #removes the requirement to run a virus scan
                "safebrowsing.disable_download_protection": True,
                # 'printing.print_preview_sticky_settings.appState': json.dumps(settings),
                #sets download path when executing self.driver.execute_script(window.print();)
                #and saving it to : self.driver.execute_script("document.title = \'{}\'".format(file_name))
                # "savefile.default_directory": self.download_path
            }
        self.function = "Invoices"
        self.name = f"bot_{self.function}"
        # folder_path = r"C:\Users\RPAadmin\Desktop"
        # unzip_path = fr"{folder_path}\Invoices"
        # try:
        #     invoice_paths = glob.glob(fr"{unzip_path}\*")

        #     invoice_path = invoice_paths[0]
        # except:
        #     invoice_path = invoice_paths
        files = glob.glob(f"{folder_path}/*")

        self.reinit_drivers(prefs)
        self.login()
        # files = glob.glob(f"{invoice_path}/*")

        print(files)
        success_count = 0
        fail_count = 0
        full_counter = 0
        final_ids = []
        posted_or_failed = []
        cols = ["Sunnova ID", "Uploaded"]
        for file in files:
            # try:
            project_id = self.getLeaseId(file)
            print(project_id)
            final_ids.append(project_id)
            full_counter += 1
            try:
                updater(self.name, f"Uploading {project_id}", project_id)
                self.selectSystemProject(project_id)
                self.upload_system_invoice(file)
                print(f"Successfully Posted invoice to {project_id}")
                completer(self.name, project_id)
                success_count += 1
                posted_or_failed.append("Posted")
            except:
                print(f"Failed on {file}")
                fail_count += 1
                posted_or_failed.append("Failed")
                # pass
                continue

        self.close()

        time.sleep(5)
        try:
            shutil.rmtree(folder_path, ignore_errors=True)
            print("Removed Invoice Path to clear up queue")
        except:
            print("second try")
            os.rmdir(folder_path)
            pass
        return success_count, fail_count, full_counter

    def selectSystemProject(self, project_id, file_path=None, search_with=None):
        """
        Searches and selects the system project by ID and sends the invoice
        """
        retry = False
        self.searchSunnova(project_id)
        print(f"Selecting {project_id}")
        # time.sleep(10)

        try:                                                                                              #'/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div[5]/div[2]/div/div/table/tbody/tr/td[1]/a'
            # time.sleep(10)
            SystemProject = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div[5]/div[2]/div/div/table/tbody/tr/td[1]/a')))
            SystemProject.click()
        except Exception as e:
            if search_with != "addresses":
                print("No Results Found")
                return None
            print(e)
            try:
                project_counter = 1
                counters = []
                project_id = project_id.lower()
                while True:

                    try:
                        street_name = self.driver.find_element(by=By.XPATH, value=f'/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div/div/table/tbody/tr[{project_counter}]/td[4]/span')
                        street_name = street_name.text
                        street_name = street_name.lower()
                        length = len(street_name)
                        # street_name = street_name[0:length-6]
                        street_name = street_name[0:2]
                        print(street_name)

                        if street_name in project_id:
                            counters.append(project_counter)
                        project_counter += 1
                        print(project_id)

                    except Exception as e:

                        break
                        # pass
                list_counter = 0
                print(counters)
                for count in counters:
                    print(count)
                    lead = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div/div/table/tbody/tr[{count}]/td[1]/a")))
                    lead.click()
                    time.sleep(30)
                    while True:
                        try:
                            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))
                            break
                        except:
                            if counters.index(count) == len(counters) - 1:
                                break
                            self.searchSunnova(project_id)

                            time.sleep(10)
                    text = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))).text
                    if "System Project:" not in text:

                        self.searchSunnova(project_id)

                        time.sleep(10)
                        list_counter += 1

                    else:
                        break
                    list_counter += 1
            except:
                return

    def getLeaseId(self, file):
        """
        Uses the Fitz library to parse 
        PDF's, expecting an ID right after Lease ID entry, and System Size entry right after the printed ID
        """
        return None
        """
        print(file)
        text = ""
        with fitz.open(file) as doc:
            for page in doc:
                # text += page.get_text()
                text += page.getText()

        text2 = text.split("Lease ID:")[1]
        id = text2.split("System Size:")[0]
        id = id.replace("\n", "")
        return id
        """

    def time_conversion(self, list_of_times):
        """
        Takes time in mm/dd/yyyy h:mmAM OR mm/dd/yyyy h:mm AM
        format and converts to a datetime object and appends to a list so that we can find
        the most recent time -> max(list) or the first time -> min(list)
        """
        formatted_times = []
        for timeslot in list_of_times:
                try:
                    thedate, thetime, ampm = timeslot.split(" ")
                    month, day, year = thedate.split("/")
                    # hourminute, ampm = thetime.split(" ")
                    hour, minute = thetime.split(":")
                    if ampm == "PM" or ampm == "pm":
                        hour = int(hour)
                        # print(hour)
                        # print(type(hour))
                        # print(minute)
                        if hour == 12:
                            hour = 12
                        else:
                            hour = int(hour)
                            hour += 12
                            # hour = str(hour)
                    # print(hour)
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    hour = int(hour)
                    minute = int(minute)
                except:
                    thedate, thetime = timeslot.split(" ")
                    month, day, year = thedate.split("/")
                    if "AM" in thetime:
                        ampm = "AM"
                        thetime = thetime.replace("AM", "")
                    elif "PM" in thetime:
                        ampm = "PM"
                        thetime = thetime.replace("PM", "")
                    
                    # hourminute, ampm = thetime.split(" ")
                    hour, minute = thetime.split(":")
                    if ampm == "PM" or ampm == "pm":
                        hour = int(hour)
                        if hour == 12:
                            hour = 12
                        else:
                            # hour = int(hour)
                            hour += 12
                            # hour = str(hour)
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    hour = int(hour)
                    minute = int(minute)
                datetimevalue = datetime.datetime(year, month, day, hour, minute, 0)
                formatted_times.append(datetimevalue)
        return formatted_times

    def searchSunnova(self, project_id):
        """
        Searches through the system projects by ID / given value
        """
        try:
            self.driver.maximize_window()
        except:
            print("Driver already maxed")
            pass
        #TRY TO SWAP DRIVER TO PARENT FRAME IF WE ARE SEARCHING FOR BACK TO BACK OPPS (DOWNLOADING REQUIRES ENTRY INTO AN IFRAME, THIS WILL RETURN)
        try:
            self.driver.switch_to.parent_frame()
        except:
            print("Driver is already on parent frame")

        self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/header/div[1]/div[3]/div/div/div/div/div/div/div[2]/div[2]/div/input').click()
        self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/header/div[1]/div[3]/div/div/div/div/div/div/div[2]/div[2]/div/input').send_keys(Keys.CONTROL, 'a')
        self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/header/div[1]/div[3]/div/div/div/div/div/div/div[2]/div[2]/div/input').send_keys(Keys.BACKSPACE)

        self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/header/div[1]/div[3]/div/div/div/div/div/div/div[2]/div[2]/div/input').send_keys(project_id)
        time.sleep(5)
        
        self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/header/div[1]/div[3]/div/div/div/div/div/div/div[2]/div[2]/div/input').send_keys(Keys.ENTER)
        # self.driver.find_elements_by_xpath('/html/body/div[3]/header/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/input')[0].send_keys(Keys.ENTER)

    def download_system_details(self, download_path, type_of_contract=None):#\31 98\:0, #\31 98\:0, #\36 1\:1860\;a, #\31 83\:0
        """
        Downloads System Details from the System project page in a Sunnova project
        """
        #sets the main window of the driver to the initial chromedriver page to handle new tabs
        main_window = self.driver.current_window_handle

        # self.selectSystemProject(id)
        # print("System Details Download")
        time.sleep(5)
        # self.grab_iframe()
        try:
            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))
            print("Switched to Iframe")
        except:
            print("Already in IFRAME")

        SystemDetails = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sunnova-root"]/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail-old/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-page-card/mat-card/mat-card-content/div/div/dl[2]/dd[3]/app-skeleton-text/a')))
        SystemDetails.click()
        #clicks the view printable view, this should open a new tab
        printableView = WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div[2]/div[2]/div[1]/div/div/div/div/article/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[2]/span/span/a')))
        printableView.click()
        length_of_files_in_download = len(glob.glob(f"{download_path}/*pdf"))

        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.execute_script('window.print();')

        if not type_of_contract:
            path = "System Details.pdf"
        else:
            path = f"{type_of_contract} - System Details.pdf"
        self.driver.execute_script("document.title = \'{}\'".format(path))
        download_quit = 0
        while True:
            length_after_download = len(glob.glob(f"{download_path}/*pdf"))
            if length_after_download == length_of_files_in_download:
                print("Waiting For Download")
                time.sleep(3)
                download_quit += 1
                if download_quit == 100:
                    return None
            else:
                break
        print("executed download script")

        self.driver.close()

        self.driver.switch_to.window(main_window)
        self.driver.back()
        time.sleep(5)

        return path

    def download_lead_details(self, download_path, type_of_contract=None):
        """
        Downloads Lead Details from the System project in the Sunnova Page
        """
        time.sleep(5)

        self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))       #'/html/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-page-card/mat-card/mat-card-content/div/div/dl[2]/dd[4]/app-skeleton-text/a
        LeadDetails = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sunnova-root"]/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail-old/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-page-card/mat-card/mat-card-content/div/div/dl[2]/dd[4]/app-skeleton-text/a')))
        LeadDetails.click()

        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//span[@title='Notes & Attachments']"))).click()
        #find files that we want to download
        contents = []
        sunnova_content_time = []
        sunnova_content_datetime = []
        certificate_content_time = []
        certificate_content_datetime = []
        sunnova_content_index = []
        certificate_content_index = []
        downloaded_files = []
        content_counter = 1
        while True:
            try:                                                                                        
                element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/table/tbody/tr[{content_counter}]/th/span/a/div/div[2]/div/div/span')))
                element = element.text
                element_time = self.driver.find_element(by=By.XPATH, value=f'/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/table/tbody/tr[{content_counter}]/td[3]/span/span').text
                element = element.lower()
                
                if "sunnova" in element:
                    print(element)
                    if "unsigned" in element or "error" in element or "Error" in element:
                        # print("Found an unsigned")
                        content_counter += 1
                        continue
                    print(element_time)
                    sunnova_content_index.append(content_counter)
                    sunnova_content_time.append(element_time)
                    content_counter += 1

                elif "certificate" in element:
                    print(element)
                    if "unsigned" in element or "error" in element or "Error" in element:
                        # print("Found an unsigned")
                        content_counter += 1
                        continue
                    print(element_time)
                    certificate_content_index.append(content_counter)
                    certificate_content_time.append(element_time)
                    content_counter += 1

                else:
                    print(element)
                    content_counter += 1

            except:
                break

        print(f"Sunnova Content, searching for max from: {sunnova_content_time}")
        print(f"Certificate Content, searching for max from: {certificate_content_time}")
        sunnova_content_datetime = self.time_conversion(sunnova_content_time)
        certificate_content_datetime = self.time_conversion(certificate_content_time)

        print(sunnova_content_time)
        print(certificate_content_time)
        latest_sunnova_file = max(sunnova_content_datetime)
        latest_certificate_file = max(certificate_content_datetime)
        contents.append(sunnova_content_index[sunnova_content_datetime.index(latest_sunnova_file)])
        contents.append(certificate_content_index[certificate_content_datetime.index(latest_certificate_file)])
        logger.info(f"Selecting Files with times: {certificate_content_time[certificate_content_datetime.index(latest_certificate_file)]} and {sunnova_content_time[sunnova_content_datetime.index(latest_sunnova_file)]}")
        #download files
        for index, item in enumerate(contents):
            # print(item)
            files = len(glob.glob(f"{download_path}/*pdf"))
            print(files)
            self.driver.find_element(by=By.XPATH, value=f'/html/body/div[3]/div/div/div[2]/div[2]/div/div/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/table/tbody/tr[{item}]/th/span/a/div/div[2]/div/div/span').click()
            download_quit = 0
            while True:
                new_len_file = len(glob.glob(f"{download_path}/*pdf"))
                # file = glob.glob(f"{download_path}/*pdf")
                if files == new_len_file:
                    time.sleep(1)
                    print("Waiting on Download")
                    download_quit += 1
                    if download_quit == 100:
                        return None
                else:
                    # self.driver.quit()
                    print("Download Complete")
                    time.sleep(3)
                    files_in_download_path = glob.glob(f"{download_path}/*pdf")
                    latest_file = max(files_in_download_path, key=os.path.getmtime)
                    print(latest_file)
                    # for file_name in file:
                    if "Certificate" in latest_file:
                        old_name = latest_file
                        try:
                            if not type_of_contract:
                                new_name = os.path.join(download_path, "Agreement DocuCert.pdf")
                            else:
                                new_name = os.path.join(download_path, f"{type_of_contract} - Agreement DocuCert.pdf")
                            os.rename(old_name, new_name)
                        except:
                            new_name = os.path.join(download_path, f"Agreement DocuCert ({new_len_file}).pdf")
                            os.rename(old_name, new_name)
                        print("Renamed File")
                        time.sleep(2)
                        downloaded_files.append(new_name)
                    else:
                        downloaded_files.append(latest_file)
                    break

        self.driver.back()
        time.sleep(3)
        try:
            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))
        except:
            pass
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//span[@title='Notes & Attachments']")))
        except:
            pass
        self.driver.back()
        return downloaded_files
    
    def download_work_order(self, download_path, type_of_contract=None):
        """
        Downloads the first Work Order from a System Project in the Sunnova Page
        """
        time.sleep(10)
        try:
            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))
        except:
            pass
        latest_file = ""
        #START DOWNLOADING WORK ORDER
        try:
            note_and_attachment_counter = 1 #the basic starting value inside the notes and attachments
            workorders_index = []
            workorder_time = []
            workorder_datetime = []
            while True:
                try:
                    len_file = len(glob.glob(f"{download_path}/*pdf"))      
                    # note_and_attachment_item = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="sunnova-root"]/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail-old/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{note_and_attachment_counter}]/app-note-list-note/div/h3/a')))                                                                                                                                                                                                                                                                                                              #counter
                    note_and_attachment_item = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="sunnova-root"]/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail-old/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{note_and_attachment_counter}]/app-note-list-note/div/h3/a')))
                    # note_and_attachment_item = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'/html/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{note_and_attachment_counter}]/app-note-list-note/div/h3/a')))
                    note_text = note_and_attachment_item.text
                    note_text = note_text.lower()
                    if "work order" in note_text:
                        note_and_attachment_time = self.driver.find_element(by=By.XPATH, value=f'//*[@id="sunnova-root"]/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail-old/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{note_and_attachment_counter}]/app-note-list-note/div/p[1]').text
                        # note_and_attachment_time = self.driver.find_element(by=By.XPATH, value=f'/html/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{note_and_attachment_counter}]/app-note-list-note/div/p[1]').text
                        workorders_index.append(note_and_attachment_counter)
                        workorder_time.append(note_and_attachment_time)
                        print(note_and_attachment_time)
                        note_and_attachment_counter += 1
                    else:
                        note_and_attachment_counter += 1
                except:
                    break
                
            workorder_datetime = self.time_conversion(workorder_time)

            latest_workorder_file = max(workorder_datetime)
            index = workorders_index[workorder_datetime.index(latest_workorder_file)]
            logger.info(f"Selecting Workorder with time: {latest_workorder_file}")

            latest_workorder = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="sunnova-root"]/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail-old/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{index}]/app-note-list-note/div/h3/a')))
            # latest_workorder = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'/html/body/app-root/mat-sidenav-container/mat-sidenav-content/main/app-system-projects-detail/div[2]/div/app-sidenav-layout/div/div[2]/app-system-projects-detail-details/app-system-projects-detail-notes/app-page-card/mat-card/mat-card-content/div/app-note-list/ul/li[{index}]/app-note-list-note/div/h3/a')))
            latest_workorder.click()
            # workOrder1.click()
            time.sleep(2)                                                                      #  '//*[@id="mat-dialog-0"]/app-note-list-note-dialog/div/div[2]/div[1]/p[3]/a'
            downloadButton = WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.LINK_TEXT, 'Download')))
            downloadButton.click()
            while True:
                new_len_file = len(glob.glob(f"{download_path}/*pdf"))
                # file = glob.glob(f"{download_path}/*pdf")
                if len_file == new_len_file:
                    time.sleep(1)
                    print("Waiting on Download")
                else:
                    # self.driver.quit()
                    print("Download Complete")
                    downloaded_files = glob.glob(f"{download_path}/*pdf")
                    latest_file = max(downloaded_files, key=os.path.getctime)
                    if type_of_contract:
                        time.sleep(2)
                        file_name = latest_file.split(download_path)[1]
                        new_name = f"{type_of_contract} - {file_name}"
                        os.rename(latest_file, new_name)
                        latest_file = new_name
                # print(latest_file)
                    break
            close_count = 0
            while True:
                try:
                    # closeButton = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="mat-dialog-{close_count}"]/app-note-list-note-dialog/div/div[3]/button[1]/span')))
                    closeButton = self.driver.find_element(by=By.XPATH, value = f'//*[@id="mat-dialog-{close_count}"]/app-note-list-note-dialog/div/div[3]/button[1]/span')
                    closeButton.click()
                    break
                except:
                    print(f"Appending Close Button Counter - {close_count}")
                    close_count += 1
            # time.sleep(3)
            time.sleep(2)
        except Exception as e:
            print(e)
            # print("Passed 2")
            return None
            # pass
        return latest_file

    def upload_trueup_invoice(self, file_path):
        """
        Takes the ID for trueup invoices and submits the given file
        """
        print("Uploading ")
        self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))
        counter = 1
        checker = 0
        while True:                                                                                                                                                                                  
            if counter == 1:        
                try:                                                  
                    trueup_invoice_text = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-3"]/div/app-data-table/div[1]/div/table/tbody/tr/td[1]/div/a')))
                    trueup_invoice_text = trueup_invoice_text.text
                except Exception as e:
                    counter += 1
                    print("Skipping First test")
                    print(e)
            
            else:
                if checker == 0:
                    counter = 1
                    checker = 10
                trueup_invoice_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-3"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]/div/a')))
                trueup_invoice_text = trueup_invoice_text.text
            print(trueup_invoice_text)
            if "true up invoice" in trueup_invoice_text.lower():
                print(counter)
                print(trueup_invoice_text)
                break
            else:
                print(f"Appending counter.. {counter}")
                counter += 1
        #upload

        try:                                                                                                     #'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[1]/td[5]/app-actions-cell-template/ul/li/input'                                                                                      
            TrueupUpload = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-3"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/app-actions-cell-template/ul/li/input')))
            print("Uploaded Invoice")
            # TrueupUpload.send_keys(file_path)
        except:
           
            print("Invoice already uploaded")
            return False

        TrueupUpload.send_keys(file_path)
        while True:
            try:
                # self.driver.switch_to.parent_frame()
                time.sleep(2)
                print("Sleeping for Upload Time")
                # print("Sleeping for load time")
                WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="mat-dialog-0"]/mat-spinner/svg/circle')))
                break
            except Exception as e:
                print(f"failed to find loader - {e}")
                break
        return True

    def upload_system_invoice(self, file_path):
        # if file_path:
        print("Uploading file...")
        time.sleep(2)
        self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))

        counter = 1
        checker = 0
        while True:                                                                                            
            if counter == 1:
                try:                                                                     
                    system_invoice_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr/td[1]')))
                    system_invoice_text = system_invoice_text.text
                except:
                    counter += 1
                    print("Skipping first check")
                    pass
            else:
                if checker == 0:
                    counter = 1
                    checker = 10
                system_invoice_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]/div/a')))
                system_invoice_text = system_invoice_text.text
            print(system_invoice_text)
            if "Invoice" in system_invoice_text:
                print(counter)
                print(system_invoice_text)
                break
            else:
                print(f"Appending counter.. {counter}")
                counter += 1
    
        try:
            SystemInvoiceUpload = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/app-actions-cell-template/ul/li/input')))
            print("Uploaded Invoice")
        except:
            
            print("Invoice already uploaded")

        SystemInvoiceUpload.send_keys(file_path)
        while True:
            try:
                # self.driver.switch_to.parent_frame()
                time.sleep(2)
                print("Sleeping for Upload Time")
                # print("Sleeping for load time")
                WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="mat-dialog-0"]/mat-spinner/svg/circle')))
                break
            except Exception as e:
                print(f"failed to find loader - {e}")
                break

    def upload_system_design(self, file):
        """
        Finds System Invoice (specific table)
        and uploads given file
        """
        print("Uploading file...")
        time.sleep(2)
        self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))

        counter = 1
        checker = 0
        while True:                                                                                            
            if counter == 1:                                                                     
                system_invoice_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]')))
                system_invoice_text = system_invoice_text.text
            else:
                if checker == 0:
                    counter = 1
                    checker = 10
                system_invoice_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]/div/a')))
                system_invoice_text = system_invoice_text.text
            print(system_invoice_text)
            if "Invoice" in system_invoice_text:
                print(counter)
                print(system_invoice_text)
                break
            else:
                print(f"Appending counter.. {counter}")
                counter += 1
    
        try:
            SystemInvoiceUpload = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/app-actions-cell-template/ul/li/input')))
            print("Uploaded Invoice")
        except:
           
            print("Invoice already uploaded")

        SystemInvoiceUpload.send_keys(file)
        # time.sleep(8)
        while True:
            try:

                print("Sleeping for Upload Time")
                # print("Sleeping for load time")
                WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="mat-dialog-0"]/mat-spinner/svg/circle')))
                break
            except Exception as e:
                print(f"failed to find loader - {e}")
                break

    def upload_commission(self, file):
        """
        Searchs for Commissioning Package (specific table)
        and uploads given file
        -- Some values have Commissioning Package and are not what we are looking for (such as Roof Commissioning Package), add to if statement if found --
        """
        try:
            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))

        except:
            pass
        logger.info("Uploading file to Commission")
        counter = 1
        checker = False
        try:
            commission_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-2"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]'))).text
            print(commission_text)
            if "Commissioning Package" in commission_text:
                if "Roof" in commission_text or "roof" in commission_text:
                    pass
                else:
                    checker = True
            elif not commission_text:
                pass
            elif commission_text == " ":
                pass
            else:
                counter += 1
        except Exception as e:

            pass

        while True:
            if checker == True:
                break
            commission_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-2"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]/div/a'))).text
            print(commission_text)
            if "Commissioning Package" in commission_text:
                if "Roof" in commission_text:
                    print(f"Appending counter.. {counter}")
                    counter += 1
                else:
                    print(counter)
                    print(commission_text)
                    break
            else:
                print(f"Appending counter.. {counter}")
                counter += 1
        
        CommissionUpload = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-2"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/app-actions-cell-template/ul/li/input')))
        CommissionUpload.send_keys(file)
        while True:
            try:
                #//*[@id="uploadfilea0E4W00002F97s1UAB"]
                #//*[@id="uploadfilea0E4W00002F97s4UAB"]
                #//*[@id="uploadfilea0E4W00002F8pCEUAZ"]
                time.sleep(2)
                print("Sleeping for Upload Time")
                # print("Sleeping for load time")
                WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="mat-dialog-0"]/mat-spinner/svg/circle')))
                break
                
            except Exception as e:
                print(f"failed to find loader - {e}")
                break
        logger.info("Finished Uploading to commission")
      
    def upload_final_design(self, file):
        """
        Finds Final Design & Assessment (specific table)
        and uploads given file
        """
        time.sleep(10)
        try:
            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))

        except:
            pass
        logger.info("Uploading to Final Design")
        counter = 1
        while True:
            final_design_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-2"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]/div/a'))).text
            print(final_design_text)
            if "Final Design" in final_design_text:
                print(f"counter is: {counter}")
                print(final_design_text)
                break
            else:
                print(f"appending counter.. {counter}")
                counter += 1                                                                                        
        FinalDesign = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-2"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/app-actions-cell-template/ul/li/input')))
        FinalDesign.send_keys(file)
        while True:
            try:
                time.sleep(2)
                print("Sleeping for Upload Time")
                # print("Sleeping for load time")
                WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="mat-dialog-0"]/mat-spinner/svg/circle')))
                break
            except Exception as e:
                print(f"failed to find loader - {e}")
                break
        logger.info("Finished Uploading to Final Design")
        
    def upload_ebill(self, file):
        """
        Finds ebill (specific table)
        and uploads given file
        """
        try:
            self.driver.switch_to.frame(self.driver.find_element(by=By.TAG_NAME, value="iframe"))
        except:
            pass

        counter = 1
        checker = False
        while True:
            if counter == 1:   
                try:
                    ebill_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]')))
                    ebill_text = ebill_text.text

                    if "Utility Bill" in ebill_text:
                        checker = True
                        break
                    elif not ebill_text:
                        pass
                    elif ebill_text == " ":
                        pass
                    else:
                        counter += 1
                except:
                    counter += 1
                    if counter == 5:
                        break
            else:
                if checker == True:
                    break
                if checker == False:                                                                             
                    ebill_text = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[1]/div/a')))
                    ebill_text = ebill_text.text
                    print(ebill_text)
                    if "Utility Bill" in ebill_text:
                        print(counter)
                        print(ebill_text)
                        break
                    else:
                        print(f"Appending counter.. {counter}")
                        counter += 1

        try:
            ebillUpload = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-2"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/div/a')))
        except:
             ebillUpload = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="cdk-accordion-child-1"]/div/app-data-table/div[1]/div/table/tbody/tr[{counter}]/td[5]/app-actions-cell-template/ul/li/input')))
        ebillUpload.send_keys(file)
        while True:
            try:
                time.sleep(2)
                WebDriverWait(self.driver, 120).until(EC.invisibility_of_element_located((By.XPATH,'//*[@id="mat-dialog-0"]/mat-spinner/svg/circle')))
                print("Sleeping for Upload Time")
                break
            except Exception as e:
                print(f"failed to find loader - {e}")
                break
                
    # CREDIT

    def check_credit(self, contract):
        """Opens the lead in sunnova and checks credit for all contacts."""
        try:
            self.get_new_lead(contract)
            self._get_lead_page(CREDIT_URL_SUFFIX)
            credit_status = self._check_credit_current_page()
            self.close()
            return credit_status
        except:
            self.close()
            return None

    def _check_credit_current_page(self):
        """Checks the current page's credit statues."""
        self.grab_iframe()
        credit_statuses = []
        # Get list of creditees
        credit_box = self.driver.find_elements_by_class_name(
            'mat-form-field-wrapper')[0]
        credit_box.click()
        credit_options = self.driver.find_elements_by_class_name(
            'mat-option-text')
        option_count = len(credit_options)
        credit_options[0].click()
        time.sleep(1)
        # Get status for each creditee
        for i in range(option_count):
            try:
                logger.info(f'Checking option {str(i)}...')
                credit_box = self.driver.find_elements_by_class_name(
                    'mat-form-field-wrapper')[0]
                credit_box.click()
                credit_options = self.driver.find_elements_by_class_name(
                    'mat-option-text')[i]
                credit_options.click()
                time.sleep(2)
                info_lines = self.driver.find_elements_by_class_name(
                    'detail-value')
                credit_status = info_lines[CREDIT_STATUS].text
                credit_statuses.append(credit_status.lower())
            except Exception as e:
                logger.error(e)
        # Check status for each creditee
        failed_count = 0
        not_run_count = 0
        logger.info(f'Credit statuses: {credit_statuses}')
        for status in credit_statuses:
            if 'fail' in status:
                failed_count += 1
            if 'not run' in status:
                not_run_count += 1
        # Check for pass
        if failed_count >= option_count:
            logger.info('All failed credit...')
            return 'failed'
        elif not_run_count >= option_count:
            return 'not_run'
        else:
            logger.info('Credit passed...')
            return 'passed'

    # TITLE VERIFICATION

    def verify_title(self, contract):
        """Verifies the title for a given contract."""
        try:
            self.reinit_drivers()
            self.get_new_lead(contract)
            self._get_lead_page(TITLE_URL_SUFFIX)
            verification_status = self._verify_title_current_page()
            self.close()
            return verification_status
        except:
            self.close()

    def check_credit_and_verify_title(self, contract):
        """Verifies title then checks credit. Returns credit check value."""
        logger.info('Checking Sunnova credit and title...')
        try:
            self.reinit_drivers()
            self.get_new_lead(contract)
            self._get_lead_page(TITLE_URL_SUFFIX)
            # Verify title
            title_verified = self._verify_title_current_page()
            time.sleep(3)
            # Check credit
            self._get_lead_page(CREDIT_URL_SUFFIX)
            time.sleep(5)
            credit_status = self._check_credit_current_page()
            if credit_status == 'failed' or credit_status == 'not_run':
                credit_passed = False
            else:
                credit_passed = True

            if not credit_passed and not title_verified:
                create_task(contract.opportunity_id, 'Contract Creation: Unable to Verify Title/Credit',
                            f'Credit checks {credit_status} for contacts. Unable to verify title.')
            elif not credit_passed:
                create_task(contract.opportunity_id, 'Contract Creation: Unable to Verify Credit',
                            f'Credit checks {credit_status} for contacts.')
            elif not title_verified:
                create_task(contract.opportunity_id,
                            'Contract Creation: Unable to Verify Title', 'Unable to verify title.')
            self.close()
            return True
        except Exception as e:
            logger.error(e)
            self.close()

    def _verify_title_current_page(self):
        self.grab_iframe()
        try:
            # Verify Title
            title_check_elem = self.driver.find_element_by_xpath(
                '//span[contains(text(), "Run Title Check")]')
            self.driver.execute_script(
                "arguments[0].click();", title_check_elem)
            time.sleep(5)
        except:
            verification = self.driver.find_elements_by_xpath(
                '//div[contains(text(), "is successfully verified")]')
            if verification:
                logger.info('Title already verified')
            else:
                logger.info('Error in verification')
        try:
            # Verify Contact on Title
            title_info = self.driver.find_elements_by_class_name(
                'title-info')[0]
            title_names = title_info.find_elements_by_class_name(
                'detail-value')[1].text.lower()
            logger.info(f'Found title names: {title_names}')
            contact_elems = self.driver.find_elements_by_class_name(
                'mat-radio-label-content')
            contacts = [elem.text.lower() for elem in contact_elems]
            logger.info(f'Found contacts {contacts}')
            contact_index = self._find_contact_in_title(contacts, title_names)
            if contact_index or contact_index == 0:
                user_check_elems = self.driver.find_elements_by_class_name(
                    'mat-radio-container')
                self.driver.execute_script(
                    "arguments[0].click();", user_check_elems[contact_index])
                logger.info('Found contact on title.')
                time.sleep(2)
            else:
                logger.info('Found no contact in title.')
                return False  # No contact found on title
        except:
            logger.info('Unable to verify contact')
            time.sleep(6)
        button_elems = self.driver.find_elements_by_css_selector('button')
        self.driver.execute_script("arguments[0].click();", button_elems[-1])
        time.sleep(5)
        return True

    def _find_contact_in_title(self, contacts, title_names):
        for index, contact in enumerate(contacts):
            found = True
            split_parts = contact.split(' ')
            for part in split_parts:
                logger.info(f'Checking {part} in title names...')
                if part not in title_names:
                    logger.info(f'{part} not found in title names...')
                    found = False
            if found:
                return index
        return None

    # SYSTEM DESIGNS

    def create_system_design(self, system_design, contract):
        """Creates a new system design for the given contract and system blueprint."""
        try:
            self.reinit_drivers()
            self.get_new_lead(contract)
            self._get_lead_page(SYSTEM_URL_SUFFIX)
            system_design_name = self._create_system_design_current_page(
                system_design)
            self.close()
            return system_design_name
        except:
            self.close()

    def _create_system_design_current_page(self, system_design):
        wait = WebDriverWait(self.driver, 10)
        try:
            self.grab_iframe()
            try:
                create_design_elem = wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                                                '//span[text()="Create System Design"]')))
                create_design_elem.click()
            except:
                pass  # Initial system design so button does not appear.
            logger.info('Creating new design...')
            # Enphase vs. SolarEdge
            total_modules = sum(
                [roof.moduleQuantity for roof in system_design.roofs])
            if total_modules < 8:
                enphase = True
                inverter_and_monitor_manufacturer = "Enphase"
                monitor_model_name = r"ENV-IQ-AMI-240 / CELLMODEM-02 M (4G)"
            else:
                enphase = False
                inverter_and_monitor_manufacturer = "SolarEdge"
                monitor_model_name = "SE-MTR240-0-000-S2 (3G)"
            # Module
            time.sleep(1)
            module_manufacturer = system_design.moduleType.split(
                '-')[0].rstrip()
            self.select_module_manufacturer(module_manufacturer)
            time.sleep(1)
            size_search = re.search("\d\d\d", system_design.moduleType)
            module_size = size_search.group()
            self.select_module_model(module_manufacturer, module_size)
            self.select_module_quantity(system_design.roofs[0].moduleQuantity)
            time.sleep(1)
            # Inverter
            self.select_inverter_manufacturer(
                inverter_and_monitor_manufacturer)
            time.sleep(1)
            if enphase:
                self.select_inverter_model(
                    r"IQ7-60-2-US (Microinverter, 60-Cell)")
                self.select_inverter_quantity(total_modules)
            else:
                self.select_inverter_model(
                    system_design.inverters[0].productCode)
                self.select_inverter_quantity(system_design.inverters[0].count)
            # Racking
            self.select_racking()
            # Monitor
            time.sleep(1)
            self.select_monitor_manufacturer(inverter_and_monitor_manufacturer)
            self.select_monitor_model(monitor_model_name)
            # Other
            time.sleep(1)
            if not enphase:
                logger.info('Adding optimizer...')
                self.select_other()
            # Shade Study
            self.select_tilt(system_design.roofs[0].tilt)
            self.select_azimuth(system_design.roofs[0].azimuth)
            self.select_solar_availability(system_design.roofs[0].availability)
            # Additional Arrays
            if not isinstance(system_design.inverters, str):
                logger.info('inside additonal arrays')
                logger.info(system_design.inverters)
                self.add_additional_arrays(system_design, enphase)
            # Submit
            self.driver.find_element_by_xpath(
                '//span[text()=" Save & Continue "]').click()
            # get system generation name
            quote_elem = self.driver.find_element_by_class_name(
                'blue-highlighted-tile')
            paragraphs = quote_elem.find_elements_by_css_selector('p')
            name_paragraph = paragraphs[0]
            system_design_name = name_paragraph.text
            logger.info(f'System design {system_design_name} created...')
            time.sleep(2)
            return system_design_name
        except Exception as e:
            logger.error(e)
            self.close()
            return None

    def select_module_manufacturer(self, module_manufacturer):
        """Selects the given module manufacturer on the current page."""
        input_elem = self.get_module_manufacturer_element()
        time.sleep(1)
        self.click_element(input_elem)
        module_manufacturer_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), '{module_manufacturer}')]")))
        time.sleep(1)
        module_manufacturer_elem.click()

    def get_module_manufacturer_element(self):
        """Finds the module manufacturer page element."""
        wait = WebDriverWait(self.driver, 20)
        text_based_elems = None
        try:
            text_based_elems = wait.until(
                EC.presence_of_all_elements_located((By.XPATH,
                                                     '//mat-label[contains(text(), "Module Manufacturer")]')))
        except TimeoutException:
            pass
        if text_based_elems:
            return text_based_elems[0]
        id_based_elem = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                                        'mat-select-0')))
        if id_based_elem:
            return id_based_elem

    def select_module_model(self, module_manufacturer, module_size):
        """Selects the given module model on the current page."""
        module_model_elem = self.get_module_model_element()
        self.click_element(module_model_elem)
        # Special Cases
        if module_manufacturer == 'Hanwha' and module_size == '340':
            logger.info('Selecting specific hanwha module + variation...')
            module_model_query = 'Q.PEAK DUO BLK-G6+ 340'
        else:
            module_model_query = module_size
        module_model_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), '"+module_model_query+"')]")))
        module_model_elem.click()

    def get_module_model_element(self):
        """Finds the module model page element."""
        text_based_elems = self.driver.find_elements_by_xpath(
            '//mat-label[contains(text(), "Module Model")]')
        if text_based_elems:
            return text_based_elems[0]
        class_based_elems = self.driver.find_elements_by_class_name(
            'mat-form-field-flex')
        if class_based_elems:
            return class_based_elems[MODULE_MODEL]

    def select_module_quantity(self, module_quantity):
        """Inputs the module quantity."""
        module_quanitity_elem = self.get_module_quantity_element()
        self.overwrite_text_box(module_quanitity_elem, module_quantity)

    def get_module_quantity_element(self):
        """Finds the module quantity input element on the current page."""
        form_based_elem = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Module_Quantity__c"]')
        if form_based_elem:
            return form_based_elem[0]
        input_elems = self.driver.find_elements_by_css_selector('input')
        if input_elems:
            MODULE_QUANTITY_INPUT_INDEX = 1
            return input_elems[MODULE_QUANTITY_INPUT_INDEX]

    def select_inverter_manufacturer(self, inverter_manufacturer):
        """Selects the given inverter manufacturer on the current page."""
        input_elem = self.get_inverter_manufacturer_element()
        self.click_element(input_elem)
        inverter_manufacturer_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), '{inverter_manufacturer}')]")))
        inverter_manufacturer_elem.click()

    def get_inverter_manufacturer_element(self):
        """Finds the inverter manufacturer page element."""
        class_based_elems = self.driver.find_elements_by_css_selector(
            'mat-select[formcontrolname="Inverter_Manufacturer_Lookup__c"]')
        if class_based_elems:
            return class_based_elems[0]
        text_based_elems = self.driver.find_elements_by_xpath(
            '//mat-label[contains(text(), "Inverter Manufacturer")]')
        if text_based_elems:
            return text_based_elems[0]

    def select_inverter_model(self, inverter_model):
        """Selects the given inverter model on the current page."""
        input_elem = self.get_inverter_model_element()
        self.click_element(input_elem)
        inverter_start = inverter_model[:7]
        inverter_model_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), '{inverter_start}')]")))
        inverter_model_elem.click()

    def get_inverter_model_element(self):
        """Finds the inverter model page element."""
        text_based_elems = self.driver.find_elements_by_xpath(
            '//mat-label[contains(text(), "Inverter Model")]')
        if text_based_elems:
            return text_based_elems[0]
        class_based_elems = self.driver.find_elements_by_css_selector(
            'mat-select[formcontrolname="Inverter_Model_Lookup__c"]')
        if class_based_elems:
            return class_based_elems[0]

    def select_inverter_quantity(self, inverter_quantity):
        """Selects the given inverter quantity on the current page."""
        logger.info(f'Found {inverter_quantity} inverters')
        inverter_quantity_element = self.get_inverter_quantity_element()
        inverter_quantity_element.send_keys(inverter_quantity)

    def get_inverter_quantity_element(self):
        """Finds the inverter quantity page input element."""
        class_based_elements = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Inverter_Quantity__c"]')
        if class_based_elements:
            return class_based_elements[0]
        id_based_elements = self.driver.find_elements_by_id('mat-input-1')
        if id_based_elements:
            return id_based_elements[0]

    def select_racking(self):
        """Selects the racking type for the current page. Currently hardcoded as Unirac."""
        input_elem = self.driver.find_element_by_css_selector(
            'mat-select[formcontrolname="Racking_Manufacturer_Lookup__c"]')
        self.click_element(input_elem)
        racking_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '//span[text()="Unirac"]')))
        racking_elem.click()

    def select_monitor_manufacturer(self, inverter_manufacturer):
        """Selects the monitor manufacturer on the current page based on the inverter manfacturer."""
        if inverter_manufacturer == 'Enphase':
            inverter_manufacturer = 'Enphase Energy'
        input_elem = self.driver.find_element_by_css_selector(
            'mat-select[formcontrolname="Monitor_Manufacturer_Lookup__c"]')
        self.click_element(input_elem)
        manufacturer_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f'//span[text()="{inverter_manufacturer}"]')))
        manufacturer_elem.click()

    def select_monitor_model(self, monitor_model):
        """Selects the monitor model on the current page."""
        input_elem = self.driver.find_element_by_css_selector(
            'mat-select[formcontrolname="Monitor_Model_Lookup__c"]')
        self.click_element(input_elem)
        model_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), '{monitor_model}')]")))
        model_elem.click()

    def select_other(self):
        """Selects the optimizer type for this install.
            Hardcoded to P340."""
        input_elem = self.driver.find_element_by_css_selector(
            'mat-select[formcontrolname="Other_Model_Lookup__c"]')
        self.click_element(input_elem)
        model_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), 'P340-5NM4MRSS (Optimizer)')]")))
        model_elem.click()

    def select_tilt(self, tilt):
        """Inputs the tilt for the initial array on the current page."""
        tilt_elem = self.driver.find_element_by_css_selector(
            'input[formcontrolname="Tilt__c"]')
        tilt_elem.send_keys(str(tilt))

    def select_azimuth(self, azimuth):
        """Inputs the azimuth for the initial array on the current page."""
        azimuth_elem = self.driver.find_element_by_css_selector(
            'input[formcontrolname="Azimuth__c"]')
        azimuth_elem.send_keys(str(azimuth))

    def select_solar_availability(self, solar_availability):
        """Inputs the solar availability for the initial array on the current page."""
        solar_availability_elem = self.driver.find_element_by_css_selector(
            'input[formcontrolname="Shading_Coefficient__c"]')
        solar_availability_elem.send_keys(str(solar_availability))

    def add_additional_arrays(self, system_design, is_enphase=False):
        """Adds each additonal array after the first on the current page."""
        for index, roof in enumerate(system_design.roofs):
            if index != 0:
                logger.info(f'looping through array {index}')
                self._add_extra_system_design_array(
                    roof, index, system_design, is_enphase)

    def _add_extra_system_design_array(self, solar_array, counter, design, is_enphase):
        """Adds another solar array to the design."""
        self.driver.find_element_by_xpath(
            '//span[text()="+ Add Additional Array"]').click()
        self.select_additional_module_quantity(
            solar_array.moduleQuantity, counter)
        if not is_enphase:
            if len(design.inverters) > counter:
                self.add_additional_inverter(
                    design.inverters[counter], counter)
        self.select_additional_tilt(solar_array.tilt, counter)
        self.select_additional_azimuth(solar_array.azimuth, counter)
        self.select_additional_solar_availability(
            solar_array.availability, counter)

    def select_additional_module_quantity(self, quantity, counter):
        module_quantity_elems = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Module_Quantity__c"]')
        module_quantity_elem = module_quantity_elems[counter]
        self.overwrite_text_box(module_quantity_elem, str(quantity))

    def add_additional_inverter(self, inverter, counter):
        logger.info('Adding additional inverter')
        logger.info(inverter)
        logger.info(f'counter: {counter}')
        additional_inverter_elems = self.driver.find_elements_by_xpath(
            '//span[contains(text(), "Add Additional Inverter")]')
        self.driver.execute_script(
            "arguments[0].click();", additional_inverter_elems[counter - 1])
        time.sleep(2)
        # Confirmation popup
        confirm_elem = self.driver.find_element_by_xpath(
            '//span[contains(text(), "Add Inverter")]')
        self.driver.execute_script("arguments[0].click();", confirm_elem)
        # Model
        model_elems = self.driver.find_elements_by_css_selector(
            'mat-select[formcontrolname="Inverter_Model_Lookup__c"]')
        logger.info('Found new inverter model dropdown')
        time.sleep(2)
        model_elems[counter].click()
        inverter_start = inverter.productCode[:7]
        inverter_model_elem = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        f"//span[contains(text(), '{inverter_start}')]")))
        inverter_model_elem.click()
        # Quantity
        quantity_elems = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Inverter_Quantity__c"]')
        self.overwrite_text_box(quantity_elems[counter], str(inverter.count))

    def select_additional_tilt(self, tilt, counter):
        """Inputs the tilt for the given array number."""
        tilt_elems = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Tilt__c"]')
        self.overwrite_text_box(tilt_elems[counter], str(tilt))

    def select_additional_azimuth(self, azimuth, counter):
        """Inputs the azimuth for the given array number."""
        azimuth_elems = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Azimuth__c"]')
        self.overwrite_text_box(azimuth_elems[counter], str(azimuth))

    def select_additional_solar_availability(self, solar_availability, counter):
        """Inputs the solar availability for the given array number."""
        solar_availability_elems = self.driver.find_elements_by_css_selector(
            'input[formcontrolname="Shading_Coefficient__c"]')
        self.overwrite_text_box(
            solar_availability_elems[counter], str(solar_availability))

    # QUOTES

    def generate_quote(self, quote, finalize=False) -> SunnovaResponse:
        """
        Generates a quote for the given contract

            Parameters:
                quote (SunnovaQuote): A sunnova quote with parameters.
                finalize (bool): Whether the quote should be finalized or not.
        """
        try:
            self.reinit_drivers()
            if not self.logged_in():
                logger.info('logger in...')
                self.login()
            if quote.genesisDesign.sunnovaLeadUrl:
                self.driver.get(quote.genesisDesign.sunnovaLeadUrl)
            else:
                self.get_new_lead(quote.genesisDesign.opportunity)
            self._get_lead_page(QUOTE_URL_SUFFIX)
            res = self._generate_quote_current_page(quote, finalize)
            self.close()
            return res
        except Exception as e:
            logger.error(f'Error creating sunnova quote: {e}')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.close()

    def generate_design_and_quote(self, design_task) -> SunnovaResponse:
        """Generates a design and initial quote for a system.
        If given, will also update the usage with the salesforce information."""
        try:
            self.reinit_drivers()
            design_task.genesisDesign.sunnovaQuotes[0].status = "Searching for Lead"
            session.commit()
            if not self.logged_in():
                logger.info('logger in...')
                self.login()
            if design_task.genesisDesign.sunnovaLeadUrl:
                self.driver.get(design_task.genesisDesign.sunnovaLeadUrl)
            else:
                self.get_new_lead(design_task.genesisDesign.opportunity)
            usage = design_task.genesisDesign.opportunity.usage
            if usage:
                design_task.genesisDesign.sunnovaQuotes[0].status = "Submitting Usage"
                session.commit()
                logger.info('Updating usage with salesforce info...')
                self._get_lead_page(USAGE_URL_SUFFIX)
                logger.info(f'Setting design url to {self.driver.current_url}')
                design_task.genesisDesign.sunnovaLeadUrl = self.driver.current_url
                self._set_usage_and_submit_current_page(usage)
            # Get to design page if this isn't the first design
            self.grab_iframe()
            time.sleep(2)
            design_task.genesisDesign.sunnovaQuotes[0].status = "Creating Design"
            session.commit()
            self.driver.find_element_by_css_selector(
                'body').send_keys(Keys.CONTROL + Keys.HOME)
            system_design_name = self._create_system_design_current_page(
                design_task.genesisDesign)
            if not system_design_name:
                return SunnovaResponse("error", error="Unable to create Sunnova Design")
            design_task.sunnovaName = system_design_name
            design_task.completed = True
            design_task.genesisDesign.sunnovaQuotes[0].status = "Creating Quote"
            session.commit()
            time.sleep(3)
            response = self._generate_quote_current_page(
                design_task.genesisDesign.sunnovaQuotes[0])
            if response.error:
                return response
            quote_data = response.data
            design_task.genesisDesign.sunnovaQuotes[0].status = "Completed"
            self.close()
            res = SunnovaResponse("ok", quote_data)
            return res
        except Exception as e:
            design_task.genesisDesign.sunnovaQuotes[0].status = "Error"
            session.commit()
            logger.error(
                f'Uncaught Error in system design and in quote generation: {e}')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.close()
            res = SunnovaResponse("error", error="Error")
            return res

    def _generate_quote_current_page(self, sunnova_quote, finalize=False) -> SunnovaResponse:
        wait = WebDriverWait(self.driver, 20)
        self.grab_iframe()
        time.sleep(4)
        logger.info('Generating quote...')
        # Select system design
        design_name = sunnova_quote.genesisDesign.createDesignTask.sunnovaName
        found_design = False
        mat_cards = self.driver.find_elements_by_css_selector('mat-card')
        for card in mat_cards:
            try:
                system_name_text = card.find_elements_by_css_selector('p')[
                    0].text
                if system_name_text == design_name:
                    card.find_elements_by_css_selector('p')[0].click()
                    found_design = True
            except:
                pass
        if not found_design:
            logger.info(
                f'Could not find system design ({design_name}) in sunnova portal.')
            return SunnovaResponse('error', error='Unable to find system design in portal')
        time.sleep(1)
        if 'Loan' in sunnova_quote.genesisDesign.opportunity.purchaseMethod:
            self._input_loan_quote_info(sunnova_quote)
        else:
            self._input_quote_info(sunnova_quote)
        # Submit
        logger.info('Submitting quote...')
        run_pricing_element = self.driver.find_element_by_xpath(
            '//span[text()=" Run Pricing "]')
        self.driver.execute_script(
            "arguments[0].click();", run_pricing_element)
        # Wait until element with text found
        try:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 '//span[text()="Quote has not been saved and will only remain until session has ended."]')
            ))
        except:
            logger.info('Invalid quote submitted...')
            # Get error message from page
            self.driver.switch_to.default_content()
            error_message_elem = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 '//span[contains(text(), "Generated quote is invalid.")]')
            ))
            logger.info(f'Found error message : {error_message_elem.text}')
            return SunnovaResponse('invalid_quote', error=error_message_elem.text)
        if finalize:
            # Save quote
            time.sleep(3)
            save_quote_button = self.driver.find_element_by_xpath(
                '//span[text()=" Add to Save List "]')
            self.driver.execute_script(
                "arguments[0].click();", save_quote_button)
            cards = wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'main-card')
            ))
            last_card = cards[-1]
            save_button = last_card.find_element_by_css_selector('button')
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", save_button)
            save_button.click()
            time.sleep(1)
            quote_buttons = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//span[text()="Go to Quote"]')
            ))
            sunnova_quote.finalized = True
            self.driver.execute_script(
                "arguments[0].click();", quote_buttons[-1])
            time.sleep(10)
            # Get quote details
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//pv-quote-details')
            ))
            quote_box = self.driver.find_element_by_css_selector(
                'pv-quote-details')
            detail_labels = quote_box.find_elements_by_class_name(
                'detail-label')
            detail_values = quote_box.find_elements_by_class_name(
                'detail-value')
            details = []
            for index, label in enumerate(detail_labels):
                if label:
                    details.append(
                        detail_labels[index].text + detail_values[index].text)
            header_box = self.driver.find_element_by_css_selector(
                'pv-systemdesignsummary-component')
            quote_subtitle = header_box.find_elements_by_class_name(
                'mat-card-header')[0]
            subtitle_labels = quote_subtitle.find_elements_by_class_name(
                'detail-label')
            subtitle_values = quote_subtitle.find_elements_by_class_name(
                'detail-value')
            for index, label in enumerate(subtitle_labels):
                if label:
                    details.append(
                        subtitle_labels[index].text + subtitle_values[index].text)
            logger.info('Got quote details...')
            logger.info(details)
            contract_id = None
            details_joined = ''.join(details)
            try:
                search_pattern = re.compile(r"(\D\D\d{9})")
                match = re.search(search_pattern, details_joined)
                contract_id = match.group(1)
            except:
                logger.info('Error getting contract Id')
            # Add to Customer View
            try:
                self.driver.find_element_by_class_name(
                    "add-to-customer-view-button").click()
                time.sleep(3)
                logger.info('Added to customer view')
            except:
                logger.info('Error adding to customer view')
            # Generate Documents
            generate_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//span[text()=" Generate Proposal "]')
            ))
            time.sleep(5)
            generate_button.click()
            download_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[text()=" Download "]')
            ))
            download_button.click()
            contract_download_not_found = True
            logger.info(f'Searching for download with {contract_id}')
            while contract_download_not_found:
                files = os.listdir(self.download_folder)
                for file in files:
                    if contract_id in file and 'crdownload' not in file:
                        logger.info(f'Found download {file}')
                        contract_download_not_found = False
                time.sleep(3)
        else:
            # Grab quote details
            try:
                quote_box = self.driver.find_element_by_id('QuoteView')
            except:
                error_message_elem = self.driver.find_elements_by_xpath(
                    '//p[contains(text(), "Positive Year")]')
                if error_message_elem:
                    return "No Positive Year One Savings"
            quotes = quote_box.find_elements_by_class_name(
                'quote-card-container')
            new_quote = quotes[0]
            detail_labels = new_quote.find_elements_by_class_name(
                'detail-label')
            detail_values = new_quote.find_elements_by_class_name(
                'detail-value')
            system_size_elem = new_quote.find_element_by_xpath(
                '//p[contains(text(), "System Size: ")]')
            quote_name = new_quote.find_element_by_class_name(
                'word-break-all').text
            details = []
            for index, label in enumerate(detail_labels):
                if label:
                    details.append(
                        detail_labels[index].text + detail_values[index].text)
            details.append(system_size_elem.text)
            logger.info(details)
        return SunnovaResponse('ok', data={'quote_details': details})

    def _input_loan_quote_info(self, sunnova_quote):
        """Inputs the quote info for loan."""
        # Loan flow -> PPA * System Size = Customer Price
        wait = WebDriverWait(self.driver, 20)
        mat_cards = self.driver.find_elements_by_css_selector('mat-card')
        logger.info(len(mat_cards))
        watt_value = None
        for card in mat_cards:
            system_name_text = card.find_elements_by_css_selector('p')[0].text
            if system_name_text == sunnova_quote.genesisDesign.createDesignTask.sunnovaName:
                card_text = card.find_elements_by_css_selector('p')[1].text
                logger.info(card_text)
                kw_substring = card_text.split('System Size: ')[-1]
                size_text = kw_substring.split(' ')[0]
                logger.info(size_text)
                size_float = float(size_text)
                watt_value = size_float * 1000
        price = str(int((watt_value * float(sunnova_quote.rate))))
        # Financing Type
        financing_type = self.get_financing_type(sunnova_quote)
        financing_elem = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//div[text()="{financing_type}"]')
        ))
        financing_elem.click()
        # Purchase Method
        pricing_method = self.get_purchase_method(sunnova_quote)
        pricing_elem = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//div[text()="{pricing_method}"]')
        ))
        pricing_elem.click()
        # Price
        price_elem = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f'input[formcontrolname="price"]')
        ))
        price_elem.send_keys(price)

    def _input_quote_info(self, sunnova_quote):
        financing_type = self.get_financing_type(sunnova_quote)
        logger.info(f'Selecting financing type {financing_type}')
        self.driver.find_element_by_xpath(
            f'//div[contains(text(), "{financing_type}")]').click()
        time.sleep(3)
        purchase_method = self.get_purchase_method(sunnova_quote)
        logger.info(f'Selecting purchase method {purchase_method}')
        self.driver.find_element_by_xpath(
            f'//div[contains(text(), "{purchase_method}")]').click()
        price = self.get_price(sunnova_quote)
        try:
            self.driver.find_element_by_css_selector(
                'input[placeholder="Price"]').send_keys(price)
        except Exception as e:
            logger.error(e)
            self.driver.find_element_by_id('mat-input-1').send_keys(price)
        time.sleep(1)
        escalator_element = self.driver.find_element_by_css_selector(
            'mat-select[placeholder="Escalator"]')
        self.driver.execute_script("arguments[0].click();", escalator_element)
        time.sleep(1)
        if sunnova_quote.escalator:
            escalator = sunnova_quote.escalator
        else:
            escalator = sunnova_quote.genesisDesign.opportunity.escalator
        split_escalator = escalator.split("%")
        sva_formatted_escalator = split_escalator[0] + \
            '0%' + split_escalator[-1]
        escalation_elements = self.driver.find_elements_by_xpath(
            f'//span[contains(text(), "{sva_formatted_escalator}")]')
        self.driver.execute_script(
            "arguments[0].click();", escalation_elements[-1])
        time.sleep(1)

    def download_quote_from_url(self, url) -> SunnovaResponse:
        """
        Downloads the given quote from a url.

            Parameters:
                url (str): A string containing the sunnova portal quote location.
        """
        self.reinit_drivers()
        wait = WebDriverWait(self.driver, 20)
        try:
            if not self.logged_in():
                self.login()
            self.driver.get(url)
            details = self._get_finalize_info_from_page()
            details_joined = ''.join(details)
            try:
                search_pattern = re.compile(r"(\D\D\d{9})")
                match = re.search(search_pattern, details_joined)
                contract_id = match.group(1)
            except:
                logger.info('Error getting contract Id')
                return False
            # Add to Customer View
            try:
                self.driver.find_element_by_class_name(
                    "add-to-customer-view-button").click()
                time.sleep(3)
                logger.info('Added to customer view')
            except:
                logger.info('Error adding to customer view')
            # Generate Documents
            self._wait_for_spinner()
            generate_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//span[text()=" Generate Proposal "]')
            ))
            time.sleep(5)
            generate_button.click()
            download_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[text()=" Download "]')
            ))
            download_button.click()
            contract_download_not_found = True
            logger.info(f'Searching for download with {contract_id}')
            while contract_download_not_found:
                files = os.listdir(self.download_folder)
                for file in files:
                    if contract_id in file and 'crdownload' not in file:
                        logger.info(f'Found download {file}')
                        contract_download_not_found = False
                time.sleep(3)
            self.close()
            return SunnovaResponse('ok', {"details": details})
        except Exception as e:
            logger.error(e)
            self.close()

    def _get_finalize_info_from_page(self):
        time.sleep(10)
        self.grab_iframe()
        detail_labels = self.driver.find_elements_by_class_name('detail-label')
        detail_values = self.driver.find_elements_by_class_name('detail-value')
        details = []
        for index, label in enumerate(detail_labels):
            if label:
                details.append(
                    detail_labels[index].text + detail_values[index].text)
        logger.info(f'Found first half of details:')
        logger.info(details)
        header_box = self.driver.find_element_by_css_selector(
            'pv-systemdesignsummary-component')
        quote_subtitle = header_box.find_elements_by_class_name(
            'mat-card-header')[0]
        subtitle_labels = quote_subtitle.find_elements_by_class_name(
            'detail-label')
        subtitle_values = quote_subtitle.find_elements_by_class_name(
            'detail-value')
        for index, label in enumerate(subtitle_labels):
            if label:
                details.append(
                    subtitle_labels[index].text + subtitle_values[index].text)
        logger.info('Got finalized quote details...')
        logger.info(details)
        return details

    def get_financing_type(self, sunnova_quote):
        if sunnova_quote.financingType:
            sf_method = sunnova_quote.financingType
        else:
            sunnova_quote.financingType = sunnova_quote.genesisDesign.opportunity.purchaseMethod
            sf_method = sunnova_quote.genesisDesign.opportunity.purchaseMethod
        if "Loan" in sf_method:
            return " Loan "
        elif "Lease" in sf_method:
            return " Lease "
        elif "EZ" in sf_method:
            return "PPA-EZ"
        else:
            return " PPA "

    def get_purchase_method(self, sunnova_quote):
        if sunnova_quote.financingType:
            sf_method = sunnova_quote.financingType
        else:
            sf_method = sunnova_quote.genesisDesign.opportunity.purchaseMethod
        if "Loan" in sf_method:
            sunnova_quote.purchaseMethod = 'Customer Price'
            return ' Customer Price '
        elif not sunnova_quote.purchaseMethod:
            sunnova_quote.purchaseMethod = 'Solar Rate'
            return 'Solar Rate'
        else:
            return sunnova_quote.purchaseMethod

    def get_price(self, sunnova_quote):
        if sunnova_quote.price:
            price = sunnova_quote.price
        else:
            price = sunnova_quote.genesisDesign.opportunity.price
        str_price = str(price)
        # PPW
        if sunnova_quote.purchaseMethod == "Dealer EPC Per Watt":
            return str_price[:-2] + "." + str_price[-2:]
        else:
            return str_price[:-3] + "." + str_price[-3:]

    # USAGE

    def _set_usage_and_submit_current_page(self, usage):
        self.grab_iframe()
        wait = WebDriverWait(self.driver, 20)
        try:
            # Annual Usage
            usage_elem = wait.until(EC.element_to_be_clickable(
                (By.ID, 'mat-input-0')
            ))
            self.overwrite_text_box(usage_elem, str(usage))
            time.sleep(2)
            # Save and Continue
            continue_elem = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Save & Continue')]")
            ))
            self.driver.execute_script("arguments[0].click();", continue_elem)
            logger.info('Submitted new usage...')
            return True
        except:
            return False

    def set_electric_bill(self, contract, electric_bill):
        """Sets electric bill info from an Electricbill object. Closes driver."""
        # Escalation default is the highest
        try:
            self.reinit_drivers()
            if not self.get_new_lead(contract):
                self.close()
                return False
            self._get_lead_page(USAGE_URL_SUFFIX)
            time.sleep(8)
            # Utility
            logger.info(electric_bill.get_utility())
            self.driver.find_element_by_id('mat-select-0').click()
            time.sleep(2)
            utility_elem = self.driver.find_element_by_xpath(
                '//span[contains(text(), "' + electric_bill.get_utility() + '")]')
            utility_elem.click()
            time.sleep(2)
            # Current Rate Plan
            logger.info(electric_bill.get_rate())
            self.driver.find_element_by_id('mat-select-1').click()
            time.sleep(3)
            rate_elem = self.driver.find_element_by_xpath(
                f'//span[contains(text(),"{electric_bill.get_rate()}")]')
            self.driver.execute_script("arguments[0].click();", rate_elem)
            time.sleep(3)
            # Proposed Rate Plan
            self.driver.find_element_by_id('mat-select-3').click()
            time.sleep(3)
            proposed_rate_elems = self.driver.find_elements_by_xpath(
                f'//span[contains(text(),"{electric_bill.get_proposed_rate()}")]')
            self.driver.execute_script(
                "arguments[0].click();", proposed_rate_elems[1])
            time.sleep(3)
            # Utility Escalation
            self.driver.find_element_by_id('mat-select-4').click()
            time.sleep(3)
            escalation_elems = self.driver.find_elements_by_xpath(
                "//span[contains(text(), '%')]")
            self.driver.execute_script(
                "arguments[0].click();", escalation_elems[-1])
            time.sleep(2)
            # Annual Usage
            usage_elem = self.driver.find_element_by_id('mat-input-0')
            self.overwrite_text_box(
                usage_elem, electric_bill.get_yearly_usage())
            # Save and Continue
            continue_elem = self.driver.find_element_by_xpath(
                "//span[contains(text(), 'Save & Continue')]")
            self.driver.execute_script("arguments[0].click();", continue_elem)
            time.sleep(8)
            self.close()
            return True
        except Exception as e:
            logger.error(f'Failed to input sunnova utility info: {e}')
            self.close()
            return False

    def set_usage(self, contract):
        """Sets usage from salesforce. Rate is defaulted to residential. Closes driver."""
        # Escalation default is the highest
        try:
            self.reinit_drivers()
            if not self.get_new_lead(contract):
                self.close()
                return False
            self._get_lead_page(USAGE_URL_SUFFIX)
            time.sleep(8)
            # Utility
            logger.info(contract.get_utility())
            try:
                self.driver.find_element_by_id('mat-select-0').click()
                time.sleep(2)
                utility_elem = self.driver.find_element_by_xpath(
                    '//span[contains(text(), "' + contract.get_utility() + '")]')
                utility_elem.click()
                time.sleep(2)
            except:
                logger.info('Static Utility')
            # Current Rate Plan
            logger.info('Residential')
            self.driver.find_element_by_id('mat-select-1').click()
            time.sleep(3)
            rate_elem = self.driver.find_element_by_xpath(
                f'//span[text()=" Residential"]')
            self.driver.execute_script("arguments[0].click();", rate_elem)
            time.sleep(3)
            # Proposed Rate Plan
            self.driver.find_element_by_id('mat-select-3').click()
            time.sleep(3)
            proposed_rate_elem = self.driver.find_element_by_xpath(
                f'//span[text()="Residential"]')
            self.driver.execute_script(
                "arguments[0].click();", proposed_rate_elem)
            time.sleep(3)
            # Utility Escalation
            self.driver.find_element_by_id('mat-select-4').click()
            time.sleep(3)
            escalation_elems = self.driver.find_elements_by_class_name(
                "mat-option-text")
            self.driver.execute_script(
                "arguments[0].click();", escalation_elems[-1])
            time.sleep(2)
            # Annual Usage
            usage_elem = self.driver.find_element_by_id('mat-input-0')
            self.overwrite_text_box(usage_elem, str(contract.usage))
            # Save and Continue
            continue_elem = self.driver.find_element_by_xpath(
                "//span[contains(text(), 'Save & Continue')]")
            self.driver.execute_script("arguments[0].click();", continue_elem)
            time.sleep(8)
            self.close()
            return True
        except Exception as e:
            logger.error(f'Failed to input sunnova utility info: {e}')
            self.close()
            return False

    # CONTRACTS

    def generate_contract(self, contract, search_query):
        try:
            self.reinit_drivers()
            self.get_new_lead(contract)
            self._get_lead_page(QUOTE_URL_SUFFIX)
            contract_details = self._generate_contract_current_page(contract)
            self.close()
            return contract_details
        except Exception as e:
            logger.error(e)
            self.close()
            return None

    def _generate_contract_current_page(self, contract):
        res = self._generate_quote_current_page(contract, finalize=True)
        return res.data

    # NAVIGATION

    def search_sunnova_portal(self, opportunity):
        """Searches the sunnova portal leads for a given query. Uses backup query if first query is not found."""
        search_query = opportunity.opportunityEmail
        second_query = opportunity.streetAddress
        third_query = opportunity.primaryContactLastName
        identifier = opportunity.lastName

        logger.info(opportunity.salesperson)
        if self.driver.current_url != self.open_leads_url:
            self.driver.get(self.open_leads_url)
        logger.info(f'Searching sunnova all open leads for {search_query}...')
        time.sleep(5)
        self.grab_iframe()
        all_leads_link = self.driver.find_element_by_xpath(
            '//a[text()="All Leads"]')
        all_leads_link.click()
        time.sleep(3)
        input_elem = self.driver.find_element_by_id('mat-input-0')
        input_elem.send_keys(search_query)
        input_elem.send_keys(Keys.ENTER)
        time.sleep(3)
        found_lead = self.search_for_lead(search_query, identifier)
        if found_lead: 
            return True

        if second_query:
            found_lead = self.search_for_lead(second_query, identifier)
            if found_lead: 
                return True

        if third_query:
            found_lead = self.search_for_lead(third_query, identifier)
            if found_lead: 
                return True
        return False


    def search_for_lead(self, query, identifier):
        """
        Searches the current lead page for a query, checks against an identifier string.
        If it finds the leads, opens it and return True.
        """
        logger.info(f'Searching leads using query: {query}')
        input_elem = self.driver.find_element_by_id('mat-input-0')
        self.overwrite_text_box(input_elem, query)
        input_elem.send_keys(Keys.ENTER)
        time.sleep(3)
        try:
            table_body = self.driver.find_element_by_css_selector('tbody')
            table_rows = table_body.find_elements_by_css_selector('tr')
            for row in table_rows:
                table_cols = row.find_elements_by_css_selector('td')
                lead_page_elem = table_cols[0].find_element_by_css_selector(
                    'a')
                sva_customer_name = lead_page_elem.text
                if identifier.lower() in sva_customer_name.lower():
                    logger.info(
                        f'Matched identifier {identifier} to {sva_customer_name}')
                    lead_page_elem.click()
                    logger.info('Clicked first result')
                    self.driver.switch_to.default_content()
                    logger.info(f'Found page for {query}...')
                    return True
            logger.info(
                f'Could not find lead with identifier {identifier}...')
            return False
        except:
            return False


    def logged_in(self):
        self.driver.get(self.home_url)
        time.sleep(3)
        if self.driver.current_url != self.home_url:
            logger.info('Not logged in...')
            return False
        else:
            logger.info('Currently logged in...')
            return True

    def login(self):
        if "login" not in self.driver.current_url:
            self.driver.get(self.login_url)
        time.sleep(3)
        logger.info('logger in...')
        self.driver.find_element_by_id('username').send_keys(SUNNOVA_USERNAME)
        self.driver.find_element_by_id('password').send_keys(SUNNOVA_PASSWORD)
        self.driver.find_element_by_id('Login').click()
        time.sleep(1)
        if r"https://sunnova.my.site.com/partnerconnect/apex/TwoFactorAuthLogin" in self.driver.current_url:
            email_validation_button = self.driver.find_element_by_css_selector(
                'button[onclick="sendOtpEmail();return false;"]')
            logger.info('found 2fa')
            email_validation_button.click()
            self.driver.find_element_by_class_name(
                'slds-checkbox__label').click()
            while True:
                time.sleep(10)
                code = self.outlook.get_sunnova_verification_code()
                if code:
                    try:
                        code_entry = self.driver.find_element_by_id(
                            'verification_code')
                    except:
                        logger.info('Finished 2fa')
                        break
                    code_entry.send_keys(code)
                    code_entry.send_keys(Keys.ENTER)
        else:
            logger.info('no 2fa')
        time.sleep(3)

    # HELPERS

    def get_new_lead(self, opportunity):
        """Opens requested lead from a contract. Restarts drivers."""
        try:
            if not self.logged_in():
                logger.info('logger in...')
                self.login()
            self.driver.get(self.open_leads_url)
            if not self.search_sunnova_portal(opportunity):
                logger.info(
                    'Could not find this sunnova lead, creating task...')
                create_task(opportunity.salesforceId, 'Contract Creation: Sunnova Lead Issue',
                            'Could not find lead in sunnova portal.')
                self.close()
                return False
            logger.info(f'Found new lead for: {opportunity.lastName}')
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(
                f'Encountered an error caught from sva portal login and go to page: {e}')
            self.close()
            return False

    def grab_iframe(self):
        try:
            iframe = self.driver.find_element_by_css_selector(
                'iframe[class="app"]')
            self.driver.switch_to.frame(iframe)
        except:
            pass

    def close(self):
        try:
            self.driver.close()
        except:
            logger.info('driver already closed')

    def overwrite_text_box(self, element, string):
        """Replaces text inside an input element with the given string."""
        element.send_keys(Keys.CONTROL, 'a')
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(string)

    def _get_lead_page(self, page):
        # Links don't work reliably so url manipulation is used
        self._wait_for_spinner()
        time.sleep(5)
        logger.info('Lead page loaded...')
        current_url = self.driver.current_url
        split_url = current_url.split(r'/')
        suffix = split_url[-1]
        if suffix == page:
            return
        split_url[-1] = page
        new_url = r'/'.join(split_url)
        logger.info(f'Switching to lead url: {new_url}')
        self.driver.switch_to.default_content()
        self.driver.get(new_url)
        # Refresh is used because sunnova portal does not allow gets for some reason
        self.driver.refresh()
        self._wait_for_spinner()

    def _wait_for_spinner(self):
        """Waits for the current pages spinner to not be clickable to prevent early clicks."""
        self.grab_iframe()
        time.sleep(1)
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "h1")))
        logger.info('spinner wait')
        WebDriverWait(self.driver, 15).until_not(
            EC.element_to_be_clickable((By.CLASS_NAME, "spinner")))
        logger.info('spinner passed')
        time.sleep(3)

    def click_element(self, element):
        """Clicks an html element using JS function."""
        self.driver.execute_script("arguments[0].click();", element)


if __name__ == '__main__':
    pass

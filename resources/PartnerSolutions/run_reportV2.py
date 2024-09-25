import sys
from inspect import getargs
import time
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import sys
# sys.path.append()
import requests
import json
import pandas as pd
from datetime import datetime
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(CURRENT_DIR))
sys.path.append(os.environ['autobot_modules'])
# sys.path.append(os.environ['autobot_resources'])

from Sunnova.SunnovaPortal import SunnovaPortal
from Sunnova.SunnovaAPI import SunnovaAPI
from customlogging import logger
# from Outlook import outlook
from customlogging.loggerV2 import SunnovaLogger
from SunnovaEmail import SunnovaEmail
from Box.BoxAPI import BoxAPI
import re
import glob 
import csv
from PyPDF2 import PdfMerger
# from BotUpdate.Update import update_bot_status
#from SalesforceAPI.SFReportToDF import 
from SalesforceAPI import SalesforceAPI
from BotUpdate.ProcessTable import RPA_Process_Table
from AutobotEmail.Outlook import Outlook
# from config import JEFF_SALESFORCE_PASSWORD, JEFF_SALESFORCE_USERNAME


# JEFF_ACCOUNT_ID = r'ea418f30-8802-4378-bb92-e9b48b1c3b02'

PA_ACCOUNT_ID = r'19889a32-5ffd-4343-853c-044e8f02af7e'

FOLDER_ID_URL = 'https://prod-13.westus.logic.azure.com:443/workflows/d0164c8f02f44f7ba45bba2cf0d085e3/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=X1hfjkztxSiOZpSHxzBU17R_aQYrmWN6X7kzy7O5mzQ'

class SunnovaReports(): 
    def __init__(self):
        #variable for pandas
        self.headers = {
            'UserKey': "2ac1a41a-a2e1-4caf-af1c-2aaf4244e2cf",
            'accept': "application/json"
        }
        #basic variables, not in use
        self.username = None
        self.counter = None
        self.download_path = None
        #init sunnova portal and box api calls
        self.sunnova = SunnovaPortal()
        self.sunnova_api = SunnovaAPI()
        self.salesforce = SalesforceAPI()
        #init sql server for bot updates
        self.bot_update = RPA_Process_Table()
        #upload pdfs will be the variable storing current pdf's that we are uploading to either box or sunnova
        self.upload_pdfs = []
        #downloaded files is a variable storing any pdf that we download to send to upload later
        self.downloaded_files = []
        #argument contains information about which config we will pull from
        self.argument = False
        self.file = ""
        #create a basic variable for when the code kicks off the run, not really used
        self.today = datetime.today()
        # print(self.today)
        # quit()
        self.daily_runs_date = str(self.today)
        self.daily_runs_date = self.daily_runs_date.split(" ")[0]
        self.total_upload_true = 0
        self.total_upload_false = 0
        # print(self.today)
        # quit()
        #basic list to contain every comment through a single process, gets reset per opportunity
        self.comments = []
        #log list contains every aspect of logs that we record (basic true or false uploads) and full opportunity information, to send as an email (this also contains manual intervention false uploads) 
        self.log_list = []
        #manual intervention will send separetly as a report containing processes we could not upload
        self.manual_intervention = []

        #basic arguments that are allowed, these are stored in the config file
        arguments = [
            "Commission_And_Final_Design",
            "Contract_Document_Download",
            # "Invoice_Upload",
            "Ebill_Upload",
            "System_Invoice",
            "Trueup_Invoice",
            "Invoices",
            "Test"
        ]
        try:
            argument = sys.argv[1] #run_report.py argument
        except:
            print(f"BAD REQUEST! Please include one of these options in the arguments - {arguments}")
            quit()
        for counter, arg in enumerate(arguments):
            if argument == arg:
                print(arg)
                print(counter)
                self.argument = arg
                self.counter = counter
                self.function = self.argument
                self.name = f"bot_{self.argument}"
                self.box = BoxAPI(application=self.argument)

        if not self.argument:
            print(f"BAD REQUEST! Please include one of these options in the arguments - {arguments}")
            quit()

        if self.argument == "Test":
            print("Running Test Environment")
            return
        CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
        CONFIG_PATH = '\\'.join([CONFIG_PATH, 'process_definition.json'])        
        with open(CONFIG_PATH) as config_file:
            config = json.load(config_file)
            # salesforce_config = config['salesforce']
            #most important variable, contains the full config information of the process we are running
            self.full_config = config[self.argument]
        #init salesforce information
        # self.salesforce_password = JEFF_SALESFORCE_PASSWORD
        # self.salesforce_username = JEFF_SALESFORCE_USERNAME
        try:
            self.download_path = self.full_config['download_path']
        except:
            print("Could not find download path in config - set to None")
            self.download_path = None
        #basic pref information for chromedriver, allows for better downloads and a specific path to send files (from config)
        #settings is to download pdf from chromedriver's window.print() script execution
        settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
        }
        self.prefs = {'download.default_directory' : self.download_path,
                "download.prompt_for_download": False, #To auto download the file
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
                #removes the requirement to run a virus scan
                "safebrowsing.disable_download_protection": True,
                'printing.print_preview_sticky_settings.appState': json.dumps(settings),
                #sets download path when executing self.driver.execute_script(window.print();)
                #and saving it to : self.driver.execute_script("document.title = \'{}\'".format(file_name))
                "savefile.default_directory": self.download_path
            }

    def run(self):
        """
        """
        if "Invoice" in self.argument:
            paths = self.full_config["paths"]
            folder_paths = paths[0]
            # print(folder_paths)
            self.invoice_queue(folder_paths=folder_paths)

        else:
            # try:
            #     self.bot_update.register_bot(self.name)
            # except:
            #     pass
            self.bot_update.register_bot(self.name)
            
            self.bot_update.update_status(self.name)
            #init dataframe will run the salesforce download and exports, we will store every bit of informaton we need, sunnova id's, opportunity id's, names, addresses 
            ids, op_id, names, addresses = self.init_dataframe(self.full_config['salesforce_url'])
            self.log_location = self.full_config['log_location']
            queue = len(ids)
            if queue == 0:
                self.interpret_logs()
                return None
            try:
                # self.bot_update.register_bot(self.name, logs=f"In Queue: {queue}")
                self.bot_update.update_logs(f"In Queue: {queue}")
            except Exception as e:
                print(e)
            #from the config, signifies what value from the dataframe we will use to search through sunnova
            search_with = self.full_config['search_with']
            print(f"Selected Search with Criteria - {search_with}")
            self.bot_update.update_status(self.name)


            #init log location from config, this will be where we store a notepad containing every file that we uploaded
            # self.log_location = self.full_config['log_location']
            #determines where the source location is, from config
            source_location = self.full_config['source_location']
            print("picked Source")
            if source_location == "Box":
                #starts webdriver and logs into the sunnova portal, this will stay open through the entire process until finish
                #self.sunnova.reinit_drivers(self.prefs)
                #self.sunnova.login()
                
                #files are the files we will be downloading from box
                files = self.full_config['files_to_download']
                #we will iterate through each opportunity in the dataframe, storing their opportunity Id as we go along
                for df_counter, opportunity in enumerate(op_id):
                    #if self.name == "bot_Commission_And_Final_Design":
                    already_uploaded = self.bot_update.update_bot_status(self.name, "Starting", ids[df_counter])
                    #else:
                    #    already_uploaded = self.bot_update.update_bot_status(self.name, "Starting", opportunity)

                    if already_uploaded == True:
                        logger.info(f"opportunity has already been uploaded... Passing")
                        continue
                        # pass
                    try:
                        self.comments = []
                        #reinits upload pdfs to clear any data from a previous opportunity that we ran
                        self.upload_pdfs = []
                        #basic print statement to signify the start of a new opportunity
                        print(f"Starting to Process opportunity")

                        logger.info("Downloading Files from Box...")
                        self.comments.append("Downloading Files from Box...")
                        #download from box will download each file we are looking for that is stored in the config, the locations of each file are also found in the config
                        #download complete contains True or False values, this will determine if we reached / downloaded every file from box
                        download_complete = self.download_from_box(opportunity)
                        #if any file was missed, we will report that the bot was inable to run the opportunity, and submit false along with a manual intervention report email
                        if not download_complete:
                            self.bot_update.update_bot_status(self.name, f"Failed to Download all files", ids[df_counter])

                            self.today = datetime.today()
                            log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments)
                            self.manual_intervention.append(log)
                            self.log_list.append(log)
                            print("DOWNLOAD NOT COMPLETE")
                            self.comments.append("DOWNLOAD NOT COMPLETE")
                            #removes any file we downloaded to clear the path for the next set
                            for file in self.upload_pdfs:
                                os.remove(file)
                            # time.sleep(20)
                            continue
                        #if self.name == "bot_Commission_And_Final_Design":
                        self.bot_update.update_bot_status(self.name, f"Finished Downloading From Box for {opportunity}, starting upload", ids[df_counter])
                        #else:
                        #    self.bot_update.update_bot_status(self.name, f"Finished Downloading From Box for {opportunity}, starting upload", opportunity)
                        
                        #once we have all the files, we proceed to upload        
                        logger.info("Starting Sunnova Upload...")
                        #searching with the local variable from the config search with, at df_counter which signifies which opportunity we are working on
                        #self.sunnova.selectSystemProject(locals()[search_with][df_counter])

                        list_uploaded_to_sunnova = []
                        sunnova_id = False
                        #for each destination signified in the upload destination in the config, we will send our pdf to it, based on pdf name and upload destination we will pick where to send the file
                        for file_counter, destination in enumerate(self.full_config['upload_destination']):
                            print(f"Running File Upload")
                            pdf = self.upload_pdfs[file_counter]
                            self.comments.append(f"Running File Upload for {pdf} at destination: {destination}")
                            self.bot_update.update_bot_status(self.name, f"Searching for Sunnova ID", ids[df_counter])

                            #this will get a method from the sunnova portal pertaining to the upload we are trying to run
                            #upload_attribute = getattr(SunnovaPortal, f"upload_{destination}")
                            #upload to sunnova we send the value we are searching with, the pdf we are working with, and the upload attribute (which depends on the file, and counter we are on from the config)
                            #for this function, the search with value is NOT important, however, we use it to print what opportunity we are working on in console
                            #the upload attribute will call a function from the SunnovaPortal
                            if not sunnova_id:
                                print("Finding sunnova ID")
                                sunnova_id = self.sunnova_api.get_sunnova_project_id(locals()[search_with][df_counter])
                                self.bot_update.update_bot_status(self.name, f"Found Sunnova ID", ids[df_counter])

                            print(f"Found sunnova ID")
                            block_id = self.sunnova_api.get_project_block_id(sunnova_id, destination)
                            self.bot_update.update_bot_status(self.name, f"Found Block Id, uploading", ids[df_counter])

                            print(f"found Block ID, attempting upload")
                            uploaded = self.sunnova_api.upload_pdf(block_id, pdf)
                            print(f"upload completed: {uploaded}")
                            #uploaded_to_sunnova = self.upload_to_sunnova(locals()[search_with][df_counter], pdf, upload_attribute)
                            #system_id = self.get_sunnova_id(locals()[search_with][df_counter])
                            #all_ids = self.get_json(system_id)
                            #for item in all_ids:
                                ## print(item['name'])
                            #    if item['name'] == destination:
                            #        upload_id = item['id']
                            #        break
                            #uploaded_to_sunnova = self.upload_to_sunnova(pdf, upload_id)
                            list_uploaded_to_sunnova.append(uploaded)
                            self.comments.append(f"{pdf} was Uploaded: {uploaded}")
                    #if any upload is marked as false, return false
                        sunnova_uploads = False
                        for value in list_uploaded_to_sunnova:
                            if not value:
                                self.bot_update.update_bot_status(self.name, f"Failed to upload all files", ids[df_counter])

                                self.today = datetime.today()
                                log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments)
                                self.log_list.append(log)
                                sunnova_uploads = False
                                break
                            else:
                                self.bot_update.update_bot_status(self.name, f"Uploaded all files", ids[df_counter])

                                sunnova_uploads = True

                        if not sunnova_uploads:
                            logger.info("All items were not uploaded, skipping")
                            continue
                        #if self.name == "bot_Commission_And_Final_Design":
                            # self.bot_update.update_bot_status(self.name, f"Finished Uploading for {opportunity}", ids[df_counter])
                        self.bot_update.complete_opportunity(self.name, ids[df_counter])
                        #else:
                            # self.bot_update.update_bot_status(self.name, f"Finished Uploading for {opportunity}", opportunity)
                        #    self.bot_update.complete_opportunity(self.name, opportunity)
                        #writes basic log to a text file, this will contain every value this code has published inside of an appendable text file at given location in config
                        with open(self.log_location, 'a') as f:
                            f.write(f"Today is - {self.today}, Processed: Address - {addresses[df_counter]}, OpportunityID: {op_id[df_counter]}, SunnovaID: {ids[df_counter]}")
                            f.write("\n")
                            f.close()
                        #creates a list value to add to the excel logs, this will return True assuming that the upload worked
                        self.comments.append(f"Uploaded docs for {opportunity}")
                        self.today = datetime.today()
                        log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, True, self.comments)
                        self.log_list.append(log)
                        self.bot_update.complete_opportunity(self.name, opportunity)

                    #if any exception is caught during this process then we will return False and continue to the next opportunity
                    except Exception as e:
                        print(e)
                        #if self.name == "bot_Commission_And_Final_Design":
                        #    self.bot_update.update_bot_status(self.name, f"Failed on {opportunity}", ids[df_counter])
                        #else:
                        #    self.bot_update.update_bot_status(self.name, f"Failed on {opportunity}", opportunity)
                        self.today = datetime.today()
                        log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments)
                        self.log_list.append(log)
                        pass

            #if source location is sunnova, we begin downloading from sunnova first and upload to box after
            elif source_location == "Sunnova":

                self.sunnova.reinit_drivers(self.prefs)
                self.sunnova.login()

                #for each opportunity inside of the set dataframe, iterate through with df_counter as our main counter through the df
                for df_counter, opportunity in enumerate(op_id):
                    already_uploaded = self.bot_update.update_bot_status(self.name, f"Starting to process {opportunity}", opportunity)
                    if already_uploaded == True:
                        continue
                    try:
                        self.comments = []
                        # uploads = []
                        logger.info("Starting Sunnova Download")
                        print(f"Starting to Process opportunity")
                        self.comments.append(f"Starting to Process: {opportunity}")
                        #basic list to hold each pdf that we will be uploading to box
                        self.upload_pdfs = []
                        
                        #searches sunnvova using the local variable we are searching with from the config
                        #total downloads is a list variable that contains True or False for if the value was downloaded
                        # total_downloads = self.download_from_sunnova(locals()[search_with][df_counter])
                        # self.comments.append(f"The type of contract being processed is {search_with[df_counter]}")
                        try:
                            total_downloads = self.download_from_sunnova(locals()[search_with][df_counter], search_with)
                        except:
                            print(f"Failed on opportunity")
                            continue
                        # if types[df_counter] == "Solar":
                            # total_downloads = self.download_from_sunnova(locals()[search_criteria[df_counter]][df_counter])
                        # elif types[df_counter] == "Roof" or types[df_counter] == "Battery":
                        #     total_downloads = self.download_from_sunnova(locals()[search_criteria[df_counter]][df_counter], types[df_counter])
                        # elif types[df_counter] == "Battery":
                        #   total_downloads = self.download_from_sunnova(locals()[search_criteria[df_counter]][df_counter], types[df_counter])
                        # print(len(total_downloads))
                        # print(len(self.full_config['upload_destination']))
                        #if the length of total files we downloaded is less than total files we expect to upload, or the length of files inside of the folder is less than we 
                        #return False for this opportunity and remove pdf's from file path
                        if len(total_downloads) < len(self.full_config['upload_destination']) or len(self.downloaded_files) < len(self.full_config['upload_destination']):
                            self.comments.append(f"All files were not found - only {len(total_downloads)} files were found out of 4")
                            files = glob.glob(f"{self.download_path}/*pdf")
                            for file in files:
                                os.remove(file)
                            self.today = datetime.today()
                            log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments, types[df_counter])
                            self.log_list.append(log)
                            continue
                        
                        self.bot_update.update_bot_status(self.name, f"Starting Box Upload for {opportunity}", opportunity)
                        logger.info("Starting Box Upload")
                        self.comments.append("Starting Box Upload")
                        # print(self.downloaded_files)
                        # self.comments.append(f"Files we have are: {self.downloaded_files}")
                    
                        total_uploads = self.upload_to_box(opportunity)
                        for item in total_uploads:
                            if item == False:
                                self.comments.append("One item Failed to Upload, returning False")
                                try:
                                    #in case files failed to delete while they failed to upload
                                    for file in self.downloaded_files:
                                        os.remove(file)
                                except:
                                    pass
                                #create a log entry
                                self.today = datetime.today()
                                # log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments, types[df_counter])
                                log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments)
                                self.log_list.append(log)
                                continue

                        self.today = datetime.today()
                        self.comments.append("Sucessfully Uploaded all documents to Opportunity")
                        log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments)
                        # log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, True, self.comments, types[df_counter])
                        self.log_list.append(log)
                        self.bot_update.update_bot_status(self.name, f"Finished {opportunity}", opportunity)
                        self.bot_update.complete_opportunity(self.name, opportunity)


                        with open(self.log_location, 'a') as f:
                            f.write(f"Today is - {self.today}, Processed: Address - {addresses[df_counter]}, OpportunityID: {op_id[df_counter]}, SunnovaID: {ids[df_counter]}")
                            # f.write(f"Today is - {self.today}, Processed: Address - {addresses[df_counter]}, OpportunityID: {op_id[df_counter]}, SunnovaID: {ids[df_counter]}, Type: {types[df_counter]}")
                            f.write("\n")
                            f.close()
                
                    except Exception as e:
                        print(e)
                        #this exception 9/10 times will be caught when we cant find the system project page
                        logger.error(f"Could not process {opportunity}")
                        self.comments.append(f"Could not process {opportunity}, No Results Found in Sunnova")
                        try:
                            #catch any files that made the download before the exception
                            files = glob.glob(f"{self.download_path}/*pdf")
                            for file in files:
                                os.remove(file)
                        except:
                            pass
                        #create a log entry
                        self.today = datetime.today()
                        # log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments, types[df_counter])
                        log = SunnovaLogger(df_counter, self.today, ids[df_counter], opportunity, names[df_counter], addresses[df_counter], self.argument, False, self.comments)

                        
                        self.log_list.append(log)
                   
                        pass
                self.sunnova.close()

            self.interpret_logs()
            self.send_logs()
            self.bot_update.edit_end()
        #self.sunnova.close()

    def send_logs(self):
        """
        Creates and sends excel logs
        """
        self.bot_update.update_status(self.name)

        text = """\
            This is the Sunnova Report
            """

        html = """
            <html>
                <body>
                    <p>
                    This is the Sunnova Report
                    </p>
                </body>
            </html>
            """

        try:
            SunnovaLogger.create_excel(self.log_list, email_subject=str(self.argument), text=text, html=html)
        except Exception as e:
            print(e)
            logger.error("Failed to send report")

    def init_dataframe(self, url):
        # self.driver.get("https://trinity-solar.lightning.force.com/lightning/r/Report/00O0d000005Y1PeEAK/view")
        # time.sleep(100000)
        logger.info("Initializing Dataframe")
        # print(url)
        # self.driver = self.sunnova.reinit_drivers(self.prefs)
        # try:
        #     self.login(url)
        # except:
        #     pass
        # self.download_report()
        ids, op_id, names, addresses = self.create_df(url)
        # ids, op_id, names, addresses, types, search_criteria = self.create_df()
  
        return ids, op_id, names, addresses

    def interpret_logs(self):
        hours_to_send_logs = ["17", "20", "21", "22", "23", "24"]
        hour = self.today.strftime("%H")

        completed_opps = self.bot_update.Select_Opportunities_Completed_Today(self.name)
        total_upload = len(completed_opps)
        print(total_upload)
        just_send = True
        if hour in hours_to_send_logs:
            text = f"""\
            Hello,
            Today, We ran {self.argument}
            The Total Uploaded Opportunities Were: {total_upload}
                   """
            html = f"""\
            <html>
                <body>
                    <p>
                    Hello,<br>
                    Today, We ran {self.argument}<br>
                    The Total Uploaded Opportunities Were: {total_upload}<br>
                    </p>
                </body>
            </html>
                    """
        else:
            return None

        if total_upload == 0:
            return None

        try:
            SunnovaEmail.send(email_subject=f"Total Uploads From {self.argument}", text=text, html=html)
        except Exception as e:
            print(e)
            pass

        return True

    def download_from_sunnova(self, sunnova_id, search_with, type_of_contract=None):
        """
        downloads all files from sunnova
        """
        sunnova_file_count = 0
        # self.sunnova.reinit_drivers(self.prefs)
        total_downloads = []
        logger.info("Selecting System Project")
        self.comments.append("Selecting System Project")
        # sunnova_id = "7 Ellen Place, Huntington Station, NY"
        self.sunnova.selectSystemProject(sunnova_id, search_with=search_with)
        print("selected")
        self.downloaded_files = []
        for temp_counter, sunnova_item in enumerate(self.full_config['download_location']):

            if isinstance(sunnova_item, list):
                print("passing")
                pass
            else:
                # print(sunnova_item)
                download_argument = getattr(SunnovaPortal, f"download_{sunnova_item}")
                logger.info(f"Searching for download link - download_{sunnova_item}")
                self.comments.append(f"Searching for download link - download_{sunnova_item}")
                if not type_of_contract:
                    downloaded_file = download_argument(self.sunnova, self.download_path)
                else:
                    downloaded_file = download_argument(self.sunnova, self.download_path, type_of_contract)
                #quit()
                if isinstance(downloaded_file, list):
                    for item in downloaded_file:
                        # print(item)
                        # print("??")
                        self.downloaded_files.append(item)
                        # total_downloads.append(True)
                        total_downloads.append(True)
                        self.comments.append(f"Downloaded {item}")
                else:
                    self.downloaded_files.append(downloaded_file)
                    self.comments.append(f"Downloaded {downloaded_file}")
                    total_downloads.append(True)
        return total_downloads
 
    def upload_to_box(self, opportunity):
        """
        Uploads files in a list to box based on the given folders in order
        """
        quit_count = 0
        total_uploads = []
        created_box_folder_structure = False
        for item_counter, download in enumerate(self.downloaded_files):
            upload = False
            try:

                logger.info("Getting Opportunity Folder ID")

                box_folder_grab_quit_count = 0
                while True:
                    try:
#                         folder_id = self.get_folder_id_from_opportunity_id(opportunity)
                        folder_id = self.box.get_opp_folder_id(opportunity)

                        if not created_box_folder_structure:
                            self.comments.append("Creating Box Folder Structure If Applicable")
                            self.create_box_folder_structure(folder_id)
                            created_box_folder_structure = True
                        try:
                            #if a file doesnt have an upload location, set a default
                            catchme = self.full_config['upload_destination'][item_counter]
                        except:
                            item_counter = 0

                        folder_argument = getattr(BoxAPI, f"get_{self.full_config['upload_destination'][item_counter]}_folder_id")
                        logger.info(f"Getting {folder_argument}")
                        folder_id = folder_argument(self.box, folder_id)
                        break
                    except Exception as e:
                        print(e)
                        logger.info("Retrying Box Folder ID Grab")
                        self.comments.append(f"Retrying Box Folder Call For: {self.full_config['upload_destination'][item_counter]}")
                        if box_folder_grab_quit_count == 10:
                            self.comments.append("Failed to Call BoxAPI to grab Folder id")
                            return False
                        box_folder_grab_quit_count += 1
                        time.sleep(10)
                # while True:
                try:
                    while True:
                        try:
                            resp = self.box.request_items_in_folder(folder_id).json()
                            if resp:
                                break
                        except:
                            print("Retrying Box grab")
                            self.comments.append("Retrying to Grab Box Folder items")
                            time.sleep(5)
                    # resp = resp.json()
                    for file in resp['entries']:
                        filename = file['name']
                        filename = filename.lower()
                        download_name = download.lower()
                        # print(filename)
                        if filename in download_name:
                            file_id = file['id']

                            quit_counter = 0
                            while True:
   
                                if not download or download == 'None' or download == None or download == "none":
                                    print("Download path is empty")
                                    logger.error("Could not Upload file, returning False")
                                    self.comments.append(f"Could not Upload file: {download}, returning False")
                                    total_uploads.append(upload)
                                    break
                                download = os.path.normpath(download)
                                response = self.box.request_upload_new_file_version(file_id, download, folder_id)

                                if response.status_code == 201:
                                    upload = True
                                    total_uploads.append(upload)
                                    self.comments.append(f"Successfully Uploaded {download}")
                                    os.remove(download)
                                    break
                                else:
                                    quit_counter += 1
                                    if quit_counter == 10:
                                        print("Failed To Upload file")
                                        self.comments.append(f"Failed To Upload file {download}")
                                        total_uploads.append(upload)
                                        break
                                    print(f"Retrying New File Version Upload")
                                    time.sleep(5)
                    if upload == False:
                        quit_counter = 0
                        while True:
                            response = self.box.request_upload_file(download, folder_id)
                            if response.status_code == 201:
                                upload = True
                                os.remove(download)
                                self.comments.append(f"Successfully Uploaded {download}")
                                total_uploads.append(upload)
                                break
                            else:
                                quit_counter += 1
                                if quit_counter == 10:
                                    print("Failed To Upload file")
                                    self.comments.append(f"Failed To Upload file {download}")
                                    total_uploads.append(upload)
                                    break
                                print(f"Retrying")
                                time.sleep(5)
                    # break
                except Exception as e:
                    print(quit_count)
                    if quit_count == 5:
                        logger.error(f"Could not Upload {download} to {self.full_config['upload_destination'][item_counter]}")
                        self.comments.append(f"Could not Upload {download} to {self.full_config['upload_destination'][item_counter]}")
                        total_uploads.append(False)
                        try:
                            os.remove(download)
                        except:
                            pass
                        break
                    # print(e)
                    logger.info("Retrying File Upload")
                    self.comments.append("Retrying File Upload")
                    quit_count += 1
                    time.sleep(3)

                logger.info(f"Uploaded {download} to {folder_id}")
                self.comments.append(f"Uploaded {download} to {folder_id}")
                # print(response)
                try:
                    os.remove(download)
                except:
                    pass
            except:
                logger.error(f"Did not finish uploading files for {opportunity}")
                self.comments.append(f"Did not finish uploading files for {opportunity}")
                continue
        return total_uploads
    
    def get_box_folder_id(self):
        return None        

    def download_from_box(self, Opportunity):
        """
        Downloads from box folders
        """
        # print("")
        #counter to iterate through the config file, this will determine each file / list we worked on
        box_list_count = 0
        #counter to iterate through a list value inside of the config files, ex: ['GENESIS SITE REPORT', 'FULL SET', 'EL'] this is listed as a single file in the config, this is because these files need merging
        #the file count will iterate through these files
        box_file_count = 0
        # print(self.full_config['download_location'])
        for box_folder in self.full_config['download_location']:
            #Exit coded in, should never reach this if statement
            if box_folder == "None":
                print("Finished Downloading")
                return True

            #if the box folder is a list, ex ['GENESIS SITE REPORT', 'FULL SET', 'EL']
            if isinstance(box_folder, list):
                full_file_name_list = False
                box_file_id = None

                #set the amount of files we expect to download
                length_of_files_expected = len(box_folder)
                list_files = self.full_config['files_to_download']
                
                pdfs = []
                # print(f"list - {box_folder}")
                self.comments.append(f"Looking For Files: {box_folder}")
                for folder in box_folder:
 
                    full_file_name = list_files[box_list_count][box_file_count]
                    if isinstance(full_file_name, list):
                        full_file_name_list = full_file_name
                        full_file_name = full_file_name[0]

                    quit_count = 0
                    box_folder_quit_count = 0
                    while True:
                        try:
                            #initial parent id for opp folder
#                             parent_id = self.get_folder_id_from_opportunity_id(Opportunity)
                            parent_id = self.box.get_opp_folder_id(Opportunity)
                            logger.info(f"get_{folder}_folder_id")
                            box_download = getattr(BoxAPI, f"get_{folder}_folder_id")
                            # self.box.request_items_in_folder()
                            folder_id = box_download(self.box, parent_id)
                            break
                        except:
                            self.comments.append(f"Retrying to call box folder: {folder}")
                            logger.info("Retrying Box Folder Grab")
                            if box_folder_quit_count == 10:
                                self.comments.append("Could not Call Box API to get folder id")
                                return False
                            box_folder_quit_count += 1
                            time.sleep(10)

                    while True:
                        count = 0
                        indexes = []
                        response = self.box.request_items_in_folder(folder_id).json()
                        if not response:
                            return False
                        site_info_design_files = response['entries']
                        
                        try:
#                             while True:
#                                 try:
#                                     response = self.box.request_items_in_folder(folder_id).json()
#                                     if response:
#                                         break
#                                 except:
#                                     self.comments.append("Retrying Call for items inside box folder")
#                                     logger.info("Retrying Call for items inside box folder")
#                             site_info_design_files = response['entries']

                            if full_file_name in self.full_config['files_with_repeat_names']:
                                # print("HERE WE ARE")
                                for index, file in enumerate(site_info_design_files):
                                    file_name = file['name']
                                    logger.info(f"found file: {file_name}")
                                    self.comments.append(f"found file: {file_name}")

                                    if full_file_name in file_name:
                                        checker = False
                                        print("CHECKING AGAINST FILES TO AVOID")

                                        avoid_these_files = self.full_config['files_to_avoid']
                                        for item in avoid_these_files:

                                            if item in file_name:
                                                # print(f"Removing file listed to avoid: {item}")
                                                site_info_design_files.pop(index)
                                                checker = True
                                                # continue
                                                break
                                        if not checker:
                                            count += 1
                                    if full_file_name_list:
                                        if full_file_name_list[-1] in file_name:
                                            # logger.info(f"Downloading File: {file_name}")
                                            box_file_id = file['id']
                                            self.comments.append(f"Downloading File: {file_name}")
                                            break


                            if count > 1 and not box_file_id:
                                logger.error(f"Failed To Determine Which file to Download for {Opportunity}.. Passing")
                                self.comments.append(f"Failed To Determine Which file to Download for {Opportunity}.. Passing")
                                return False
                            if not box_file_id:
                                box_file_id = None

                                for file in site_info_design_files:
                                    # box_file_id = None
                                    file_name = file['name']

                                    # print(full_file_name)
                                    # print(">???<")
                                    logger.info(f"found file: {file_name}")
                                    self.comments.append(f"found file: {file_name}")

                                    if full_file_name_list:
                                        for item in full_file_name_list:
                                            if item in file_name:
                                                box_file_id = file['id']
                                                logger.info("Found File ID")
                                                break
                                    else:
                                        if full_file_name in file_name:

                                            box_file_id = file['id']
                                            logger.info("Found File ID")
                                            break
                            logger.info("Requesting items")
                            self.comments.append("Requesting items")
                            if not box_file_id:
                                print(f"Failed to Find files")
                                self.comments.append(f"Failed to Find {list_files[box_list_count][box_file_count]}")
                                return False
        # genesis site report
                            response = self.box.request_download_file(box_file_id)
                            system_path = fr"{self.download_path}\{full_file_name}.pdf"
                            #reset box file id for the next iteration
                            box_file_id = None
                            with open(system_path, 'wb') as f:
                                f.write(response.content)
                                f.close()
                                logger.info("Wrote file to local path")
                                self.comments.append("Wrote file to local path")
                            pdfs.append(system_path)
                            box_file_count += 1
                            break
                        except:
                            print("retrying box download")
                            self.comments.append(f"retrying box download for {full_file_name}")
                            quit_count += 1
                            if quit_count == 10:
                                box_file_count += 1
                                # box_list_count += 1
                                break
                            time.sleep(10)
                if length_of_files_expected == len(pdfs):
                    self.merge(pdfs)
                    self.comments.append("Merging Files")
                else:
                    logger.error(f"Failed to Download all required Files for {Opportunity}, Returning as False")
                    self.comments.append(f"Failed to Download all required Files for {Opportunity}, Returning as False")
                    return False

                box_list_count += 1

            else: #if type is not a list
                # update_bot_status(f"Downloading Files for {Opportunity}")
                full_file_name = self.full_config['files_to_download']
                full_file_name = full_file_name[box_list_count]
                # print(full_file_name)

                # print(f"string - {box_folder}")
                self.comments.append(f"Looking For: {box_folder}")
                quit_counter = 0
                while True:
                    try:
#                       parent_id = self.get_folder_id_from_opportunity_id(Opportunity)
                        parent_id = self.box.get_opp_folder_id(Opportunity)
                        logger.info(f"get_{box_folder}_folder_id")
                        box_download = getattr(BoxAPI, f"get_{box_folder}_folder_id")
                        # self.box.request_items_in_folder()
                        folder_id = box_download(self.box, parent_id)
                        # print(folder_id)
                        break
                    except Exception as e:
                        quit_counter += 1
                        if quit_counter == 10:
                            return False
                        print(e)
                        logger.info("Retrying Box Folder Grab")
                        self.comments.append(f"Retrying to call box folder: {folder}")

                        time.sleep(10)

                response = self.box.request_items_in_folder(folder_id).json()
                # print(response)
                site_info_design_files = response['entries']
                for file in site_info_design_files:
                    file_name = file['name']
                    file_name = file_name.lower()
                    full_file_name = full_file_name.lower()
                    if full_file_name in file_name:
                        if "400" in file_name:
                            continue
                        # elif len(file_name) < 35:
                        #     pass
                        else:
                            box_file_id = file['id']
                            logger.info("Found File ID")
                            self.comments.append("Found File ID")
                logger.info("Requesting items")
                self.comments.append("Requesting items")
                if not box_file_id:
                    # update_bot_status(f"Failed on {Opportunity}")
                    print(f"Failed to Find files")
                    self.comments.append(f"Failed to Find {list_files[box_list_count][box_file_count]}")

                response = self.box.request_download_file(box_file_id)
                system_path = fr"{self.download_path}\{full_file_name}.pdf"
                with open(system_path, 'wb') as f:
                    f.write(response.content)
                    f.close()
                    logger.info("Wrote File to Local Path")
                    self.comments.append("Wrote File to Local Path")

                self.upload_pdfs.append(system_path)
                box_list_count += 1
        return True
    
    def invoice_queue(self, folder_paths):
        """
        Runs a queue check, this will keep checking a designated folder in the config file until files are adding in (this will happen through Power automate and our RPA server, we will use 
        Power automate to check for the email containing the invoices, which will send to sharepoint and download onto the server - SunnovaPortal.download_from_sharepoint(folder_path))
        """
        self.bot_update.register_bot(self.name)

        while True:
            for index, path in enumerate(folder_paths):
                invoice_paths = glob.glob(fr"{folder_paths[path]}\*")

                try:
                    invoice_path = invoice_paths[0]
                except:
                    invoice_path = invoice_paths

                if "pdf" in invoice_path:
                    files = invoice_path
                else:
                    files = glob.glob(f"{invoice_path}/*")

                if len(files) < 1:
                    print(f"waiting for {path}")
                    self.bot_update.update_status(self.name)
                    time.sleep(10)
                    continue
                else:
                    if "true" in path.lower():
                        os.remove(folder_paths[path])
                    else:
                        # self.bot_update.register_bot(self.name, logs=f"In Queue: {}")
                        self.bot_update.update_status(self.name)
                        time.sleep(20)
                        email = [
                            "avigoyal@trinity-solar.com",
                            "jeffmacdonald@trinity-solar.com",
                            "powerautomateteam@trinity-solar.com"
                            ]

                        text = f"""\
                        The {path} Process has started
                            """
                        html = f"""
                            <html>
                                <body>
                                    <p>
                                    The {path} Process has started
                                    </p>
                                </body>
                            </html>
                            """
                        subject = f"{path}"
                        SunnovaEmail.send(path=None, email=email, html=html, text=text, email_subject=subject)
                    
                        invoiceattribute = getattr(SunnovaPortal, f"{path}")
                        print(f"Running {self.argument}")

                        success_count, fail_count, full_counter = invoiceattribute(self.sunnova, invoice_path, self.bot_update.update_bot_status, self.bot_update.complete_opportunity)
                        self.bot_update.edit_end()
                        # email = ["avigoyal@trinity-solar.com",
                        #         "jeffmacdonald@trinity-solar.com"]

                        text = """\
                        The Sunnova System invoice has been uploaded
                        Total invoices uploaded:""" + str(success_count) + """
                        Total Invoices not uploaded:""" + str(fail_count) + """
                        Total Invoices run through:""" + str(full_counter) + """ 
                        """

                        html = """
                        <html>
                            <body>
                                <p>
                                The Sunnova System invoice has been uploaded <br>
                                </p>
                                <p>
                                Total invoices uploaded:""" + str(success_count) + """ <br>
                                </p>
                                <p>
                                Total Invoices not uploaded:""" + str(fail_count) + """<br>
                                </p>
                                <p>
                                Total Invoices run through:""" + str(full_counter) + """ 
                                </p>
                            </body>
                        </html>
                        """
                        SunnovaEmail.send(text=text, html=html, email=email, email_subject=f"Sunnova {path} Invoice Upload")


    def create_box_folder_structure(self, box_opportunity_folder_id):
        """
        Creates a basic BOX folder structure (if not created) in BOX
        for given opportunity
        """
        # update_bot_status("Checking Box Folder Structure")
        EXPECTED_FOLDERS = [
            'Site Info-Designs',
            'Sales Documents',
            'Miscellaneous Documentation',
            'Job Photos',
            'Installation Documents',
            'Contract Documents',
            'Archive',
            'Applications',
            'Accounting'
        ]
        existing_folders = []
        # logger.info('Checking box folder structure')
        # BoxValidate(f'Box Request items - Transfer SiteCapture photos {box_opportunity_folder_id} - Create Box folder structure')
        items_res = self.box.request_items_in_folder(
            box_opportunity_folder_id)
        if items_res:
            items = items_res.json()['entries']
            for item in items:
                existing_folders.append(item['name'])

        for folder in EXPECTED_FOLDERS:
            if folder not in existing_folders:
                # logger.info(f'Could not find {folder}, creating folder...')
                print("Creating folder...")
                # BoxValidate(f'Box Create Folder - Transfer SiteCapture photos {box_opportunity_folder_id} - Create Box folder structure')
                self.box.create_folder(folder, box_opportunity_folder_id)
                print("created folder structure")
                self.comments.append(f"Created folder: {folder}")
            else:
                print(f"Found: {folder}")

    def input_verification_code(self):
        """
        Pulls the verification code from Power Automate Email
        """
        code = None
        while not code:
            time.sleep(10)
            code = self.get_salesforce_verification_code()
        return code


    def get_salesforce_verification_code(self, account_id=PA_ACCOUNT_ID):
        """
        Gets the verification CODE
        """
        # update_bot_status("Getting verification")
        while True:
            try:
                self.access_token = outlook.get_new_access_token()
                break
            except:
                logger.info("Retrying Outlook API Token")
                time.sleep(10)
        first_ten_mailbox = outlook.get_mail(account_id)
        for email in first_ten_mailbox['value']:
            if 'your identity in Salesforce' in email['subject']:
                message_id = email['id']
                body = outlook.get_message_body(message_id, account_id)
                groups = re.search(r"Verification Code: (\d{6})", body)
                code = groups.group(1)
                return code
        return None

    def get_folder_id_from_opportunity_id(self, opportunity_id):
        """
        Gets a Box folder ID by using an opportunity ID
        """
        content = {'opp_id': opportunity_id}

        try:
            response = requests.post(FOLDER_ID_URL, json=content)

            response_dict = response.json()
            folder_id = response_dict['folder_id']
            if folder_id:
                return folder_id
            else:
                return None
        except Exception as e:
            return None

    def login(self, link):
        self.driver.get(link)
        self.driver.find_element(by=By.ID, value='username').send_keys(self.salesforce_username)
        self.driver.find_element(by=By.ID, value='password').send_keys(self.salesforce_password)
        self.driver.find_element(by=By.ID, value='Login').click()
        verf = ""
        # try:
        print("Retrieving Verification Code")
        time.sleep(2)
        # page_text = self.driver.find_element_by_css_selector('body').text
        page_text = self.driver.find_element(by=By.CSS_SELECTOR, value='body').text
        page_text = str(page_text)
        # print(page_text)
        if "Verify Your Identity" in page_text:
            self.verification_checker = True
            verf = self.input_verification_code()
            # print(verf)
            #inputs the verification code
            self.driver.find_element(by=By.XPATH, value='//*[@id="emc"]').click()
            self.driver.find_element(by=By.XPATH, value='//*[@id="emc"]').send_keys(verf)
            #clicks verify
            self.driver.find_element(by=By.XPATH, value='//*[@id="save"]').click()
            # self.driver.find_element_by_xpath('//*[@id="save"]').click()
            time.sleep(30)
        elif "Problem Verifying Your Identity" in page_text:
            self.driver.close()
            print("Failed to load verification page, Salesforce is down, or too many access codes received today")
            exit()

        try:
            elem = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tryLexDialogX")) #This is a dummy element
            )
            elem.click()
        except:
            pass
        return None

    def export(self, mode):
        """
        Selects to export and download the report
        """
        #clicks export file format
        if mode == "classic":
            file_type = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#xf"))
            )
            file_type.click()
            #clicks csv
            # self.driver.find_element_by_xpath('//*[@id="xf"]/option[1]').click()
            csv = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="xf"]/option[1]')))
            csv.click()
            export = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bottomButtonRow"]/input[1]'))
            )

            export.click()
        elif mode == "lightning":
            file_type = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="785:0"]')))
            file_type.click()
            csv = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="785:0"]/option[3]')))
            csv.click()
            export = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/div/div[2]/div/div[3]/button[2]/span')))
            export.click()

    def download_report(self):
        self.driver.maximize_window()

        try:
            export = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="report"]/div[3]/div[2]/input[8]')))
            export.click()
            self.export("classic")
        except:
            print("lightining export")
            dropdown = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="xAy1uC5dOg"]/button')))
            dropdown.click()
            export = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Export")]')))
            export.click()
            details = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Details Only")]')))
            details.click()
            self.export("lightning")
        while True:
            self.file = glob.glob(f"{self.download_path}/*csv")
            if len(self.file) == 0:
                time.sleep(1)
                print("Waiting on Download")
            else:
                time.sleep(10)
                self.driver.quit()
                print("Download Complete")
                break
        # print(self.file)
        # quit()

    def create_df(self, url):
        """
        Creates a df using given data and splits into separate lists
        """
        df1 = self.salesforce.get_report(url)
        # print(df1)
        ids = []
        op_id = []
        names = []
        addresses = []
        types = []
        search_critera = []

        # counter = 1

        for value in df1.values:
            
            if value[1] != "":
                # try:
                #     #USE ADDRESS TO SEARCH THIS
                #     # if "Solar" in value[12] and not isinstance(value[1], float):
                #     print(value[12])
                #     if "Solar" in value[12] and value[1] != "":
                #     # if value[1] != "nan" and value[1] != '' and value[1] != " " and value[1] != "''":#and len(value[1] > 4):
                #         # ids.append(value[1])
                #         # op_id.append(value[2])
                #         # names.append(value[4])
                #         # addresses.append(value[8])
                #         ids.append(value[0])
                #         op_id.append(value[1])
                #         names.append(value[2])
                #         addresses.append(value[3])
                #         types.append("Solar")
                #         search_critera.append("addresses")
                #         #roofing
                #     #USE ROOFING ID TO SEARCH THIS
                #     # if "Roof" in value[12] and not isinstance(value[4], float):
                #     if "Roof" in value[12] and value[4] != "":
                #         print(type(value[4]))
                #         ids.append(value[4])
                #         op_id.append(value[1])
                #         names.append(value[2])
                #         addresses.append(value[3])
                #         # value[4] #roofing id
                #         types.append("Roof")
                #         search_critera.append("ids")
                #         #MARK THAT ITS ROOFING SO I CAN APPEND FILE NAMES
                #         #ANDProduct Category equals "Solar"
                #     #battery
                #     #USE BATTERY ID TO SEARCH THIS
                #     if "Battery" in value[12] and value[5] != "":
                #         ids.append(value[5])
                #         op_id.append(value[1])
                #         names.append(value[2])
                #         addresses.append(value[3])
                #         # value[5] #battery id
                #         types.append("Battery")
                #         search_critera.append("ids")
                #         #MARK THAT ITS BATTERY SO I CAN APPEND FILE NAMES
                #     #roof only, may not have a roofing id but can be found through address
                #     #USE ADDRESS TO SEARCH THIS
                #     if "Roof" in value[12] and value[4] == "":
                #         ids.append(value[0])
                #         op_id.append(value[1])
                #         names.append(value[2])
                #         addresses.append(value[3])
                #         types.append("Roof")
                #         # print("APPENDING A ROOF PROJECT")
                #         search_critera.append("addresses")
                #     #battery only, may not have a roofing id but can be found through address
                #     #USE ADDRESS TO SEARCH THIS
                #     if "Battery" in value[12] and value[5] == "":
                #         ids.append(value[0])
                #         op_id.append(value[1])
                #         names.append(value[2])
                #         addresses.append(value[3])
                #         types.append("Battery")
                #         search_critera.append("addresses")
                    
                # except:
                ids.append(value[0])
                op_id.append(value[1])
                names.append(value[2])
                addresses.append(value[3])
        # counter += 1
            # except:
            #     break
        # os.remove(self.file)
        # print(ids)
        return ids, op_id, names, addresses

    def merge(self, pdfs):
        """
        Merges Given pdfs
        """
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        merger.write(fr"{self.download_path}\result.pdf")
        self.upload_pdfs.append(fr"{self.download_path}\result.pdf")
        merger.close()
        for pdf in pdfs:
            os.remove(pdf)
        return None

    def upload_to_sunnova(self, id, file, upload_attribute):
        """
        For Commission and Final Design, takes two files (files are given as a list) and sends to proper spot in Sunnova using SunnovaPortal()
        """
        # print(id)
        # print(file)
        # print(upload_attribute)
        try:
            self.comments.append(f"Trying to Upload {file}")
            upload_attribute(self.sunnova, file)
        except:
            logger.error("File Already Uploaded")
            self.comments.append("File Already Uploaded")
            os.remove(file)
            return False
            # pass
        self.comments.append(f"Uploaded {file} to {id}")

        os.remove(file)
        return True

    def get_sunnova_id():
        #web scrapes sunnova to get the ID back
        return True

    def get_json(system_id):
        #gets full json from system id
        resp = requests.get("https://trinityapipanda.azurewebsites.net/api/Sunnova/GetProjectBlocks/a8u4W000000AuVYQA0", headers=self.headers)
        return resp.json()

    def register_bot(self):
        content = {'status': 'Registering',
                   'function': self.function, 'key': '951753'}
        content = {'status': 'Registering',
                   'function': self.function}
        url = r'http://148.77.75.60:6050/api/bots/' + self.name
        # url = r'http://20.119.35.89:6050/api/bots' + self.name
        # url = r'http://69.27.238.133:6050/api/bots' + self.name
        # url = r'http://10.0.3.4:6050/api/bots' + self.name
        try:
            res = requests.post(url, json=content)
            if res.status_code == 201:
                print(f"Register Bot Status: Registered")
            if res.status_code == 204:
                print(f'Register Bot Status: Updated')
            else:
                print(f'Got Status Code {res.status_code}')
        except Exception as e:
            print(e)
            print("Could not register bot...")

    def update_status(self, status):
        content = {'status': status}
        url = r'http://148.77.75.60:6050/api/bots/' + self.name
        # url = r'http://20.119.35.89:6050/api/bots' + self.name
        # url = r'http://69.27.238.133:6050/api/bots' + self.name
        # url = r'http://10.0.3.4:6050/api/bots' + self.name
        try:
            res = requests.post(url, json=content)
            if res.status_code == 204:
                print(f'Bot Status: Updated')
            else:
                print(f'Got Status Code {res.status_code}')
        except Exception:
            print("Could not update bot status...")

    def update_queue(self, queue):
        #returns with status code 400, invalid request - looking into possible ways to add a queue
        content = {'name': queue}
        url = r'http://148.77.75.60:6050/api/bots/' + self.name + "/queue"
        # url = fr'http://148.77.75.60:6050/api/bots/{self.name}/queue' 
        try:
            res = requests.post(url, json=content)
            if res.status_code == 204:
                print(f'Bot Status: Updated')
            else:
                print(f'Got Status Code {res.status_code}')
        except Exception:
            print("Could not update bot queue...")

    # def update_dashboard(self, status=None):
    #     # self.function = self.argument
    #     self.name = f"bot_{self.argument}"
    #     # self.register_bot()
    #     update_bot_status(self.name, "Active")
    #     # print("Bot Status Updated")
    #     logger.info("Bot Status Updated")

if __name__ == "__main__":
    a = SunnovaReports()
    # a.interpret_logs()
    a.run()

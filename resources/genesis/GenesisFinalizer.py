from resources.Box.BoxAPI import BoxAPI
from resources.Salesforce import Salesforce
from resources.SalesforceAPI  import SalesforceAPI 
from resources.config import  MICROSOFT_USERNAME, MICROSOFT_PASSWORD
from api.box.BoxCallValidate import BoxValidate 
# from modules.autobot import Autobot
import os
import time
import csv
import requests
import threading
import random
from pywinauto.application import Application
from resources.genesis import GenesisLogger

def SketchUp_Salesforce_via_Microsoft(sf_dlg, logger):
    logger.info("Salesforce Login via Microsoft SSO")
    sf_dlg.Button1.click_input()
    """
    time.sleep(5)
    login_status = sf_dlg.child_window(title="Allow",control_type="Button").exists(timeout=5)   
    if login_status: 
        sf_dlg.Button2.click_input()     
        # sf_dlg.send_keys("{PGDN}")       
        sf_dlg.type_keys("{PGDN}")  
        time.sleep(3)  
        sf_dlg.Allow.click_input()     
    else:     
        sf_dlg.Button1.click_input() 
        time.sleep(5)
        sf_dlg.PasswordEdit.type_keys(MICROSOFT_PASSWORD)    
        sf_dlg.Button2.click_input()         
        time.sleep(5)
        sf_dlg.Button2.click_input()
        time.sleep(5) 
        sf_dlg.Button2.click_input()     
        # sf_dlg.send_keys("{PGDN}")       
        sf_dlg.type_keys("{PGDN}") 
        time.sleep(3)   
        sf_dlg.Allow.click_input()        
     """
   
    logger.info("Salesforce Login via Microsoft Credentials Completed")   
    return   

def SketchUp_Salesforce_via_Okta(sf_dlg, logger):
    try:
        sf_dlg.Hyperlink.click_input()
    except:
        sf_dlg.Button1.click_input()
    try:
        sf_dlg.Button1.click_input()
        sf_dlg.UsernameEdit.type_keys('^a^c')
        sf_dlg.UsernameEdit.type_keys("{BACKSPACE}")
        sf_dlg.UsernameEdit.type_keys("power.automateteam@trinitysolarsystems.com")
        sf_dlg.Next.click_input()       
        sf_dlg.PasswordEdit.type_keys("pA951456!")
        logger.info("Entering Okta Credentials")
        sf_dlg.Verify.click_input() 
        logger.info("Salesforce Login via Okta")
        sf_dlg.type_keys("{PGDN}")
        sf_dlg.Allow.click_input()        
    except:   
        sf_dlg.type_keys("{PGDN}")
        sf_dlg.Allow.click_input()
        logger.info("Salesforce Login via Okta")
        return

def SketchUp_Salesforce_via_AzureAD(sf_dlg, logger, retry=False):
    #try:
    #    sf_dlg.Hyperlink.click_input()        
    #except:
    #    sf_dlg.Button2.click_input()        
    try:        
        #sf_dlg.Button2.click_input()        
        sf_dlg.UsernameEdit.type_keys(SALESFORCE_USERNAME)
        sf_dlg.PasswordEdit.type_keys(SALESFORCE_PASSWORD)
        logger.info("Entering AzureAD Credentials")
        sf_dlg.Button.click_input()
        #sf_dlg.Button.click_input()
        #logger.info("Salesforce Login via AzureAD")
        #sf_dlg.type_keys("{PGDN}")
        #sf_dlg.Allow.click_input()        
    except:
        if retry:
            return False
        try:
            sf_dlg.Hyperlink.click_input()        
        except:
            sf_dlg.Button2.click_input()
        #sf_dlg.type_keys("{PGDN}")
        #sf_dlg.Allow.click_input()
        #logger.info("Salesforce Login via AzureAD")
        SketchUp_Salesforce_via_AzureAD(sf_dlg, logger, True)

class GenesisFinalizer:
    REPORT_TYPES = {
        "same_day": r'https://trinity-solar.lightning.force.com/lightning/r/Report/00O5b0000050NlJEAU/view',
        "rsa": r'https://trinity-solar.lightning.force.com/lightning/r/Report/00O5b0000050PFP/view'
    }
    REPORT_TYPES = {
        "same_day": '00O5b0000050NlJEAU',
        "rsa": '00O5b0000050PFP'
    }
   
    DEFAULT_STATE_MODULES = {
        #"ca": "350:Longi- LR4-60HPB-350M",
        "ca": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        # "ct": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "ct": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        #"de": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "de": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        "fl": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        #"fl": "405:Hanwha - Q.PEAK DUO BLK ML-G10 plus 405",
        # "ma": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "ma": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        #"md": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "md": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        #"nj": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "nj": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        #"ny": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "ny": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        # "pa": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400",
        "pa": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        "ri": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410",
        "nh": "410:Hanwha - Q.PEAK DUO BLK ML-G10 plus 410"
        # "ri": "400:Hanwha - Q.PEAK DUO BLK ML-G10 400"
    }
    # FL updated 11/1/21 JM
    # CT MA PA updated to 405 1/16/23 JM 
    # Updated to 405 for all states on   02/27/2023 by Pahan         
    DEFAULT_RERUN_MODULE = "400:Hanwha - Q.PEAK DUO BLK ML-G10 400"

    # PA = Hanwha - Q.PEAK DUO BLK-G9 380 8/8/22 JM
    # CA= Longi 350s
    # FL= 340s
    # NJ,DE,MD,RI,NY,MA,CT,PA= 400s jm 10/27
    # Default 400s KJ 8/13

    def __init__(self, rerun=False, name=None) -> None:
        self.RERUN = rerun
        self.box_api = BoxAPI(application=name)
        # self.autobot_api = Autobot()
        self.salesforce = Salesforce()
        self.current_box_folder_id = None
        self.completed_opportunities = []
        self.logger = GenesisLogger()
        self.start_bugsplat_thread()
        self.salesforce_api = SalesforceAPI()

    def start_bugsplat_thread(self):
        """
        Starts a thread that checks for bugsplat
        processesing the background,
        closing them in encountered.
        """
        def bugsplat_thread():
            while True:
                try:
                    # Bugsplat spawns its own process, not a popup
                    os.system(r"taskkill /im BsSndRpt64.exe")
                    time.sleep(10)
                except Exception:
                    pass

        thread = threading.Thread(target=bugsplat_thread)
        thread.start()

    def get_opportunities(self, report_url) -> list:
        """
        Get opportunity ID's that need a genesis finalized.
        Valid report types are 'saturday', 'same_day', 'tomorrow', 'today'.
        """
        opportunities = []
        report = self.salesforce_api.get_report(report_url)
        for value in report['Opportunity ID']:
            opportunities.append(value)

        return opportunities

    def has_street_side_pathways(self, opportunity_id) -> bool:
        """
        Get the streetside pathways value for an opportunity.
        Used for handling the Genesis popup.
        """
        try:
            account_id = list(self.salesforce_api.Select(f"Select AccountId from Opportunity where Id = '{opportunity_id}'")['AccountId'])[0]
            township_id = list(self.salesforce_api.Select(f"Select Township__c from Account where Id = '{account_id}'")['Township__c'])[0]
            pathways = list(self.salesforce_api.Select(f"Select Street_Side_Pathway__c from Account where Id = '{township_id}'")['Street_Side_Pathway__c'])[0]
        except:
            return True
        return pathways

    def set_action_item_start(self, opportunity_id) -> None:
        """
        Sets the RSA action item status as started
        """
        try:
            action_item = list(self.salesforce_api.Select(f"Select Id from Action_Item__c where Opportunity__c = '{opportunity_id}' and name = 'Remote Site Assessment' and Status__c = 'Not Started'")['Id'])[0]
            data = {
                "Status__c": "Started",
                "Personnel_Assigned_To__c": "0035b00002bDUNvAAO"
            }
            self.salesforce_api.Update("Action_Item__c", data, action_item)
            self.logger.info('Action Item Set Started')
            return True
        except:
            return False

    def set_action_item_finish(self, opportunity_id) -> None:
        try:
            action_item = list(self.salesforce_api.Select(f"Select Id from Action_Item__c where Opportunity__c = '{opportunity_id}' and name = 'Remote Site Assessment' and Status__c = 'Started'")['Id'])[0]
            data = {
                "Status__c": "Completed",
                "Assigned_To__c": "00332000028B4gIAAS",
                "Notes__c": "RPA RSA Bot",
            }
            self.salesforce_api.Update("Action_Item__c", data, action_item)
            self.logger.info('Action Item Set Finished')
            return True
        except:
            return False

    def reset_action_item(self, opportunity_id) -> None:
        """
        Reset action item to not started and removed assigned to fields
        """
        try:
            action_item = list(self.salesforce_api.Select(f"Select Id from Action_Item__c where Opportunity__c = '{opportunity_id}' and name = 'Remote Site Assessment' and Status__c = 'Started'")['Id'])[0]
            data = {
                "Status__c": "Not Started",
                "Assigned_To__c": "00332000022uLYnAAM",
                "Personnel_Assigned_To__c": None,
            }
            self.salesforce_api.Update("Action_Item__c", data, action_item)
            self.logger.info('Action Item Reset')
            return True
        except:
            return False

    def check_action_item_started(self, opportunity_id) -> None:
        """
        Checks if action item is set to started
        """
        try:
            status_list = list(self.salesforce_api.Select(f"Select Status__c from Action_Item__c where Opportunity__c = '{opportunity_id}' and name = 'Remote Site Assessment'")['Status__c'])
            for status in status_list:
                if status == 'Not Started':
                    return False
            return True
        except:
            return True

    def complete_opportunity(self, opportunity_id) -> None:
        """
        Closes the opportunity action item and adds it to the completed log.
        """
        self.set_action_item_finish(opportunity_id)
        self.logger.complete(opportunity_id)
        # self.autobot_api.post_genesis_finalize_task(opportunity_id)

    def transfer_roof_objects(self, opportunity_id) -> None:
        """
        Calls Power Automate to copy roof data to the Genesis_Production object in staging.
        """
        self.logger.info('Updating Salesforce Roof Objects...')

        System_Size_kWdc__c = list(self.salesforce_api.Select(f"Select System_Size_kWdc__c from Opportunity where Id = '{opportunity_id}'")['System_Size_kWdc__c'])[0]
        roof = self.salesforce_api.Select(f"Select Actual_Production_PVWatts__c, PVWatts_Production_Utility__c, Module_Type__c, Number_of_Modules__c, Production_Multiplier__c, Name, Shade__c, TSRF__c from Roofs__c where Opportunity__c = '{opportunity_id}'")
        Actual_Production_PVWatts__c = list(roof['Actual_Production_PVWatts__c'])
        PVWatts_Production_Utility__c = list(roof['PVWatts_Production_Utility__c'])
        Module_Type__c = list(roof['Module_Type__c'])
        Number_of_Modules__c = list(roof['Number_of_Modules__c'])
        Production_Multiplier__c = list(roof['Production_Multiplier__c'])
        Name = list(roof['Name'])
        Shade__c = list(roof['Shade__c'])
        TSRF__c = list(roof['TSRF__c'])
        for counter, roof_name in enumerate(Name):
            data = {
                "OwnerId": "005320000054f0tAAA",
                "Actual_Production_PVWatts__c": Actual_Production_PVWatts__c[counter],
                "Default_Production_PVWatts__c": PVWatts_Production_Utility__c[counter],
                "Module_Type__c": Module_Type__c[counter],
                "Number_Of_Modules__c": Number_of_Modules__c[counter],
                "Opportunity_ID__c": opportunity_id,
                "Production_Multiplier__c": Production_Multiplier__c[counter],
                "Roof_Name__c": roof_name,
                "Shade__c": Shade__c[counter],
                "TSRF__c": TSRF__c[counter],
                "System_Size__c": System_Size_kWdc__c
            }
            self.salesforce_api.Create("Genesis_Production__c", data)

        self.logger.info('Updated Salesforce Roof Objects...')

    def download_skp(self, opportunity_id) -> str:
        """
        Downloads a SKP file for sketchup for the given opportunity id.
        Uses the Box API. Returns the file path or an empty
        string if file could not be downloaded.
        """
        # Get Home Folder
        home_folder_id = self.box_api.get_opp_folder_id(opportunity_id)
        if not home_folder_id:
            return ""
        # Get "Site Info-Designs" folder id
        BoxValidate(f'Box Request items - GenesisFinalizer {opportunity_id} - site_info_designs_folder_id')
        site_info_designs_folder_id = self.box_api.get_folder_id_from_parent(
            home_folder_id, "Site Info-Designs")
        if not site_info_designs_folder_id:
            return ""
        # Get "Site Info Documents" folder id
        BoxValidate(f'Box Request items - GenesisFinalizer {opportunity_id} - site_info_documents_folder_id')
        site_info_documents_folder_id = self.box_api.get_folder_id_from_parent(
            site_info_designs_folder_id, "Site Info Documents")
        if not site_info_documents_folder_id:
            return ""
        self.current_box_folder_id = site_info_documents_folder_id
        # Get files in that folder
        BoxValidate(f'Box Request items - GenesisFinalizer {opportunity_id} - site_info_document_files')
        res = self.box_api.request_items_in_folder(
            site_info_documents_folder_id).json()
        files = res['entries']
        found_file_id = None
        found_file_name = None
        for file in files:
            file_name = file['name']
            #if ".skp" in file_name and "GENESIS" in file_name:
            if ".skp" in file_name and "AUR_GENESIS" in file_name:
                found_file_id = file['id']
                found_file_name = file_name
        if not found_file_id:
            return ""
        # Download Genesis file
        dst_path = os.path.join(os.getcwd(), "temp", found_file_name)
        if os.path.exists(dst_path):  # Delete old versions
            os.remove(dst_path)
        BoxValidate(f'Box Request Download File - GenesisFinalizer {opportunity_id} - site_info_document_file')
        response = self.box_api.request_download_file(found_file_id)
        with open(dst_path, 'wb') as f:
            f.write(response.content)
            f.close()
        return dst_path

    def finalize_genesis(self, file_path,
                         module_name,
                         has_street_side_pathways=False,
                         secondary_job=False) -> bool:
        """
        Opens Genesis/Sketchup and finalizes the design.
        click_input has to be used over click
        """
        try:
            self.logger.info(f"Finalizing for {file_path}")
            skp_file_name = os.path.basename(file_path)
             #app = Application(backend="uia").start(
              #   f'SketchUp.exe "{file_path}"')            
            SketchPath = r"C:/Program Files/SketchUp/SketchUp 2022/SketchUp.exe"            
            app = Application(backend="uia").start(f'"{SketchPath}" "{file_path}"')           
            main_dlg = app[skp_file_name]
            self.logger.info('Waiting for window visibility...')
            main_dlg.wait('visible', timeout=90)
            # Handle Don't Panic Window
            time.sleep(5)
            try:
                panic_dlg = main_dlg.child_window(title="Don't Panic!")
                panic_dlg.FixNow.click_input()
                self.logger.info("Handled panic popup...")
                time.sleep(10)
            except Exception:
                self.logger.info("No panic popup found...")
 #       try:
#          self.logger.info(f"Finalizing for {file_path}")
#            skp_file_name = os.path.basename(file_path)
 #           app = Application(backend="uia").start(
 #               f'SketchUp.exe "{file_path}"')
 #           main_dlg = app[skp_file_name]
 #           self.logger.info('Waiting for window visibility...')
  #          main_dlg.wait('visible', timeout=30)
   #         # Handle Don't Panic Window
    #        time.sleep(5)
   #         try:
   #             panic_dlg = main_dlg.child_window(title="Don't Panic!")
   #             panic_dlg.FixNow.click_input()
   #             self.logger.info("Handled panic popup...")
    #            time.sleep(10)
    #        except Exception:
     #           self.logger.info("No panic popup found...")

            # Hand Update Popup
            try:
                update_dlg = main_dlg.child_window(
                    title="SketchUp Update Service")
                update_dlg.RemindMeLater.click_input()
                self.logger.info("Handled update popup...")
                time.sleep(10)
            except Exception as e:
                self.logger.info("No update popup found...")

            self.logger.info('Opening Salesforce Login')
            main_dlg.Genesis.Button1.click_input()
            sf_dlg = main_dlg.child_window(title="Salesforce Login")
            self.logger.info('Waiting for Salesforce Login visibility...')
            sf_dlg.wait('visible', timeout=60)
           
            try:
                #login_portal = sf_dlg.child_window(title='Log in with AzureADSSOPREPRODButton') 
                login_portal = "Microsoft"
                if login_portal == "AzureAD":
                    SketchUp_Salesforce_via_AzureAD(sf_dlg, self.logger)
                elif login_portal == "Okta":
                    SketchUp_Salesforce_via_Okta(sf_dlg, self.logger)
                elif login_portal == "Microsoft":
                    SketchUp_Salesforce_via_Microsoft(sf_dlg, self.logger)
            except:
                pass
                # self.logger.info('Inputting username...')
                # sf_dlg.UsernameEdit.type_keys(SALESFORCE_USERNAME)
                # self.logger.info('Inputting password...')
                # sf_dlg.PasswordEdit.type_keys(SALESFORCE_PASSWORD)
                # self.logger.info('Submitting...')
                # sf_dlg.Button.click_input()

            self.logger.info("Grabbing module window...")
            module_dlg = main_dlg.child_window(title="Pick a Module")
            module_dlg.wait('visible', timeout=60)
            self.logger.info(
                f"Selecting genesis formatted module type {module_name}")
            time.sleep(1)
            module_dlg.ModuleTypeEdit.set_text(module_name)
            time.sleep(1)
            module_dlg.OK.click()
            try:
                self.logger.info("Checking for resizing panels...")
                panel_dlg = main_dlg.child_window(title="SketchUp")
                panel_dlg.Yes.click_input()
                # At this point resizing will take some time. We have to wait for another window named SketchUp.
                self.logger.info("Waiting for shade calculation...")
                counter = 0
                MAX_COUNT = 20
                TIMEOUT = 15
                self.logger.info(f"Max Wait {MAX_COUNT * TIMEOUT}")
                while counter < MAX_COUNT:
                    try:
                        confirmation_dlg = main_dlg.child_window(
                            title="SketchUp")
                        confirmation_dlg.wait('visible', timeout=TIMEOUT)
                        confirmation_dlg.OK.click_input()
                        break
                    except Exception:
                        time.sleep(1)
                        counter += 1
                        self.logger.info(f"Count {counter}")
            except Exception:
                pass

            # Ignore Pathways
            self.logger.info("Opening Panel Controls...")
            main_dlg.Genesis.Button2.click_input()  # Panel Wheel Button
            if has_street_side_pathways:
                self.logger.info("Setting Driveway Status...")
                counter = 0
                while counter < 30:
                    try:
                        driveway_dlg = main_dlg.child_window(
                            title="Site Driveway")
                        driveway_dlg.wait('visible', timeout=4)
                        driveway_dlg.Edit.set_text("No")
                        driveway_dlg.OK.click_input()
                        break
                    except Exception:
                        self.logger.info('No window found...')
                        time.sleep(1)
                        counter += 1
            # Wait for setback notes window to load
            counter = 0
            while counter < 30:
                try:
                    setback_dlg = main_dlg.child_window(title="Setback Notes")
                    setback_dlg.Close.click_input()
                    break
                except Exception:
                    self.logger.info(f'No notes window found ({counter})...')
                    counter += 1
                    time.sleep(5)

            self.logger.info("Ignoring Pathways...")
            main_dlg.right_click_input()
            ctx_dlg = app.Context
            ctx_dlg['Ignore Pathways'].click_input()

            self.logger.info("Clicking Finalize...")
            #main_dlg.Genesis.print_control_identifiers()
            main_dlg.Genesis.Button12.click_input()  # Finalize Button

            self.logger.info("Handling Shade Popup...")
            shade_dlg = app['Dialog']
            shade_dlg.OK.click_input()

            self.logger.info("Setting RSA Status and Finishing...")
            counter = 0
            while counter < 90:
                try:
                    if secondary_job:
                        main_dlg.Finalizing.UploadWebGenEdit.set_text("No")
                    main_dlg.Finalizing.OK.click_input()
                    break
                except Exception:
                    time.sleep(5)
                    counter += 1

            self.logger.info("Waiting for Finalizing Complete...")
            counter = 0
            MAX_COUNT = 20
            TIMEOUT = 15
            self.logger.info(f"Max Wait {MAX_COUNT * TIMEOUT} Seconds")
            while counter < MAX_COUNT:
                try:
                    complete_dlg = main_dlg.child_window(
                        title="SketchUp")
                    complete_dlg.wait('visible', timeout=TIMEOUT)
                    complete_dlg.OK.click_input()
                    break
                except Exception:
                    time.sleep(1)
                    counter += 1
                    self.logger.info(f"Count {counter}")
            if counter >= MAX_COUNT:
                self.logger.error("Unable to finalize...")
                app.kill()
                return False

            self.logger.info("Closing SketchUp")
            time.sleep(5)
            app.kill()
            return True
        except Exception as e:
            self.logger.error(e)
            app.kill()
            return False

    def run(self, report_type, updater=None, end=None):
        """
        Runs the Genesis finalizer using the specified report type.
        """

        print('*** Getting the Salesforce file downloaded')

        try:
            report_url = self.REPORT_TYPES[report_type]
            # print('*** Fetched the report type')
            opportunities = self.get_opportunities(report_url)
            print('*** Requesting Report via API')
            if not opportunities:
                return
            # Suffle opportunities so if multiple bots run, less chance of overlap
            random.shuffle(opportunities)
            self.logger.info(f'Opportunity Count: {len(opportunities)}')
            for opportunity in opportunities:
                success = self.run_opportunity(opportunity)
                if updater:
                    updater(f"Ran {opportunity} | Success: {success}", opportunity)
                if end and success:
                    end(opportunity)
        except Exception as e:
            self.logger.error(e)
            return False

    def run_opportunity(self, opportunity_id) -> bool:
        """
        Runs the genesis finalizer for a single opportunity.
        """
        try:
            if self.check_action_item_started(opportunity_id):
                self.logger.info(f'Action item already started...')
                return False
            self.logger.info(f"Downloading skp for {opportunity_id}")
            skp_path = self.download_skp(opportunity_id)
            if not skp_path:
                self.logger.info(f'Could not find skp file...')
                return False
            self.logger.info(f'Found skp file {skp_path}')
            self.logger.info('Setting AI Started')
            self.set_action_item_start(opportunity_id)
            self.logger.info("Checking driveway status...")
            has_street_side_pathways = self.has_street_side_pathways(
                opportunity_id)
            if self.RERUN:
                self.finalize_genesis(skp_path,
                                      module_name=self.DEFAULT_RERUN_MODULE,
                                      has_street_side_pathways=has_street_side_pathways,
                                      secondary_job=False)
                self.transfer_roof_objects(opportunity_id)
            state_code = skp_path[-6:-4].lower()
            module_name = self.DEFAULT_STATE_MODULES[state_code]
            finalize_success = self.finalize_genesis(skp_path,
                                                     module_name=module_name,
                                                     has_street_side_pathways=has_street_side_pathways,
                                                     secondary_job=False)
            self.wait_for_file_delete(skp_path)
            if finalize_success:
                self.logger.info(f"Finalized {opportunity_id}")
                self.transfer_roof_objects(opportunity_id)
                self.complete_opportunity(opportunity_id)
                return True
            else:
                self.logger.info(f"Failed {opportunity_id}")
                self.reset_action_item(opportunity_id)
                return False

        except Exception as e:
            self.wait_for_file_delete(skp_path)
            self.logger.info("Encountered Exception:")
            self.logger.info(e)
            return False

    def wait_for_file_delete(self, file_path) -> None:
        """
        Tries to delete file with a small time buffer that
        catches any issues.
        """
        counter = 0
        while os.path.exists(file_path):
            if counter >= 10:
                return
            try:
                os.remove(file_path)
                return
            except Exception:
                time.sleep(5)
                counter += 1

    def add_suffix_most_recent_skp_and_report(self, opportunity_id, suffix):
        """
        Finds the most recent skp file in an opportunity and adds a suffix to the file name.
        """
        opp_folder_id = self.box_api.get_box_folder_id(opportunity_id)
        # get Site Info-Designs folder
        designs_folder_id = self.box_api.get_folder_id_from_parent(
            opp_folder_id, 'Site Info-Designs')
        # get Site Info Documents folder
        documents_folder_id = self.box_api.get_folder_id_from_parent(
            designs_folder_id, 'Site Info Documents')
        folder_data = self.box_api.request_folder_info(
            documents_folder_id).json()
        files_data = folder_data['item_collection']['entries']
        found_files = {}
        for file_data in files_data:
            file_name = file_data['name']
            if '340' not in file_name and '380' not in file_name:
                if '.skp' in file_name:
                    found_files[file_data['id']] = file_name
                if 'GENESIS SITE REPORT' in file_name:
                    found_files[file_data['id']] = file_name
        if not found_files:
            return
        for file_id in found_files:
            file_name = found_files[file_id]
            name_parts = file_name.split('.')
            new_name = f"{'.'.join(name_parts[:-1])}{suffix}.{name_parts[-1]}"
            self.logger.info(f'Renaming {file_name} to {new_name}')
            res = self.box_api.request_rename_file(file_id, new_name)
            self.logger.info(res.status_code)


class SecondaryGenesisFinalizer(GenesisFinalizer):
    """
    A Genesis finalizer for running test panels for data purposes. Will saves to Box with 
    file name suffix based on panel wattage. Does not update Web Gen or action items.
    """

    DEFAULT_MODULE = '400:Hanwha - Q.PEAK DUO BLK ML-G10 400'

    def __init__(self, module_name) -> None:
        super().__init__()
        self.module_name = module_name
        self.logger.info(f'Initialized for module: {module_name}')

    def run(self, updater=None):
        """
        Runs the opportunities in the API queue.
        """
        try:
            # opps = self.autobot_api.get_genesis_finalize_tasks(
                # module_name=self.module_name, completed=False)
            self.logger.info(opps)
            for opp in opps:
                success = self.run_opportunity(opp)
                # if success:
                    # self.autobot_api.complete_genesis_finalize_task(
                        # opp, self.module_name)
                if updater:
                    updater(f"Ran {opp} Success: {success}")

        except Exception as e:
            self.logger.error(e)
            return False

    def run_opportunity(self, opportunity_id, transfer_roofs=True) -> bool:
        """
        Runs the genesis finalizer for a single opportunity.
        """
        try:
            skp_path = self.download_skp(opportunity_id)
            if not skp_path:
                self.logger.info(f'Could not find skp file...')
                return False
            self.logger.info(f'Downloaded skp file to {skp_path}')
            self.logger.info("Checking driveway status...")
            has_street_side_pathways = self.has_street_side_pathways(
                opportunity_id)

            finalize_success = self.finalize_genesis(skp_path,
                                                     module_name=self.module_name,
                                                     has_street_side_pathways=has_street_side_pathways,
                                                     secondary_job=True)
            self.wait_for_file_delete(skp_path)
            if not finalize_success:
                return False
            if transfer_roofs:
                self.transfer_roof_objects(opportunity_id)
            return True

        except Exception as e:
            self.logger.info("Encountered Exception:")
            self.logger.info(e)
            return False


class RerunGenesisFinalizer(GenesisFinalizer):
    """
    Runs an opportunity with a specific panel, 
    transfers the roof information in Salesforce, 
    then reruns with the original panels.
    """

    REPORT_URL = r'https://trinity-solar.lightning.force.com/lightning/r/Report/00O5b000005iewu/view'
    DEFAULT_RERUN_MODULE = r'400:Hanwha - Q.PEAK DUO BLK ML-G10 400'

    def __init__(self) -> None:
        super().__init__()

    def run(self, module_name=None, fix=True):
        """
        Runs the Genesis finalizer using the specified report type.
        """
        try:
            if not module_name:
                rerun_module = self.DEFAULT_RERUN_MODULE
            opportunities = self.get_opportunities(self.REPORT_URL)
            if not opportunities:
                return
            random.shuffle(opportunities)
            self.logger.info(f'Opportunity Count: {len(opportunities)}')
            for opportunity in opportunities:
                if fix:
                    # Run default
                    self.run_opportunity(opportunity, rerun_module)
                # Run 340
                self.run_opportunity(opportunity, self.DEFAULT_MODULE)

        except Exception as e:
            self.logger.error(e)
            return False

    def run_opportunity(self, opportunity_id, module_name) -> bool:
        """
        Runs a genesis finalizer without modifying any action items.
        """
        try:
            self.logger.info(f"Downloading skp for {opportunity_id}")
            skp_path = self.download_skp(opportunity_id)
            if not skp_path:
                self.logger.info(f'Could not find skp file...')
                return False
            self.logger.info(f'Found skp file {skp_path}')
            self.logger.info("Checking driveway status...")
            has_street_side_pathways = self.has_street_side_pathways(
                opportunity_id)
            finalize_success = self.finalize_genesis(skp_path,
                                                     module_name=module_name,
                                                     has_street_side_pathways=has_street_side_pathways,
                                                     secondary_job=False)
            self.wait_for_file_delete(skp_path)
            if finalize_success:
                self.logger.info(f"Finalized {opportunity_id}")
                self.transfer_roof_objects(opportunity_id)
                return True
            else:
                self.logger.info(f"Failed {opportunity_id}")
                return False

        except Exception as e:
            self.logger.info("Encountered Exception:")
            self.logger.info(e)
            return False
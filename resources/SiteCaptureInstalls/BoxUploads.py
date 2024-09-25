import sys
import os
import time
import requests
from customlogging import logger
import aspose.pdf as pdf
# from resources.ContractCreation.config import usage_url, task_url, requested_ai_url, folder_id_url, COMPLETE_CC_AI_URL
from Sitecapture_Project_Creation import SiteCaptureProjectCreation
sys.path.append(os.environ['autobot_modules'])
from Box.BoxAPI import BoxAPI


class BoxUploads:
    def __init__(self, bot_name=None):
        self.bot_name = bot_name
        self.updater = SiteCaptureProjectCreation()
        #self.salesforce = SalesforcePortal()
        #self.sunnova = SunnovaPortal()
        while True:
            try:
                self.box_api = BoxAPI(application="Sitecapture")
                break
            except Exception as e:
                print(f"Encountered an Exception.. {e}")
                logger.info("Sleeping for 5 seconds and retrying")
                time.sleep(5)

        self.SharepointConnection = self.updater.sharepoint

    
    def run_sitecapture_task(self, opportunity_id, project_id, name):
        """
        Runs a task to download and upload site capture photos to box.
        get_installation_documents_folder_id
        """
        # logger.info('Site Capture photo upload...')
        # post_count = 0
        # finished_ids = []
        # self.updater = SiteCaptureProjectCreation() #reinit to make a new process value
        # self.updater.register_bot(self.bot_name, logs=f"In Queue:{len(opportunity_ids)}")
        # for counter, opportunity_id in enumerate(opportunity_ids):
        self.updater.update_status("Sitecapture_Installs_Creation") #updates creation so it doesnt stall for too long
        self.updater.update_bot_status(bot_name=self.bot_name, status="Uploading", identifier=opportunity_id)
#             opp_folder_id = get_folder_id_from_opportunity_id(opportunity_id)
        opp_folder_id = self.box_api.get_opp_folder_id(opportunity_id)
        quit_count = 0
        
        while True:
            try:
                self.create_box_folder_structure(opp_folder_id)
                break
            except:
                quit_count += 1
                time.sleep(3)
                print("Failed to create folder structure")
                if quit_count == 10:
                    print("Failed to create Box Folder 10 times, passing... FILES WILL END UP IN MAIN FOLDER")
                    break
        # current_id = project_id
        project_id = int(project_id)
        try:
            print("Searching for Project")
            self.SharepointConnection.find_pictures(project_id)
            print("Found Project")
            self.updater.update_bot_status(bot_name=self.bot_name, status="Finding Report", identifier=opportunity_id)

            self.SharepointConnection.find_report(project_id, name)

            pictures_path = self.SharepointConnection.get_pictures_path()

            success = self.upload_files_in_folder_to_installation(pictures_path, opp_folder_id, opportunity_id)
            if success:
                # finished_ids.append(project_id)
                self.updater.complete_opportunity(self.bot_name, opportunity_id)
                # post_count += 1
            else:
                self.updater.update_bot_status(bot_name=self.bot_name, status="Failed to Get Box Folder IDs", identifier=opportunity_id)                
            
        except Exception as e:
            print(f"Error, Skipping {e}")
            pass
            # self.upload_file_to_applications(bill_pdf_path, opp_folder_id)
            # sitecapture_task.completed = True
            # self.task_manager.commit()
        self.updater.edit_end()
        return success

    def run_sitecapture_job_photos(self, opportunity_id, project_ids):
        for counter, dl in enumerate(dls):
            opp_folder_id = get_folder_id_from_opportunity_id(opportunity_id)
            self.create_box_folder_structure(opp_folder_id)
            self.SharepointConnection.find_pictures(project_ids[counter])
            self.SharepointConnection.find_report(project_ids[counter])
            pictures_path = self.SharepointConnection.get_pictures_path()
            self.upload_files_in_folder_to_sales(pictures_path, opp_folder_id)

        return None
    def create_box_folder_structure(self, box_opportunity_folder_id):
        # while True:
        #     try:
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
        logger.info('Checking box folder structure')
        # BoxValidate(f'Box Request items - Transfer SiteCapture photos {box_opportunity_folder_id} - Create Box folder structure')
        items_res = self.box_api.request_items_in_folder(
            box_opportunity_folder_id)
        if items_res:
            items = items_res.json()['entries']
            for item in items:
                existing_folders.append(item['name'])

        for folder in EXPECTED_FOLDERS:
            if folder not in existing_folders:
                logger.info(f'Could not find {folder}, creating folder...')
                # BoxValidate(f'Box Create Folder - Transfer SiteCapture photos {box_opportunity_folder_id} - Create Box folder structure')
                self.box_api.create_folder(folder, box_opportunity_folder_id)
                if folder == "Job Photos":
                    job_photo_id = self.box_api.get_job_photos_folder_id(box_opportunity_folder_id)
                    self.box_api.create_folder("Installation", job_photo_id)
            # except:
            #     print("Retrying Box folder structure")
            #     time.sleep(5)

    def upload_files_in_folder_to_installation(self, folder_path, opportunity_folder_id, opportunity_id):
        logger.info('Uploading Sales docs...')
        quit_counter = 0
        while True:
            try:
                # BoxValidate(f'Box Request items - Transfer SiteCapture photos {opportunity_folder_id} - get_job_photos_folder_id')
                installation_folder_id = self.box_api.get_installation_from_folder_id(
                    opportunity_folder_id)
                install_documents_folder_id = self.box_api.get_installation_documents_folder_id(opportunity_folder_id)
                if not installation_folder_id or not install_documents_folder_id:
                    print("Did not grab both folder ids, sleeping and retrying")
                    quit_counter += 1
                    if quit_counter == 6:
                        return False
                    time.sleep(5)
                else:
                    break
            except Exception as e:
                print(e)
                job_photo_id = self.box_api.get_job_photos_folder_id(opportunity_folder_id)
                self.box_api.create_folder("Installation", job_photo_id)
                print(f"Trying to grab install folder with")# {opportunity_folder_id}")
                time.sleep(5)
        #print(installation_folder_id)
        # Create subfolder
        # subfolder_name = os.path.basename(folder_path)
        # # BoxValidate(f'Box Request items - Transfer SiteCapture photos {sales_folder_id} - Create Subfolder')
        # subfolder_id = self.box_api.create_folder(
        #     subfolder_name, sales_folder_id)
        # print(subfolder_id)
        # if not subfolder_id:
        #     subfolder_id = sales_folder_id
        files = os.listdir(folder_path)
        ground_files = []
        for file_name in files:
            # print(file_name)
            full_path = os.path.join(folder_path, file_name)
            upload_quit_counter = 0
            if "Installation Report" in file_name:
                try:
                    file_id = None
                    items = self.box_api.request_items_in_folder(install_documents_folder_id)
                    # print(items.json())
                    for item in items.json()['entries']:
                        if "Installation Report" in item['name']:
                            file_id = item['id']
                            #print(item)
                            #print(file_id)
                            break
                    if file_id:
                        self.box_api.request_upload_new_file_version(file_id, full_path, install_documents_folder_id)
                        #print(f"Uploaded New Version for : {full_path}")
                        time.sleep(5)
                        os.remove(full_path)
                        continue
                except Exception as e:
                    print(f"Failed to find old installation id {e}")
                    file_id = None
                    pass
                logger.info("Uploading pictures...")
                while True:
                    try:
                        self.box_api.request_upload_file(full_path, install_documents_folder_id)
                        #print(f"Uploaded {full_path}")

                        time.sleep(5)
                        if "Completed_Array_from_Ground" in full_path:
                            ground_files.append(full_path)


                        try:
                            os.remove(full_path)
                        except:
                            pass
                        break
                    except Exception as e:
                        print(e)
                        upload_quit_counter += 1
                        if upload_quit_counter == 5:
                            print(f"Passing upload for {full_path}")
                            break
                        time.sleep(5)
                logger.info("Finished Uploading pictures...")
                    
                continue
            # print(full_path)
            # BoxValidate(f'Box Upload File - Transfer SiteCapture photos {subfolder_id} - Uploading Sales docs')
            pdfFileEditor = pdf.facades.PdfFileEditor()
            completed_ground_photo_merged = pdfFileEditor.concatenate(ground_files, fr"{folder_path}\{opportunity_id}.pdf")
            
            try:
                self.box_api.request_upload_file(fr"{folder_path}\{opportunity_id}.pdf", "255951256132")
                time.sleep(5)
                os.remove(fr"{folder_path}\{opportunity_id}.pdf")
            except Exception as e:
                print(e)
                print("could not upload box image to marketo file")


            while True:
                try:
                    success = self.box_api.request_upload_file(full_path, installation_folder_id)
                    break
                except:
                    time.sleep(5)
            try:
                os.remove(full_path)
            except:
                pass
            if success:
                print(f"Uploaded Installation report")
                continue
                # logger.info(f'Uploaded {full_path} to Installation folder...')
            else:
                # logger.error(
                    print(
                    f'Failed to upload Installation report to Installation folder...')
        return True

    def upload_files_in_folder_to_sales(self, folder_path, opportunity_folder_id):
        logger.info('Uploading Sales docs...')
        # BoxValidate(f'Box Request items - Transfer SiteCapture photos {opportunity_folder_id} - get_job_photos_folder_id')
        sales_folder_id = self.box_api.get_sales_folder_id_from_opportunity_folder(
            opportunity_folder_id)
        # print(sales_folder_id)
        # Create subfolder
        subfolder_name = os.path.basename(folder_path)
        # BoxValidate(f'Box Request items - Transfer SiteCapture photos {sales_folder_id} - Create Subfolder')
        subfolder_id = self.box_api.create_folder(
            subfolder_name, sales_folder_id)
        # print(subfolder_id)
        if not subfolder_id:
            subfolder_id = sales_folder_id
        files = os.listdir(folder_path)
        for file_name in files:
            # print(file_name)
            full_path = os.path.join(folder_path, file_name)
            # print(full_path)
            # BoxValidate(f'Box Upload File - Transfer SiteCapture photos {subfolder_id} - Uploading Sales docs')
            success = self.box_api.request_upload_file(full_path, subfolder_id)
            try:
                os.remove(full_path)
            except:
                pass
            if success:
                logger.info(f'Uploaded {full_path} to Sales folder...')
            else:
                logger.error(
                    f'Failed to upload {full_path} to Sales folder...')

    def upload_file_to_applications(self, file_path, opportunity_folder_id):
        logger.info('Uploading Applications docs...')
        success = self.box_api.upload_file_to_applications_folder(
            opportunity_folder_id, file_path)
        if success:
            logger.info(f'Uploaded {file_path} to Applications folder...')
        else:
            logger.error(
                f'Failed to upload {file_path} to Applications folder...')

if __name__ == "__main__":
    pass

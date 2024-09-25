from resources.customlogging import logger
import os
import io
import zipfile
import base64
import datetime
import time
import requests
from resources.Salesforce.utilities import get_opportunity_info
from resources.queues.ContractCreationQueue import ContractCreationQueue
from resources.Box.BoxAPI import BoxAPI
from resources.BotUpdate.Update import update_bot_status, add_bot_history
from resources.Files.FileHandler import FileHandler
from resources.Salesforce.SalesforcePortal import SalesforcePortal
# from resources.Dropbox.DropboxAPI import DropboxAPI
from resources.ContractCreation.SunnovaParser import get_generated_quote_details
from resources.ContractCreation.Contract import Contract
from resources.AutobotEmail.Email import Email
from resources.AutobotEmail.Outlook import Outlook
from resources.Sunnova.SunnovaPortal import SunnovaPortal
from resources.SiteCapture.SiteCaptureAPI import SiteCaptureAPI
from resources.SiteCapture.SiteCapturePortal import SiteCapturePortal
from resources.ContractCreation.config import usage_url, task_url, requested_ai_url, folder_id_url, COMPLETE_CC_AI_URL
from api.box.BoxCallValidate import BoxValidate

# This is from before all bots were run through run_bot.py
try:
    from models.alchemy_contract_creation_models import GenesisRoof, session, Inverter
except ImportError:
    pass

def get_folder_id_from_opportunity_id(opportunity_id):
    content = {'opp_id': opportunity_id}
    logger.info('Requesting DL Opportunity Folder ID')
    try:
        response = requests.post(folder_id_url, json=content)
        logger.info(f'Received response: {response.status_code}')
        response_dict = response.json()
        folder_id = response_dict['folder_id']
        if folder_id:
            logger.info('Got folder id...')
            return folder_id
        else:
            logger.info('Unable to retrieve folder id...')
            logger.info(response.text)
            return None
    except Exception as e:
        logger.error('Unable to retrieve folder id...')
        logger.error(e)
        return None


def set_quote_details(quote, details, finalize=False):
    try:
        quote.solarRate = details['price']
        quote.systemSize = details['system_size']
        quote.monthlySunnovaPayment = details['monthly_sunnova_payment']
        quote.estimatedProduction = details['estimated_production']
        quote.newUtilityBill = details['new_utility_bill']
        quote.totalMonthlyElectrityCost = details['total_monthly_electric_cost']
        quote.utilityRate = details['utility_rate']
        quote.yearOneSavings = details['year_one_savings']
        quote.savingsOverTermLength = details['savings_over_term_length']
        quote.lifetimePayment = details['lifetime_payment']
        quote.pricePerWatt = details['price_per_watt']
        quote.totalEpc = details['total_epc']
        quote.valid = True
        quote.generated = True
        if finalize:
            quote.finalized = True
            quote.contractId = details['contract_id']
        if not quote.financingType:
            quote.financingType = quote.opportunity.purchaseMethod
    except:
        quote.valid = False
        quote.generated = True
    finally:
        session.commit()


class ContractCreator:
    def __init__(self, bot_name, task_manager):
        self.bot_name = bot_name
        self.salesforce = SalesforcePortal()
        self.sunnova = SunnovaPortal()
        self.box_api = BoxAPI(application=bot_name)
        self.sitecapture = SiteCapturePortal()
        self.sitecapture_api = SiteCaptureAPI()
        self.outlook = Outlook()
        # self.dropbox_api = DropboxAPI()
        self.file_handler = FileHandler()
        self.queue = ContractCreationQueue()
        self.task_manager = task_manager
        logger.info(f'Initialized as {self.bot_name} ...')

    def run_task(self, opp_id, function, bot_status):
        #function = task['function']
        #data = task['data']
        success = False
        if function == 'quote':
            self.run_quote_task(opp_id)
        elif function == 'preliminary':
            success = self.run_preliminary_tasks(opp_id, bot_status)
        elif function == 'non_sunnova_preliminary':
            success = self.run_preliminary_tasks(opp_id, bot_status, sunnova=False)
        logger.info('10 Second Wait')
        time.sleep(10)
        return success

    def run_create_design_task(self, create_design_task):
        """
        NEW Creates new system design, then creates a quote for that system design.
        """
        logger.info('Creating design...')
        self.update_status("Creating design...")
        sunnova_response = self.sunnova.generate_design_and_quote(
            create_design_task)
        if sunnova_response.error:
            if sunnova_response.status == 'invalid_quote':
                create_design_task.genesisDesign.sunnovaQuotes[0].generated = True
                create_design_task.completed = True
            create_design_task.genesisDesign.sunnovaQuotes[0].status = sunnova_response.error
            self.task_manager.commit()
            return False
        quote_details_list = sunnova_response.data['quote_details']
        quote_details = get_generated_quote_details(quote_details_list)
        set_quote_details(
            create_design_task.genesisDesign.sunnovaQuotes[0], quote_details)
        create_design_task.completed = True
        session.commit()
        return True

    def run_generate_quote_task(self, generate_quote_task):
        """
        NEW
        """
        logger.info('Generating Quote...')
        self.update_status("Generating quote...")
        sunnova_response = self.sunnova.generate_quote(generate_quote_task)
        if sunnova_response.error:
            generate_quote_task.status = sunnova_response.error
            if sunnova_response.status == 'invalid_quote':
                generate_quote_task.generated = True
                generate_quote_task.valid = False
            self.task_manager.commit()
            return False
        quote_details = get_generated_quote_details(
            sunnova_response.data['quote_details'])
        set_quote_details(generate_quote_task, quote_details)
        generate_quote_task.status = "Completed Quote"
        self.task_manager.commit()
        return True

    def run_finalize_quote_task(self, finalize_quote_task, url=None, multiple_options=False):
        """
        NEW
        """
        logger.info('Finalizing Quote...')
        self.update_status("Finalizing quote...")
        generate_quote_task = finalize_quote_task.sunnovaQuote
        if url:
            sunnova_response = self.sunnova.download_quote_from_url(
                finalize_quote_task.sunnovaUrl)
            if not sunnova_response:
                return False
            # Update Design
            self.update_finalize_only_design(
                sunnova_response.data['details'], finalize_quote_task)
            # Update inverters
            self.update_finalize_only_inverters(
                sunnova_response.data['details'], finalize_quote_task)
            details_joined = ''.join(sunnova_response.data['details'])
        else:
            sunnova_response = self.sunnova.generate_quote(
                generate_quote_task, finalize=True)
            if not sunnova_response:
                return False
            details_joined = sunnova_response.data['quote_details']
        if sunnova_response.error:
            generate_quote_task.status = sunnova_response.error
            self.task_manager.commit()
            return False
        quote_details = get_generated_quote_details(details_joined)
        contract_file_path = self.sitecapture.get_newest_path_in_folder(
            self.sunnova.download_folder)
        finalize_quote_task.sunnovaFinalized = True
        finalize_quote_task.contractDownloaded = True
        self.task_manager.commit()
        # Set quote details
        set_quote_details(generate_quote_task, quote_details, finalize=True)
        # Update opportunity in salesforce
        self.update_salesforce_with_quote(generate_quote_task)
        if multiple_options:
            logger.info(
                "Multiple options selected, creating new contract object...")
            self.create_salesforce_contract(generate_quote_task)
        else:
            logger.info("Updating salesforce first contract...")
            self.update_salesforce_contract(generate_quote_task)
        finalize_quote_task.salesforceUpdated = True
        self.task_manager.commit()
        # Generate Conga Packet
        combined_packet_path = self.salesforce.generate_conga_contract(
            generate_quote_task.genesisDesign.opportunity)
        if combined_packet_path:
            finalize_quote_task.combinedPacketDownloaded = True
        self.task_manager.commit()
        # Upload documents using dropbox api
        files = [contract_file_path, combined_packet_path]
        uploaded = self.upload_contract_files_to_dropbox(
            generate_quote_task.genesisDesign.opportunity, files)
        if uploaded:
            logger.info(f'Files successfully uploaded to dropbox...')
            finalize_quote_task.contractUploaded = True
            self.task_manager.commit()
        else:
            logger.warning(f'Files unsuccessfully uploaded to dropbox...')
        self.send_combined_packet_to_contract_user(
            finalize_quote_task, combined_packet_path)
        self.file_handler.delete_file(combined_packet_path)
        self.file_handler.delete_file(contract_file_path)
        # Send salesforce email
        if self.salesforce.send_contract_email(finalize_quote_task):
            finalize_quote_task.emailSent = True
        self.task_manager.commit()
        self.set_cc_ai_completed(
            generate_quote_task.genesisDesign.opportunity.salesforceId)
        add_bot_history(
            self.bot_name, generate_quote_task.genesisDesign.opportunity.opportunityName, finalize_quote_task.sunnovaUrl)
        return True

    def send_combined_packet_to_contract_user(self, finalize_task, cb_path) -> True:
        """
        Sends the combined packet to the sales ops user for back up.
        """
        try:
            email_body = f"https://trinity-solar.lightning.force.com/lightning/r/Opportunity/{finalize_task.sunnovaQuote.genesisDesign.opportunityId}/view\nPlease see attached file(s)."
            download_email = Email(subject=f"{finalize_task.sunnovaQuote.genesisDesign.opportunity.opportunityName} - Combined Packet",
                                   body=email_body)
            with open(cb_path, "rb") as cb:
                encoded_string = base64.b64encode(cb.read())
                file_content = encoded_string.decode('utf-8')
            download_email.add_attachment(
                file_content, name=os.path.basename(cb_path))
            download_email.add_recipient(
                finalize_task.sunnovaQuote.genesisDesign.userEmail)
            self.outlook.send_email(download_email)
        except Exception as e:
            logger.error("Failed to send combined packet to user...")
            logger.error(e)

    def update_finalize_only_design(self, details, finalize_only_task) -> None:
        """
        Updates the design with info from the sunnova portal.
            Parameters:
                details (list): A list of design and quote details from the sunnova portal, each are colon separated values.
                finalize_only_task (FinalizeSunnovaQuoteTask): A task with a sunnova url to a finalized quote.
        """
        design = finalize_only_task.sunnovaQuote.genesisDesign
        if design.roofs:
            return
        for index, item in enumerate(details):
            if "Module Quantity" in item:
                quantity = details[index].split(":")[-1]
                tilt = details[index + 2].split(":")[-1]
                azimuth = details[index + 3].split(":")[-1]
                availability = details[index + 4].split(":")[-1]
                roof = GenesisRoof(moduleQuantity=quantity,
                                   tilt=tilt,
                                   azimuth=azimuth,
                                   availability=availability,
                                   genesisSystemDesignId=design.id)
                session.add(roof)
        self.task_manager.commit()

    def update_finalize_only_inverters(self, details, finalize_only_task) -> None:
        """
        Updates the inverters with info from the sunnova portal.
            Parameters:
                details (list): A list of design and quote details from the sunnova portal, each are colon separated values.
                finalize_only_task (FinalizeSunnovaQuoteTask): A task with a sunnova url to a finalized quote.
        """
        design = finalize_only_task.sunnovaQuote.genesisDesign
        if design.inverters:
            return False
        for index, item in enumerate(details):
            if 'Inverter Model' in item:
                unformatted_model = item.split(':')[-1]
                # Check for Enphase
                if "SE" not in unformatted_model:
                    model = "Enphase IQ7-60-2-US"
                else:
                    model = unformatted_model.replace(
                        'xxx', '000').replace(' (Inverter)', '')
                count = int(details[index + 3].split(':')[-1])
                if count > 0:
                    new_inverter = Inverter(productCode=model,
                                            count=count,
                                            genesisSystemDesignId=finalize_only_task.sunnovaQuote.genesisDesign.id)
                    session.add(new_inverter)
        self.task_manager.commit()

    def update_salesforce_with_quote(self, quote):
        url = r'https://prod-122.westus.logic.azure.com:443/workflows/f8eae09471a147a9bb9da0b9d19b93d1/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=2hui8Qn9UkHCtvNFiNKXHhFalRdFdpUYXBBjftuU1Fk'
        data = self.get_salesforce_update_data(quote)
        requests.post(url, json=data)

    def update_salesforce_contract(self, quote):
        """
        Updates the first contract in salesforce with the quote data.
        """
        url = r'https://prod-48.westus.logic.azure.com:443/workflows/5646aa10831649ac999b73127628c2be/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=M-Zey9i589DRJ9qYYQS_Rk8fEuTowTYKEOa79c-j4u0'
        data = self.get_contract_update_json(quote)
        requests.post(url, json=data)

    def create_salesforce_contract(self, quote):
        """
        Creates a contract in salesforce with the quote data.
        """
        url = r'https://prod-98.westus.logic.azure.com:443/workflows/27f6c37d89334e9aa93c66965edee6a4/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=z9HSwddR-qsDmrWMu5WV0KzhBCaq2Vf7bg8O-rKLcJ8'
        data = self.get_contract_update_json(quote)
        requests.post(url, json=data)

    def get_salesforce_update_data(self, quote):
        template = {
            "opportunityId": "",  # Salesforce Opportunity ID as a string
            "loiRate": "",  # LOI Rate as a string ex. "0.179"
            "loiRateChangeReason": "",  # Reason from the dropdown
            "inverters": [
                {"productCode": "",  # Product Code from Salesforce
                 "count": ""},  # Number of inverters as a string
                {"productCode": "",
                 "count": ""},
                {"productCode": "",
                 "count": ""},
                {"productCode": "",
                 "count": ""}
            ],
            "installationType": [],  # Installation type taken from pick list
            "systemSize": "",  # System Size in mW ex. 6.12
            "contractId": "",  # Contract Id from sunnova quote
            "notes": "",  # Notes from salesops
            # Production from contract with no comma. Float or int ex. "5365.37"
            "contractProduction": "",
            "amount": "",  # Price of system with no comma. Float or int ex. "32322.98"
            "moduleQuantity": "",  # Total module quantity
            "permitPayer": "",
            "monthlyPayments": ""
        }
        template['opportunityId'] = quote.genesisDesign.opportunity.salesforceId
        template['loiRate'] = str(quote.solarRate).replace(',', '')
        template['loiRateChangeReason'] = quote.finalizeSunnovaQuoteTask.loiRateChangeReason
        template['monthlyPayments'] = quote.monthlySunnovaPayment

        total_modules = 0
        for roof in quote.genesisDesign.roofs:
            total_modules += roof.moduleQuantity
        # Inverters
        for index, inverter in enumerate(quote.genesisDesign.inverters):
            if total_modules < 8:
                inverter.productCode = "Enphase IQ7-60-2-US"
                session.commit()
                inverter.count = total_modules
            template['inverters'][index] = {
                "productCode": inverter.productCode, "count": str(inverter.count)}
        # Installation Type
        for installation_type in quote.finalizeSunnovaQuoteTask.installationType:
            template['installationType'].append(
                installation_type.installationType)
        template['systemSize'] = str(quote.systemSize)
        template['contractId'] = quote.contractId
        template['notes'] = quote.finalizeSunnovaQuoteTask.notes
        template['contractProduction'] = str(
            quote.estimatedProduction).replace(',', '')
        template['amount'] = str(quote.totalEpc).replace(',', '')
        template['moduleQuantity'] = str(total_modules)
        template['permitPayer'] = quote.finalizeSunnovaQuoteTask.permitPayer
        return template

    def get_contract_update_json(self, quote):
        data = self.get_salesforce_update_data(quote)
        formatted_data = {
            "opportunityId": data["opportunityId"],
            "loiRate": float(data["loiRate"]),
            "systemSize": float(data["systemSize"]),
            "contractId": data["contractId"],
            "amount": int(float(data["amount"])),
            "monthlyPayments": float(data["monthlyPayments"]),
            "contractProduction": int(float(data["contractProduction"]))
        }
        return formatted_data
      
    def run_preliminary_tasks(self, opp_id, bot_status, sunnova=True):
        """Downloads photos from sitecapture, uploads them to box. Gets utility bill usages and updates salesforce."""
        try:
            success = False
            #opp_id = data["oppID"]
            contract = Contract(opp_id)
            # print("set contract")
           # Check if already done
            logger.info(f"checking opportunity id for completion: {opp_id}")
            bot_status(f"Checking for completion in sitecapture, {contract.direct_lead}", opp_id)
            #update_bot_status(
            #    self.bot_name, f'Running preliminary tasks for {opp_id}')

            # Transfer photos from Sitecapture to Box

            #3/30 bug fixes, RPA-810
            success, message = self.transfer_opportunity_photos(contract)
            bot_status(message, opp_id)

            #3/30 bug fixes, RPA-810
            if not success:
                self.set_cc_ai_requested(opp_id)
                bot_status("Set AI to requested, created task", opp_id)
                return None
                # json = {
                # 'oppID': opp_id,
                # 'key': 951753
                # }
                # if sunnova:
                #     resp = False
                #     # resp = requests.post(url=SUNNOVA_URL, json=json)
                # else:
                #     resp = False
                    # resp = requests.post(url=CC_URL, json=json)
            # else:
            #     if sunnova:
            #          try:
            #              # Credit check and Title Verification
            #             logger.info('Checking Sunnova credit and title')
            #             self.sunnova.check_credit_and_verify_title(
            #                  contract)  # Tasks created inside
            #          except:
            #              logger.error(
            #                  'Error checking title and credit in sunnova...')

               # Set AI to requested
            self.set_cc_ai_requested(opp_id)
            bot_status("Set AI to requested", opp_id)
                #update_bot_status(self.bot_name, f'Standby')
                # Add file to history
                #data['name'] = contract.opportunity_name
                #data['completed_datetime'] = datetime.datetime.now().strftime(
                #    "%m/%d %H:%M")
               # self.queue.add_history(data)

            return True

        except Exception as e:
            logger.error(f'Error running sunnova preliminary task: {e}')
            logger.error(e)
        finally:
            #add_bot_history(self.bot_name, opp_id)
            return success

        # try:
        #     opp_id = data["oppID"]
        #     contract = Contract(opp_id)
        #     # Check if already done
        #     logger.info(f"checking opportunity id for completion: {opp_id}")
        #     update_bot_status(
        #         self.bot_name, f'Running preliminary tasks for {opp_id}')

        #     # Transfer photos from Sitecapture to Box
        #     self.transfer_opportunity_photos(contract)

        #     # if sunnova:
        #     #     try:
        #     #         # Credit check and Title Verification
        #     #         logger.info('Checking Sunnova credit and title')
        #     #         self.sunnova.check_credit_and_verify_title(
        #     #             contract)  # Tasks created inside
        #     #     except:
        #     #         logger.error(
        #     #             'Error checking title and credit in sunnova...')

        #     # Set AI to requested
        #     self.set_cc_ai_requested(opp_id)
        #     update_bot_status(self.bot_name, f'Standby')
        #     # Add file to history
        #     data['name'] = contract.opportunity_name
        #     data['completed_datetime'] = datetime.datetime.now().strftime(
        #         "%m/%d %H:%M")
        #     self.queue.add_history(data)

        #     return True
        # except Exception as e:
        #     logger.error(f'Error running sunnova preliminary task: {e}')
        #     logger.error(e)
        # finally:
        #     add_bot_history(self.bot_name, opp_id)

    def transfer_opportunity_photos(self, contract):
        """Searches sitecapture for photos and uploads them to the related opportunity in box."""
        # SiteCapture Download
        logger.info(f'Searching for project id for {contract.direct_lead}...')
        project_id = self.sitecapture_api.get_project_id(
            contract.direct_lead, contract.last_name, contract.street_address)
        if project_id:
            logger.info(f'Found project id {project_id}')
            pictures_path = os.path.join(
                os.getcwd(), f'./temp/{contract.opportunity_name} - LOI')
            logger.info('Getting project photos...')
            res = self.sitecapture_api.get_project_photos(project_id)
            if res.status_code == 200:
                logger.info('Found project photos, extracting data...')
                zipper = zipfile.ZipFile(io.BytesIO(res.content))
                zipper.extractall(pictures_path)
                logger.info('Extracted zip file...')
        else:
            logger.error(
                f'Could not find project id using {contract.direct_lead}, {contract.last_name}, {contract.street_address} ...')
            message = f'Could not find project id using {contract.direct_lead}, {contract.last_name}, {contract.street_address} ...'
            # self.create_salesforce_task('Could not locate DL in SiteCapture.',
            #                             contract.opportunity_id, 'Contract Creation: Unable to Locate Site Capture')
            return None, message
        # If no pictures in SiteCapture, zip extract produces no folder
        if not os.path.exists(pictures_path):
            # self.create_salesforce_task('Site Capture does not contain photos.',
            #                             contract.opportunity_id, 'Contract Creation: Missing All Photos')
            message = 'Site Capture does not contain photos.'

            return None, message
        if len(os.listdir(pictures_path)) == 0:
            # self.create_salesforce_task('Site Capture does not contain photos.',
            #                             contract.opportunity_id, 'Contract Creation: Missing All Photos')
            message = 'Site Capture does not contain photos.'
            
            return None, message

        logger.info('Site Capture photo uploads...')
        opp_folder_id = get_folder_id_from_opportunity_id(
            contract.opportunity_id)
        self.create_box_folder_structure(opp_folder_id)
        print(f"{pictures_path}, {opp_folder_id}")
        self.upload_files_in_folder_to_sales(pictures_path, opp_folder_id)


        # Electric Bill Conversion
        bill_paths = self.file_handler.get_bill_photo_paths(pictures_path)
        if not bill_paths:
            logger.info("Electric bill not found... moving on")
            # self.create_salesforce_task('No bill photos located in SiteCapture.',
            #                              contract.opportunity_id, 'Contract Creation: Missing Bill Photos')
            #return None
        else:
            bill_pdf_path = self.file_handler.convert_photos_to_pdf(bill_paths)
            for bill_path in bill_paths:
                self.file_handler.delete_file(bill_path)
            self.upload_file_to_applications(bill_pdf_path, opp_folder_id)
            self.file_handler.delete_file(bill_pdf_path)


        # Remove remaining files
        self.file_handler.delete_folder(pictures_path)
        message = "Success"
        return True, message
        # # SiteCapture Download
        # logger.info(f'Searching for project id for {contract.direct_lead}...')
        # project_id = self.sitecapture_api.get_project_id(
        #     contract.direct_lead, contract.last_name, contract.street_address)
        # if project_id:
        #     logger.info(f'Found project id {project_id}')
        #     pictures_path = os.path.join(
        #         os.getcwd(), f'./temp/{contract.opportunity_name} - LOI')
        #     logger.info('Getting project photos...')
        #     res = self.sitecapture_api.get_project_photos(project_id)
        #     if res.status_code == 200:
        #         logger.info('Found project photos, extracting data...')
        #         zipper = zipfile.ZipFile(io.BytesIO(res.content))
        #         zipper.extractall(pictures_path)
        #         logger.info('Extracted zip file...')
        # else:
        #     logger.error(
        #         f'Could not find project id using {contract.direct_lead}, {contract.last_name}, {contract.street_address} ...')
        #     self.create_salesforce_task('Could not locate DL in SiteCapture.',
        #                                 contract.opportunity_id, 'Contract Creation: Unable to Locate Site Capture')
        #     return None
        # # If no pictures in SiteCapture, zip extract produces no folder
        # if not os.path.exists(pictures_path):
        #     self.create_salesforce_task('Site Capture does not contain photos.',
        #                                 contract.opportunity_id, 'Contract Creation: Missing All Photos')
        #     return None
        # if len(os.listdir(pictures_path)) == 0:
        #     self.create_salesforce_task('Site Capture does not contain photos.',
        #                                 contract.opportunity_id, 'Contract Creation: Missing All Photos')
        #     return None

        # logger.info('Site Capture photo uploads...')
        # opp_folder_id = get_folder_id_from_opportunity_id(
        #     contract.opportunity_id)
        # self.create_box_folder_structure(opp_folder_id)
        # self.upload_files_in_folder_to_sales(pictures_path, opp_folder_id)

        # # Electric Bill Conversion
        # bill_paths = self.file_handler.get_bill_photo_paths(pictures_path)
        # if not bill_paths:
        #     # self.create_salesforce_task('No bill photos located in SiteCapture.',
        #     #                              contract.opportunity_id, 'Contract Creation: Missing Bill Photos')
        #     return None
        # else:
        #     bill_pdf_path = self.file_handler.convert_photos_to_pdf(bill_paths)
        #     for bill_path in bill_paths:
        #         self.file_handler.delete_file(bill_path)
        #     self.upload_file_to_applications(bill_pdf_path, opp_folder_id)

        # # Remove remaining files
        # self.file_handler.delete_file(bill_pdf_path)
        # self.file_handler.delete_folder(pictures_path)

    def run_sitecapture_task(self, sitecapture_task) -> bool:
        """
        Runs a task to download and upload site capture photos to box.
        """
        logger.info('Site Capture photo download...')
        if not sitecapture_task.directLead or not sitecapture_task.streetAddress or not sitecapture_task.lastName:
            # Get DL and Street Address
            opp_info = get_opportunity_info(sitecapture_task.opportunityId)
            sitecapture_task.directLead = opp_info['direct_lead']
            sitecapture_task.streetAddress = opp_info['street_address']
            sitecapture_task.lastName = opp_info['last_name']
            self.task_manager.commit()
        res = self.sitecapture.download_pictures(sitecapture_task)
        pictures_path = res.data['path']
        bill_paths = self.file_handler.get_bill_photo_paths(pictures_path)

        if not bill_paths:
            sitecapture_task.attempts += 1
            self.task_manager.commit()
            return False

        bill_pdf_path = self.file_handler.convert_photos_to_pdf(bill_paths)
        for bill_path in bill_paths:
            self.file_handler.delete_file(bill_path)

        opp_folder_id = get_folder_id_from_opportunity_id(
            sitecapture_task.opportunityId)
        self.create_box_folder_structure(opp_folder_id)
        self.upload_files_in_folder_to_sales(pictures_path, opp_folder_id)
        self.upload_file_to_applications(bill_pdf_path, opp_folder_id)
        sitecapture_task.completed = True
        self.task_manager.commit()
        return True

    def create_box_folder_structure(self, box_opportunity_folder_id):
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
        BoxValidate(f'Box Request items - Transfer SiteCapture photos {box_opportunity_folder_id} - Create Box folder structure')
        items_res = self.box_api.request_items_in_folder(
            box_opportunity_folder_id)
        if items_res:
            items = items_res.json()['entries']
            for item in items:
                existing_folders.append(item['name'])

        for folder in EXPECTED_FOLDERS:
            if folder not in existing_folders:
                logger.info(f'Could not find {folder}, creating folder...')
                BoxValidate(f'Box Create Folder - Transfer SiteCapture photos {box_opportunity_folder_id} - Create Box folder structure')
                self.box_api.create_folder(folder, box_opportunity_folder_id)

    def upload_files_in_folder_to_sales(self, folder_path, opportunity_folder_id):
        logger.info('Uploading Sales docs...')
        BoxValidate(f'Box Request items - Transfer SiteCapture photos {opportunity_folder_id} - get_job_photos_folder_id')
        sales_folder_id = self.box_api.get_sales_folder_id_from_opportunity_folder(
            opportunity_folder_id)
        # Create subfolder
        subfolder_name = os.path.basename(folder_path)
        print(f"{subfolder_name}, {sales_folder_id}")
        BoxValidate(f'Box Request items - Transfer SiteCapture photos {sales_folder_id} - Create Subfolder')
        #Tries to create folder, if already exists then get folder from parent id
        subfolder_id = self.box_api.create_folder(
                subfolder_name, sales_folder_id)
        # subfolder_id = self.box_api.get_folder_id_from_parent(sales_folder_id, "test")
        if not subfolder_id:
            subfolder_id = self.box_api.get_folder_id_from_parent(sales_folder_id, subfolder_name)
        # quit()
        print(f"{subfolder_id} created subfolder")
        # quit()
        files = os.listdir(folder_path)
        for file_name in files:
            full_path = os.path.join(folder_path, file_name)
            BoxValidate(f'Box Upload File - Transfer SiteCapture photos {subfolder_id} - Uploading Sales docs')
            success = self.box_api.request_upload_file(full_path, subfolder_id)
            if success:
                logger.info(f'Uploaded {full_path} to Sales folder...')
            else:
                logger.error(
                    f'Failed to upload {full_path} to Sales folder...')

    def upload_file_to_applications(self, file_path, opportunity_folder_id):
        logger.info('Uploading Applications docs...')
        BoxValidate(f'Box Request items, Box Upload File - Electric Bills {opportunity_folder_id} - Uploading Applications docs')
        success = self.box_api.upload_file_to_applications_folder(
            opportunity_folder_id, file_path)
        if success:
            logger.info(f'Uploaded {file_path} to Applications folder...')
        else:
            logger.error(
                f'Failed to upload {file_path} to Applications folder...')

    def update_opportunity_usage(self, opp_id, usage):
        content = {
            'opp_id': opp_id,
            'usage': usage
        }
        try:
            requests.post(usage_url, json=content)
        except:
            logger.info('Could not update usage in salesforce.')

    def send_quote_email_to_rep(self, rep_email, email_body):
        new_email = Email('Your Sunnova Quote is Ready', email_body)
        new_email.add_recipient(rep_email)
        response = self.outlook.send_email(new_email)
        logger.info('Sent email to rep...')
        logger.info(response.text)

    def flip_salesperson(self, name):
        name_segments = name.split(', ')
        reversed_name = reversed(name_segments)
        return ' '.join(reversed_name)

    def format_salesperson(self, salesperson) -> str:
        """
        Returns a salesperson's full name from a reversed name.
        ie Smith, Bob -> Bob Smith
            Parameters:
                salesperson (str): The salesperson name.
            Returns:
                formatted_name (str): The formatted name.
        """
        if ',' in salesperson:
            flipped = self.flip_salesperson(salesperson)
            split = flipped.split(' ')
            return split[0] + ' ' + split[-1]
        else:
            split = salesperson.split(' ')
            return split[0] + ' ' + split[-1]

    def upload_contract_files_to_dropbox(self, opportunity, files) -> bool:
        """
        Uploads all contract files to dropbox for oppportunity. Max tries 3 times. Skips if unable to find salesperson folder.
        Also creates the DL folder in the salesperson folder.
            Parameters:
                opportunity (str): The opportunity ID.
                files (list): A list of file paths to upload.
            Returns:
                success (bool): True if files were uploaded, false if not.
        """
        # Find folder path for salesman
        opportunity_name = opportunity.opportunityName
        direct_lead = opportunity.directLeadName
        salesperson = opportunity.salesperson
        space_count = salesperson.count(" ")
        if space_count > 1:
            salesperson = ' '.join(salesperson.split(" ")[0:2])
        salesperson_folder = self.get_salesperson_dropbox_folder(salesperson)
        if salesperson_folder:
            logger.info(f"Found Salesperson Folder: {salesperson_folder}")
            # Create folder using {Opp name- DL-Number}
            dl_folder_name = f'{salesperson_folder}/{opportunity_name} {direct_lead}'
            dl_folder = None
            # dl_folder = self.dropbox_api.create_folder(dl_folder_name)
            if dl_folder:
                logger.info(f"Found DL Folder: {dl_folder}")
                self.update_status("Uploading files...")
                self.upload_files_to_dropbox(files, dl_folder)
            else:
                logger.error(
                    f'Cannot create dropbox folder for {dl_folder_name}...')
                return False
            return True
        else:
            logger.info(f'Cannot find dropbox folder for {salesperson}...')
            return False

    def upload_files_to_dropbox(self, file_paths, dst_folder) -> bool:
        """
        Uploads files to dropbox.
            Parameters:
                file_paths (str): The file paths to the requested files to upload.
                dst_folder (str): The destination folder path in dropbox.
        """
        success = True
        for file_path in file_paths:
            if file_path:
                logger.info(f'Uploading {file_path}...')
                if not self.upload_file_to_dropbox(file_path, dst_folder):
                    success = False
        if not success:
            logger.error('Dropbox file upload has failed...')
        return success

    def upload_file_to_dropbox(self, file_path, dst_folder) -> bool:
        """
        Uploads a file to dropbox, attemping up to 3 times for each.
            Parameters:
            file_path (str): The file path to the requested file to upload.
            dst_folder (str): The destination folder path in dropbox.
        """
        counter = 0
        MAX_TRIES = 2
        while counter < MAX_TRIES:
            result = ""
            # result = self.dropbox_api.upload_file(file_path, dst_folder)
            if result:
                logger.info(f'Upload status: {result}')
                return True
            else:
                counter += 1
        return False

    def get_salesperson_dropbox_folder(self, salesperson) -> str:
        """
        Gets the most likely result for a salesperson's folder in dropbox through api.
            Parameters:
                salesperson (str): A salesperson name
            Returns:
                (str): A folder path for the salesperson's highest probability folder.
        """
        counter = 0
        MAX_TRIES = 2
        while counter < MAX_TRIES:
            result = ""
            # results = self.dropbox_api.search_folder(
                # salesperson, r'/Trinity Sales/Trinity Direct')
            if results:
                for result in results:
                    if "." not in result and "481075" not in result:  # 481075 is a wrong folder that gets picked a lot
                        return result
            else:
                counter += 1
        return ''

    def transfer_genesis_documents(self, opportunity_id) -> bool:
        """
        Searches for the finalized genesis documents in the x folder and moves them to the salesperson's DL folder in dropbox.
            Parameters:
                opportunity_id (str): The opportunity ID
            Returns:
                success (bool): Whether the files were successfully moved or not.
        """
        # Get opportunity info
        opp_info = get_opportunity_info(opportunity_id)
        dropbox_folder_name = f"{opp_info['opportunity_name']} {opp_info['direct_lead']}"

        # Get box folder
        print(f'Getting box folder with SF ID {opportunity_id}')
        opportunity_folder_id = self.box_api.get_box_folder_id(opportunity_id)
        print(f'Found box folder id {opportunity_folder_id}')
        BoxValidate(f'Box Request items - Transfer Genesis documents {opportunity_id} - site_info_designs_folder_id')
        site_info_designs_folder_id = self.box_api.get_folder_id_from_parent(
            opportunity_folder_id, 'Site Info-Designs')
        BoxValidate(f'Box Request items - Transfer Genesis documents {opportunity_id} - site_info_documents_folder_id')    
        site_info_documents_folder_id = self.box_api.get_folder_id_from_parent(
            site_info_designs_folder_id, 'Site Info Documents')

        # Only looking for direct layout 2/22
        TARGET_FILES = [f'DIRECT LAYOUT.pdf']

        found_files = self.get_genesis_file_ids(
            site_info_documents_folder_id, TARGET_FILES)
        if not found_files:
            return False

        # Download genesis documents
        downloaded_files = self.download_box_documents(found_files)

        # Get DL dropbox folder
        results = None
        # results = self.dropbox_api.search_folder(
            # dropbox_folder_name, r'/Trinity Sales/Trinity Direct')
        if results:
            dropbox_folder = results[0]
            logger.info(f'Found dropbox folder {dropbox_folder}')
        else:
            logger.info('Could not find dropbox folder, deleting files...')
            self.delete_temp_files(found_files)
            return False

        # Upload files
        if self.upload_files_to_dropbox(downloaded_files, dropbox_folder):
            logger.info('Uploaded files to dropbox folder...')
            self.update_status("Finished finalizing...")
        else:
            logger.info('Failed to upload files to dropbox folder...')
            self.delete_temp_files(found_files)
            return False

        self.delete_temp_files(found_files)
        return True

    def get_genesis_file_ids(self, folder_id, target_files) -> dict:
        """
        Searches the box folder for the file names given. Returns a dictionary with the key being the file name,
        and the value being the file id.
            Parameters:
                folder_id (str): The box folder id.
                target_files (list<str>): A list of file names to search for.
            Returns:
                found_files (dict): Filename key to ID value dictionary.
        """
        # Check if genesis documents exist, if not return false
        BoxValidate(f'Box Request items - Transfer Genesis documents {folder_id} - get_genesis_file') 
        contents_response = self.box_api.request_items_in_folder(folder_id)
        if not contents_response:
            return {}
        folder_items = contents_response.json()['entries']

        # Get file ids
        logger.info('Searching for these files:')
        logger.info(target_files)
        found_files = {}
        folder_content_data = {file['name']: file['id']
                               for file in folder_items}
        logger.info('Found following files in documents folder:')
        logger.info(folder_content_data)
        for search_file_name in target_files:
            for found_file_name in folder_content_data:
                if search_file_name in found_file_name:
                    found_files[found_file_name] = folder_content_data[found_file_name]
        logger.info(f'Matched files in folder: {found_files}')
        return found_files

    def download_box_documents(self, files_info) -> list:
        """
        Downloads the given file ids from dropbox.
            Parameters:
                file_ids (dict): A dictionary where the key is the file name and the value is the file id.
            Returns:
                downloaded_files (list): A list of file paths to successfully downloaded files.
        """
        downloaded_files = []
        for found_file in files_info:
            download_path = os.path.join(os.getcwd(), f'temp\\{found_file}')
            BoxValidate('Box Download file - Download Genesis documents') 
            response = self.box_api.request_download_file(
                files_info[found_file])
            if not response:
                continue
            with open(download_path, 'wb') as f:
                f.write(response.content)
                f.close()
            downloaded_files.append(download_path)
            logger.info(f'Downloaded file: {download_path}')
        return downloaded_files

    def delete_temp_files(self, files) -> None:
        for file in files:
            try:
                os.remove(f'./temp/{file}')
                logger.info(f'Deleted file: {file}')
            except:
                pass

    def run_disqualify_task(self, task):
        """
        Runs a disqualify opportunity task. Sets the opportunity stage to 11: Lost, fills in the reason lost and stag status. Send the
        rep email for reason why the opportunity was lost.
        """
        try:

            opp_info = get_opportunity_info(task.opportunityId)
            salesperson_email = opp_info['salesperson_email']

            email_success = self.salesforce.send_disqualify_email(
                task.opportunityId, task.notes, salesperson_email)
            if not email_success:
                return False

            update_success = self.disqualify_opportunity(task.opportunityId)
            if not update_success:
                return False

            return True

        except Exception as e:
            logger.info(e)
            return False

    def disqualify_opportunity(self, opportunity_id, lost_reason, lost_notes, stage_status):
        """
        Sets an opportunity stage to lost.
        """
        data = {
            "opportunity_id": opportunity_id,
            "lost_reason": lost_reason,
            "lost_notes": lost_notes,
            "stage_status": stage_status
        }
        res = requests.post(r"https://prod-27.westus.logic.azure.com:443/workflows/941a087c9c30457fa7a03779fdcd19e3/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=USqGXmp7tbQ4XSfo1g0m75FpO5jlVTPxSg2TQzV6TpQ", json=data)
        if res.status_code == 200:
            return True
        else:
            logger.error(res.text)
            return False

    # Helpers

    def update_status(self, status):
        """
        Updates the bots current status.
        """
        update_bot_status(self.bot_name, status)

    def create_salesforce_task(self, error, opp_id, subject) -> None:
        """
        Creates a task in salesforce for the given opportunity with the subject and an additional error message.
            Parameters:
                error (str): The error to append to the main body.
                opp_id (str): The opportunity id.
                subject (str): The subject of the task.
        """
        content = {
            'error': error,
            'opp_id': opp_id,
            'subject': subject
        }
        try:
            requests.post(task_url, json=content)
        except:
            logger.error(f'Unable to create salesforce task for {opp_id}...')

    def set_cc_ai_requested(self, opp_id) -> None:
        """
        Sets the given action item status to requested.
            Parameters:
                opp_id (str): The opportunity id.
        """
        content = {
            'opp_id': opp_id
        }
        try:
            requests.post(requested_ai_url, json=content)
            logger.info(f'Set Create Contract AI to "Requested"...')
        except:
            logger.error(f'Unable to set AI to "Requested" for {opp_id}...')

    def set_cc_ai_completed(self, opp_id) -> None:
        """
        Sets the given action item status to completed. This can probably be combined with other CC action item functions with an arg for status.
            Parameters:
                opp_id (str): The opportunity id.
        """
        content = {
            'opportunity_id': opp_id
        }
        try:
            requests.post(COMPLETE_CC_AI_URL, json=content)
        except:
            logger.error('Unable to set Create Contract AI to completed. ')


if __name__ == "__main__":
    pass

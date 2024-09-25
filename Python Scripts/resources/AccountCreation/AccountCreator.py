# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ..Salesforce.SalesforcePortal import SalesforcePortal
from AccountCreation.PA_config import ahj_url, human_intervention_url, referral_url
from SalesforceAPI import SalesforceAPI
# from ..config import JEFF_SALESFORCE_PASSWORD, JEFF_SALESFORCE_USERNAME
#from BotUpdate.Update import update_bot_status
from AutobotEmail.Outlook import outlook
from Configs.chromedriver_config import driver_path
import time
import requests
from customlogging import logger
from modules.outlook import outlook as intervention_outlook
from modules.outlook.Email import Email

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
#import subprocess
OS_USERNAME = os.environ.get('USERNAME')
AC_URL = r'http://148.77.75.60:6050/accountcreation'

class AccountCreator:
    def __init__(self):
        self.error = None
        self.main_window = None
        self.outlook = outlook
        self.intervention_outlook = intervention_outlook
        self.LOI_PROCESSING_REPORT_ID = '00O5b000005vulk'

    def reinit_driver(self):
        self.vars = {}
        self.start_url = 'https://trinity-solar.my.salesforce.com/home/home.jsp'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\AccCreation")  # this is the directory for the cookies
        try:
            # self.driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        except Exception as e:
            #subprocess.call("TASKKILL /f  /IM  CHROME.EXE")
            #subprocess.call("TASKKILL /f  /IM  CHROMEDRIVER.EXE")
            try:
                self.driver.quit()
                self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            except:
                pass
            logger.error('Chrome window process exists. Please close existing chrome window.')
            print(e)
            sys.exit()
        self.driver.implicitly_wait(10)
        self.main_window = self.driver.current_window_handle
        
    def create(self, direct_lead_name, bot_status):
        success = False
        try:
            self.reinit_driver()
            # self.driver.get(self.start_url)
            self.main_window = self.driver.current_window_handle
            #update_bot_status('bot3', f'Creating Account for: {direct_lead_name}')
            # self.login()

            salesforce = SalesforcePortal(self.start_url, self.driver)
            salesforce.login()

            time.sleep(2)
            while self.driver.current_url != r'https://trinity-solar.my.salesforce.com/home/home.jsp':
                if self.driver.current_url == 'https://trinity-solar.lightning.force.com/lightning/page/home':
                    break
                time.sleep(5)
                #update_bot_status('bot3', f'Need to log in...')
            self.switch_to_classic()
            bot_status("Searching for lead", direct_lead_name)
            self.classic_search(direct_lead_name)
            self.classic_search_select_direct_lead(direct_lead_name)
            bot_status("Pushing DL", direct_lead_name)
            if not self.push_dl():
                # self.close()
                logger.info("rerunning ...")
                if not self.create_rerun(direct_lead_name):
                    bot_status("Failed to push DL", direct_lead_name)
                    return False
                else:
                    return True

            if not self.click_classic_lead(direct_lead_name):
                self.close()
                return False

            bot_status("Converting Lead", direct_lead_name)
            self.convert_lead(direct_lead_name)
            success = True

            self.create_title(direct_lead_name)

            self.verify_account_created()
            logger.info('Account creation ui flow complete, sending request for AHJ and opportunity completion...')
            bot_status("AC Flow complete, creating AHJ Request", direct_lead_name)

            self.send_for_ahj(direct_lead_name)
            self.close()
            return True

        except Exception as err:
            bot_status(err, direct_lead_name)

            logger.error(err)
            self.close()
            return False
            
    def create_rerun(self, direct_lead_name):
        success = False
        try:
            #update_bot_status('bot3', f'Creating Account for: {direct_lead_name}')
            if not self.click_classic_lead(direct_lead_name):
                self.close()
                return False
            self.convert_lead(direct_lead_name)
            self.create_title(direct_lead_name)
            success = True

            self.verify_account_created()
            logger.info('Account creation ui flow complete, sending request for AHJ and opportunity completion...')
            self.send_for_ahj(direct_lead_name)
            self.close()
            return True

        except Exception as err:
            logger.error(err)
            self.close()
            return False

    def create_referral(self, direct_lead_name, bot_status):
        success = False
        try:
            self.reinit_driver()

            # self.driver.get(self.start_url)
            #update_bot_status('bot3', f'Creating Account for Referral: {direct_lead_name}')
            # self.login()

            salesforce = SalesforcePortal(self.start_url, self.driver)
            salesforce.login()

            self.switch_to_classic()
            bot_status("Searching for Lead", direct_lead_name)
            self.classic_search(direct_lead_name)
            self.classic_search_select_direct_lead(direct_lead_name)

            bot_status("Pushing DL", direct_lead_name)
            if not self.push_dl():
                if not self.create_referral_rerun(direct_lead_name):
                    return False
                else:
                    return True

            logger.info("Checking for attatched referral...")
            if not self.attach_referral(direct_lead_name):
                logger.info(f"Could not find referral.. {direct_lead_name}")
                #self.send_for_human_intervention(direct_lead_name, f'Failed to Attach Referral for {direct_lead_name}', 'Could not attach referral',True)
                # self.close()
                # return False

            # logger.info("Clicking Lead...")
            self.click_classic_lead(direct_lead_name)
            time.sleep(5)
            
            lead_conversion_result = self.convert_lead(direct_lead_name)

            logger.info(f"THIS IS THE LEAD RESULT: {lead_conversion_result}") #what is the conversion printing

            if lead_conversion_result == False:
                self.close()
                return False 

            self.create_title(direct_lead_name)
            success=True
            self.verify_account_created()
            logger.info('Account creation ui flow complete, sending request for AHJ and opportunity completion...')

            self.close()
            self.send_for_ahj(direct_lead_name)

            if lead_conversion_result == 'Creation Completed':                

                self.close()

                self.reinit_driver()
                # self.driver.get(self.start_url)
                #update_bot_status('bot3', f'Creating Account for Referral: {direct_lead_name}')
                # self.login()

                salesforce = SalesforcePortal(self.start_url, self.driver)
                salesforce.login()

                self.switch_to_classic()
                self.classic_search(direct_lead_name)
                self.classic_search_select_direct_lead(direct_lead_name)
                if not self.push_dl():
                    self.close()
                    return False
                if not self.attach_referral(direct_lead_name):
                    self.close()
                    return False
                lead_conversion_result = self.convert_lead(direct_lead_name)
                if lead_conversion_result == False:
                    self.close()
                    return False
                if lead_conversion_result == 'Creation Completed':
                    self.close()
                    return True

            self.create_title(direct_lead_name)
            if not self.verify_account_created():
                self.close()
                return False
            logger.info('Account creation referral ui flow complete, sending request for AHJ and opportunity completion...')
            self.send_for_ahj(direct_lead_name)
            success = True
            self.close()
            return True

        except Exception as err:
            bot_status(err, direct_lead_name)

            logger.error(err)
            self.close()
            return False

    def create_referral_rerun(self, direct_lead_name):
        try:
            logger.info("Checking for attatched referral...")
            if not self.attach_referral(direct_lead_name):
                logger.info("Could not find referral..")
                self.send_error_email(direct_lead_name)
                self.close()
                return False

            self.click_classic_lead(direct_lead_name)
            time.sleep(5)
            
            lead_conversion_result = self.convert_lead(direct_lead_name)

            if lead_conversion_result == False:
                self.close()
                return False 

            self.create_title(direct_lead_name)
            # time.sleep(2)

            self.verify_account_created()
            logger.info('Account creation ui flow complete, sending request for AHJ and opportunity completion...')

            self.close()
            # logger.info("sending to PA")
            self.send_for_ahj(direct_lead_name)

            if lead_conversion_result == 'Creation Completed':                

                self.close()

                self.reinit_driver()
                # self.driver.get(self.start_url)
                #update_bot_status('bot3', f'Creating Account for Referral: {direct_lead_name}')
                # self.login()

                salesforce = SalesforcePortal(self.start_url, self.driver)
                salesforce.login()

                self.switch_to_classic()
                self.classic_search(direct_lead_name)
                self.classic_search_select_direct_lead(direct_lead_name)
                if not self.push_dl():
                    self.close()
                    return False
                if not self.attach_referral(direct_lead_name):
                    self.close()
                    return False
                lead_conversion_result = self.convert_lead(direct_lead_name)
                if lead_conversion_result == False:
                    self.close()
                    return False
                if lead_conversion_result == 'Creation Completed':
                    self.close()
                    return True

            self.create_title(direct_lead_name)
            if not self.verify_account_created():
                self.close()
                return False
            logger.info('Account creation referral ui flow complete, sending request for AHJ and opportunity completion...')
            self.send_for_ahj(direct_lead_name)
            self.close()
            return True

        except Exception as err:
            logger.error(err)
            self.close()
            return True

    def check_loi_processing_report(self):
        sf_item = SalesforceAPI()
        df = sf_item.get_report(self.LOI_PROCESSING_REPORT_ID)
        if df.size == 0:
            return True

        for item_counter, direct_lead_id in enumerate(list(df['Direct Lead: ID'])):
            #print(direct_lead_id)
            sf_item.Update("Direct_Lead__c", {'Stages__c': 'LOI'}, f'{direct_lead_id}')
            logger.info(f"Updated stage to LOI for {direct_lead_id}")
            #stage = sf_item.Select(f"SELECT Stages__c from Direct_Lead__c where Id = '{direct_lead_id}'")
            #print(stage)
        return True

    def convert_referral_lead(self, direct_lead):
        """Converts a direct lead with referral source to a lead
         for attaching referral before converting to an account."""
        try:
            self.reinit_driver()
            # self.driver.get(self.start_url)
            self.main_window = self.driver.current_window_handle
            #update_bot_status('bot3', f'Creating referral lead: {direct_lead}')

            # self.login()
            salesforce = SalesforcePortal(self.start_url, self.driver)
            salesforce.login()

            time.sleep(2)
            while self.driver.current_url != r'https://trinity-solar.my.salesforce.com/home/home.jsp':
                time.sleep(5)
                #update_bot_status('bot3', f'Need to log in...')
            self.switch_to_classic()
            self.classic_search(direct_lead)
            self.classic_search_select_direct_lead(direct_lead)
            return self.push_dl()
        except Exception as err:
            logger.error(err)
            self.close()
            return True

    def close(self):
        logger.info('Ending program...')
        try:
            self.driver.quit()
        except:
            logger.info('Driver already closed...')
    '''
    def login(self):
        logger.info('logger in...')
        try:
            self.driver.find_element_by_id('username').send_keys(Keys.CONTROL, 'a')
            self.driver.find_element_by_id('username').send_keys(Keys.BACKSPACE)
            self.driver.find_element_by_id('username').send_keys(JEFF_SALESFORCE_USERNAME)
            self.driver.find_element_by_id('password').send_keys(JEFF_SALESFORCE_PASSWORD)
            self.driver.find_element_by_id('Login').click()
            time.sleep(3)
            try:
                page_text = self.driver.find_element_by_css_selector('body').text
                if "verify your identity" in page_text:
                    self.input_verification_code()
            except:
                pass
        except:
            logger.warning('unable to log in...')

    def input_verification_code(self) -> None:
        """
        Inputs the verification code for Robotic Process Automation from outlook.
        """
        code = None
        while not code:
            time.sleep(10)
            code = self.outlook.get_salesforce_verification_code()
        self.driver.find_element_by_id('emc').send_keys(str(code))
        self.driver.find_element_by_id('save').click()
    '''
    def switch_to_classic(self):
        logger.info('Switching to classic view...')
        self.driver.get(r'https://trinity-solar.lightning.force.com/ltng/switcher?destination=classic&referrer=%2Flightning%2Fpage%2Fhome')

    def classic_search(self, search_query):
        logger.info(f'Searching for {search_query}')
        try:
            self.driver.find_element_by_id('phSearchInput').send_keys(search_query)
            self.driver.find_element_by_id('phSearchButton').click()
            logger.info('done searching')
        except:
            logger.error(f'Error searching in classic mode for: {search_query}')

    def push_dl(self):
        # self.fix_direct_lead_phone_numbers()
        time.sleep(3)
        try:
            self.driver.find_element_by_css_selector('input[title="Push DL"]').click()
            # self.driver.find_element_by_xpath('//*[@id="topButtonRow"]/input[6]').click()
            logger.info('Pushing DL...')
        except:
            logger.info('DL has already been converted, no Push DL button found...')
            # self.close()
            return False
        time.sleep(3)
        # Check success status
        try:
            alert_obj = self.driver.switch_to.alert
            time.sleep(5)
            if alert_obj.text == 'Please Work Off of the Existing Opportunity Attached to the Direct Lead':
                logger.warning("DL already has a lead!")
            time.sleep(2)
            self.driver.switch_to.window(self.main_window)
            return True
        except:
            logger.info('DL Push Success')
            return True

    def fix_direct_lead_phone_numbers(self):
        logger.info('Checking phone numbers...')
        actionChains = ActionChains(self.driver)
        try:
            primary_phone = self.driver.find_element_by_id('00N32000002b3HD_ileinner')
            secondary_phone = self.driver.find_element_by_id('00N32000002b3HC_ileinner')
            phone_number_elems = [primary_phone, secondary_phone]
            for number_elem in phone_number_elems:
                actionChains.double_click(number_elem).perform()
                time.sleep(2)
        except:
            logger.error('Unable to format phone numbers!')
        try:
            logger.info('saving direct lead')
            self.driver.find_element_by_css_selector('input[title="Save"]').click()
        except:
            logger.error('Unable to save direct lead...')
            self.close()

    def click_classic_lead(self, lead_name):
        logger.info('Clicking on lead...')
        try:
            dl_name_elem = self.driver.find_element_by_id('Name_ileinner')
        except:
            logger.error('click_classic_lead was called outsite DL page...')
            # self.close()
            # return False
        try:
            self.driver.find_element_by_id('CF00N32000002b3IB_ilecell').find_element_by_css_selector('a').click()
            return True
        except:
            logger.error('Could not open new lead! Creating task for failed DL push...')
            self.send_for_human_intervention(lead_name,'The DL was unable to be pushed. Please manually push.','Failed DL Push')
            self.close()
            return False

    def classic_search_select_direct_lead(self, lead_name):
        logger.info(f'Selecting lead: {lead_name}')
        try:
            direct_lead_div = self.driver.find_element_by_id('Direct_Lead__c_body')
            direct_lead_div.find_element_by_xpath(f'//a[text()="{lead_name}"]').click()
        except:
            logger.error('Direct Lead Not Found!')
            self.close()

    def create_title(self, lead):
        try:
            title_div = self.driver.find_element_by_css_selector('iframe[title="TitlesAccount"]') # CF00N32000002jgvx_ileinner
            title_a_tag = title_div.driver.find_elements_by_css_selector('a')
            if title_a_tag:
                logger.info('Title already exists...')
                return False
        except:
            pass
        try:
            self.driver.find_element_by_css_selector('input[title="Create Title"]').click()
            logger.info('Created title...')
            time.sleep(6)
            alert_obj = self.driver.switch_to.alert
            alert_text = alert_obj.text
            alert_obj.accept()
            time.sleep(3)
        except:
            logger.info('Unable to create title')
            return False

    def convert_lead(self, direct_lead_name):
        logger.info('Converting Lead...')
        time.sleep(10)
        try:
            self.driver.find_element_by_css_selector('input[title="Convert"]').click()
        except:
            logger.info('Lead already converted')
            #self.send_for_human_intervention(direct_lead_name, f'Lead already converted for {direct_lead_name}. Please check manually.', 'Lead already converted',True)            
            return 'Creation Completed'
        self.driver.find_element_by_id('owner_id').send_keys(Keys.CONTROL, 'a')
        self.driver.find_element_by_id('owner_id').send_keys(Keys.BACKSPACE)
        self.driver.find_element_by_id('owner_id').send_keys('Trinity Direct')

        account = self.driver.find_element_by_id('accid')
        account.send_keys('create new')
        account.send_keys(Keys.ENTER)

        self.driver.find_element_by_css_selector('input[title="Convert"]').click()
        time.sleep(3)

        page_text = self.driver.find_element_by_css_selector('body').text
        # if "invalid data" in page_text.lower():
        #     json = {
        #         'lead': direct_lead_name,
        #         'key': 951753,
        #         'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiUlBBX1VTRVIiLCJ1c2VybmFtZSI6IlJQQS5JbnRlcmlvciJ9.JIlv6Azpk7JzJitM_b0y5PvK51mTLJhQ8jPPtFpIpf8'
        #     }
        #     resp = requests.post(url=AC_URL, json=json)

        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert_obj = self.driver.switch_to.alert
            alert_text = alert_obj.text
            logger.error(f'Cannot Convert Lead: {alert_text}')
            self.close()
            return False
        except:
            logger.info('Lead Converted')
            return True

    def check_for_conversion_errors(self, direct_lead_name):
        try:
            errors = self.driver.find_elements_by_class_name('errorMsg')
            for error_msg in errors:
                if error_msg.text == 'Error: Validation error on Lead: This Direct Lead has a Referral, please add Referral to Look Up field.':
                    logger.info('Referral attached, sending for referral creation...')
                    self.send_referral(direct_lead_name)
                    self.close()
                    return False
            for error_msg in errors:
                if error_msg.text == 'Error: You must enter a value':
                    logger.warning('Generic conversion error found, creating task...')
                    self.send_for_human_intervention(direct_lead_name,'The lead was unable to be converted. Please check manually.','Failed Lead Convert')

        except:
            logger.info('referral error not found')
            return True

    def verify_account_created(self):
        try:
            h1 = self.driver.find_element_by_css_selector('h1')
        except:
            logger.error('Lead Converted, Updating Opportunity VIA Power Automate')
            self.close()
            return False
        if h1.text == 'Account':
            logger.info(f'Successfully converted lead to account.')
            return True
        else:
            logger.error('Lead Converted, Updating Opportunity VIA Power Automate')
            self.close()
            return False

    def attach_referral(self, direct_lead):
        """Check if a referral was set for this DL"""
        logger.info("Sending referral...")
        try: #sometimes the PA flow completely fails, when this is the case - return false.
            result = self.send_referral(direct_lead)
            if result['setReferral'] == 'True':
                return True
            else:
                return False
        except:
            return False
        
    def send_for_ahj(self, lead_name):
        request_json = {
            'lead':lead_name
        }
        requests.post(ahj_url,json=request_json)
    
    def send_for_human_intervention(self, lead_name, error_msg, subject, mail=False):
        
        if mail:
            RECIPIENTS = [
                "sandra.balakrishnan@citrusinformatics.com",                    
                "jeff.macdonald@trinity-solar.com",
                "powerautomateteam@trinity-solar.com",
                "vijay.madduri@trinitysolarsystems.com"
            ]

            email = Email(subject="Lead Already Converted Alert")
            email.add_recipients(RECIPIENTS)        
            email.add_bcc("Power.AutomateTeam@trinitysolarsystems.com")

            logger.info("Alert Email For Lead Already Converted")
            body = "<h3>Hello,<br/>Human-Intervention needed for " + str(lead_name) +" with error Lead Already Created.</h3>"            
            email.set_body(body)           
            intervention_outlook.send_email(email)
            mail = False

        request_json = {
            'lead':lead_name,
            'error':error_msg,
            'subject':subject
        }
        if error_msg == "Lead already converted":
            do_nothing = True
        else:
            requests.post(human_intervention_url,json=request_json)     
        
    
    def send_referral(self,lead_name):
        request_json = {
            'lead':lead_name
        }
        response = requests.post(referral_url,json=request_json)
        return response.json()
    
    def send_error_email(self, direct_lead_name):
        
        sender_email = "powerautomateteam@trinity-solar.com"
        receiver_email = [
            "avigoyal@trinity-solar.com",
            "jeffmacdonald@trinity-solar.com",
            "powerautomateteam@trinity-solar.com"
            ]
        password = "pA951456!"

        message = MIMEMultipart("alternative")
        message["Subject"] = "Account Creation Error, Failed To Find Referral"
        message["From"] = sender_email
        message["To"] = ", ".join(receiver_email)

        text = """\
            Hey,
            Failed to find referral for DL:""" + direct_lead_name + """ """

        html = """\
            <html>
              <body>
                <p>Hey,</p><br>
                <p>Failed to find referral for DL:""" + direct_lead_name + """ </p>
              </body>
            </html>
         """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        mailserver = smtplib.SMTP('smtp.office365.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login(sender_email, password)
        mailserver.sendmail(sender_email, receiver_email, message.as_string())
        mailserver.quit()

if __name__ == "__main__":
    #manual_lead = 'DL-958631'
    # manual_lead = 'DL-1000876'
    creator = AccountCreator()
    creator.check_loi_processing_report()

    #creator.create(manual_lead)




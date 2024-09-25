# Resource Folder Import
import os
import sys
import json

from dotenv import dotenv_values

sys.path.append(os.environ["autobot_modules"])
from customlogging import logger
import time
from AutobotEmail.Outlook import outlook
from Configs.chromedriver_config import driver_path

try:
    from resources.config import (
        SALESFORCE_USERNAME,
        SALESFORCE_PASSWORD,
        MICROSOFT_USERNAME,
        MICROSOFT_PASSWORD,
    )
except:
    from config import (
        SALESFORCE_USERNAME,
        SALESFORCE_PASSWORD,
        MICROSOFT_USERNAME,
        MICROSOFT_PASSWORD,
    )
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OS_USERNAME = os.environ.get('USERNAME')
config_path = os.environ['autobot_modules'].split("\\resources")[0]
"""
try:
    OKTA = open('config.json')
except:
    OKTA = open(f"{config_path}/config.json")

OKTA = json.load(OKTA)
OKTA_USERNAME = OKTA['credentials']["okta"]["rpa"]["username"]
OKTA_PASSWORD = OKTA['credentials']["okta"]["rpa"]["password"]
"""
class SalesforcePortal:
    def __init__(self, salesforce_url=None, driver=None):
        self.error = None
        self.outlook = outlook
        self.vars = {}
        self.lightning_url = "https://trinity-solar.lightning.force.com/lightning/page/home"

        if salesforce_url:
            self.driver = driver
            self.start_url = salesforce_url
        else:
            self.start_url = "https://trinity-solar.my.salesforce.com/home/home.jsp"
            self.genesis_report_url = r"https://trinity-solar.lightning.force.com/lightning/r/Report/00O5b0000050MhzEAE/view"
            self.driver = None
        self.preprod_url = r"https://trinity-solar--preprod.sandbox.my.salesforce.com/"

        self.preprod_url = "https://trinity-solar--preprod.sandbox.my.salesforce.com/"

    def reinit_drivers(self):
        self.close()
        chrome_options = webdriver.ChromeOptions()
        # this is the directory for the cookies
        chrome_options.add_argument(
            f"user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\Salesforce"
        )
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # self.driver = webdriver.Chrome(
        #     # options=chrome_options, executable_path=driver_path)
        #     executable_path=driver_path
        # version='')
        self.driver.implicitly_wait(10)

    def close(self):
        logger.info("Ending program...")
        try:
            self.driver.quit()
        except:
            logger.info("Driver already closed...")

    def task(func):
        """
        This is a decorator for every function in a portal. Starts and closes drivers whether or not there is an error.
        All functions should be wrapped with this to ensure to open chromedrivers leak.
        """

        def wrapper(self, *args, **kwargs):
            self.reinit_drivers()
            try:
                func(self, *args, **kwargs)
            except Exception:
                pass
            finally:
                self.close()

        return wrapper

    def send_contract_email(self, finalize_quote_task):
        try:
            self.reinit_drivers()
            self.driver.get(self.start_url)
            self.login()
            self.switch_to_classic()
            self.classic_search(
                finalize_quote_task.sunnovaQuote.genesisDesign.opportunity.directLeadName
            )
            self.open_opportunity(
                finalize_quote_task.sunnovaQuote.genesisDesign.opportunity.salesforceId
            )
            time.sleep(5)
            logger.info("attempting open action item page")
            try:
                self.open_create_contract_ai()
            except:
                self.open_action_item_page()
                logger.info("attempting open create contract ai")
                self.open_create_contract_ai()
                logger.info("attempting open send email")
            self.open_send_email()
            logger.info("attempting format email")
            self.select_email_template(template="contract")
            self.format_email(finalize_quote_task)
            self.send_email()
            self.close()
            return True
        except Exception as err:
            logger.error(err)
            self.close()
            return False

    def send_disqualify_email(self, opportunity_id, notes, salesperson_email) -> bool:
        """
        Sends the Create Contract AI email for disqualification.
        """
        try:
            self.reinit_drivers()
            self.driver.get(self.start_url)
            self.login()
            self.switch_to_classic()
            self.open_opportunity(opportunity_id)  # TODO: Get opp using ID only
            time.sleep(5)
            logger.info("Opening Action Items Page")
            try:
                self.open_create_contract_ai()
            except:
                self.open_action_item_page()
                logger.info("Opening Action Item...")
                self.open_create_contract_ai()
                logger.info("Opening Email...")
            self.open_send_email()
            logger.info("Formatting Email...")
            self.select_email_template(template="disqualify")
            self.format_disqualify_email(salesperson_email, notes)
            self.send_email()
            self.close()
            return True
        except Exception as err:
            logger.error(err)
            self.close()
            return False

    def generate_conga_contract(self, opportunity):
        try:
            self.reinit_drivers()
            self.driver.get(self.start_url)
            self.login()
            self.switch_to_classic()
            self.classic_search(opportunity.directLeadName)
            self.open_opportunity(opportunity.salesforceId)
            contract_path = self.generate_contract_current_page(
                opportunity.opportunityName
            )
            self.close()
            return contract_path
        except Exception as err:
            logger.error(err)
            self.close()
            return None

    def login(self) -> bool:
        """
        Logs the user in to the current page.
        """
        logger.info("Logging in...")
        self.driver.get(self.start_url)
        time.sleep(5)
        self.driver.maximize_window()
        url = self.driver.current_url

        if self.start_url in url or self.lightning_url in url:
            return True

        try:
            microsoft_sso = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Microsoft SSO')]",)))
            microsoft_sso.click()
            time.sleep(5)
            url = self.driver.current_url
            if self.start_url in url or self.lightning_url in url:
                return True
        except Exception as e:
            print(e)
            pass

        #username
        try:
            username = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="i0116"]')))
            username.send_keys(MICROSOFT_USERNAME)
            #clicks next
            self.driver.find_element(by=By.XPATH, value='//*[@id="idSIButton9"]').click()
            time.sleep(5)
        except:
            print(f"Passing the username")
            pass
        #password
        try:
            password = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#i0118')))
            time.sleep(5)
            password.send_keys(MICROSOFT_PASSWORD)
            time.sleep(5)
        except:
            print("Could not input password")

        #sign in
        try:    
            self.driver.find_element(by=By.XPATH, value='//*[@id="idSIButton9"]').click()
        except:
            print("Already logged in")

        logger.info('10 second wait...')
        time.sleep(10)
        #if page text has "stay signed in.. "
        try:
            page_text = self.driver.find_element(by=By.CSS_SELECTOR, value='body').text
            if "Stay signed in?" in page_text:
                self.driver.find_element(by=By.XPATH, value='//*[@id="idBtn_Back"]').click()
                logger.info("Logged in...")
        except:
            print("Logging in...")
            pass
        """
        logger.info('Logging in...')
        self.driver.get(self.salesforce_url)
        time.sleep(5)
        self.driver.maximize_window()
        url = self.driver.current_url
        logger.info(f"Current url:{url}")

        logger.info("Salesforce Login via Microsoft SSO")
        driver = self.driver
        try:
            try:
                microsoft_azure = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@id='idp_section_buttons']//span[contains(text(),'Microsoft SSO')]",
                        )
                    )
                )
                microsoft_azure.click()
                time.sleep(5)
                url = driver.current_url
                if self.start_url in url:
                    return True
                try:
                    WebDriverWait(driver, 100).until(
                        EC.presence_of_element_located((By.NAME, "loginfmt"))
                    ).send_keys(MICROSOFT_USERNAME)
                    WebDriverWait(driver, 100).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//input[@id='idSIButton9']")
                        )
                    ).click()
                    time.sleep(3)
                    WebDriverWait(driver, 25).until(
                        EC.presence_of_element_located((By.NAME, "passwd"))
                    ).send_keys(MICROSOFT_PASSWORD)
                    time.sleep(3)
                    WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//input[@id='idSIButton9']")
                        )
                    ).click()
                    time.sleep(3)
                    WebDriverWait(driver, 50).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//input[@id='idSIButton9']")
                        )
                    ).click()
                    time.sleep(3)
                    return True
                except Exception as e:
                    logger.info("Unable to login to Salesforce Account")
                    logger.error(e)
                    return False
            except:
                microsoft_azure = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@id='idp_hint']//span[contains(text(),'Microsoft SSO')]",
                        )
                    )
                )
                microsoft_azure.click()
                time.sleep(5)
                return True
        except Exception as e:
            logger.info("Unable to login to Salesforce Account")
            logger.error(e)
            return False
        """
    def input_verification_code(self) -> None:
        """
        Inputs the verification code for Robotic Process Automation from outlook.
        """
        code = None
        while not code:
            time.sleep(10)
            code = self.outlook.get_salesforce_verification_code()
        self.driver.find_element_by_id("emc").send_keys(str(code))
        self.driver.find_element_by_id("save").click()

    def switch_to_classic(self):
        logger.info("Switching to classic view...")
        try:
            time.sleep(3)
            self.driver.find_element(by=By.CLASS_NAME, value="photoContainer")
            self.driver.find_element(
                by=By.XPATH,
                value='//a[contains(text(), "Switch to Salesforce Classic")]',
            ).click()
        except:
            logger.info("already in classic")

    def classic_search(self, search_query):
        logger.info(f"Searching for {search_query}")
        try:
            self.driver.find_element_by_id("phSearchInput").send_keys(search_query)
            self.driver.find_element_by_id("phSearchButton").click()
            time.sleep(5)
            self.driver.find_element_by_xpath(
                f'//a[contains(text(), "{search_query}")]'
            ).click()
        except:
            logger.error(f"Error searching in classic mode for: {search_query}")

    def open_action_item_page(self):
        ai_id = self.get_action_item_id()
        action_item_box = self.driver.find_element_by_id(ai_id)
        action_item_box.find_element_by_xpath("//a[contains(text(), 'Go to list')]")

    def open_create_contract_ai(self):
        try:
            self.driver.find_element_by_xpath(
                '//a[contains(text(), "Create Contract")]'
            ).click()
        except:
            logger.info("Could not find Create Contract AI")

    def open_send_email(self):
        self.driver.find_element_by_css_selector('input[value="Send E-mail"]').click()

    def overwrite_text_box(self, element, string):
        """Replaces text inside an input element with the given string."""
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(string)

    def format_email(self, finalize_quote_task):
        """
        Formated the AI email template on the current page.

            Parameters:
                finalize_quote_task (FinalizeSunnovaQuoteTask): The finalize task with the needed info.
        """
        loi_rate = str(
            finalize_quote_task.sunnovaQuote.genesisDesign.opportunity.loiRate
        )
        escalator = finalize_quote_task.sunnovaQuote.genesisDesign.opportunity.escalator
        solar_production = finalize_quote_task.sunnovaQuote.estimatedProduction

        # Add salesperson's email to the "To:" field
        self.driver.find_element_by_id("p24").send_keys(
            finalize_quote_task.sunnovaQuote.genesisDesign.opportunity.salespersonEmail
        )
        # Get the original body template
        email_body_elem = self.driver.find_element_by_id("p7")
        email_body = email_body_elem.get_attribute("value")
        # Add information to template since it has not been updated
        rated_email_body = email_body.replace(
            "LOI Rate:  @", f"LOI Rate: ${loi_rate} @ {escalator}"
        )
        formatted_email_body = rated_email_body.replace(
            "Solar Production: ", f"Solar Production: {solar_production}"
        )

        if finalize_quote_task.salespersonNotes:
            logger.info("Adding salesperson notes...")
            logger.info(formatted_email_body)
            snip = "If you have any questions or need changes, please contact Sales Operations Support."
            new_section = (
                f"Additional Notes: {finalize_quote_task.salespersonNotes}"
                + "\n\n"
                + snip
            )
            formatted_email_body = formatted_email_body.replace(snip, new_section)
            logger.info("Replaced: ")
            logger.info(formatted_email_body)
        else:
            logger.info("No additional notes found...")
        self.overwrite_text_box(email_body_elem, formatted_email_body)

    def format_disqualify_email(self, email, notes):
        """
        Formats the existing email template with notes.
        """
        # Add salesperson's email to the "To:" field
        self.driver.find_element_by_id("p24").send_keys(email)
        # Get the original body template
        email_body_elem = self.driver.find_element_by_id("p7")
        email_body = email_body_elem.get_attribute("value")
        new_email_body = email_body.replace("<reason(s)>", notes)
        self.overwrite_text_box(email_body_elem, new_email_body)

    def select_email_template(self, template="contract"):
        """
        Chooses the Direct Contract Email template from the Select Templates Menu

            Parameters:
                template (str): Type of email template. contract or disqualify
        """
        if template == "contract":
            template_title = "Direct Contract Email"
        elif template == "disqualify":
            template_title = "Direct Lost Email"

        main_handle = self.driver.current_window_handle

        template_button = self.driver.find_elements_by_css_selector(
            'input[name="template"]'
        )[0]
        self.driver.execute_script("arguments[0].click();", template_button)

        popup_handle = None
        for handle in self.driver.window_handles:
            if handle != main_handle:
                popup_handle = handle
        if not popup_handle:
            logger.error("Unable to open select template window...")
            return None

        self.driver.switch_to.window(popup_handle)
        self.driver.find_element_by_xpath(
            f"//a[contains(text(), '{template_title}')]"
        ).click()
        self.driver.switch_to.window(main_handle)
        return True

    def send_email(self):
        time.sleep(2)
        self.driver.find_element_by_css_selector('input[name="send"]').click()
        time.sleep(5)

    def get_action_item_id(self):
        suffix = "_00N32000003F2wx"
        url = self.driver.current_url
        splits = url.split(r"/")
        opp_id = splits[-1][:14]
        return opp_id + suffix

    def generate_contract_current_page(self, opportunity_name):
        logger.info("Generating contract for current page.")
        # Save current window handle
        main_handle = self.driver.current_window_handle
        # Get iframe title="CongaRedirects"
        WebDriverWait(self.driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it(
                self.driver.find_element_by_css_selector(
                    'iframe[title="CongaRedirects"]'
                )
            )
        )
        # Click Generate Contract after it loads.
        contract_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[value="Generate Contract"]')
            )
        )
        self.driver.execute_script("arguments[0].click();", contract_button)
        # Grab popup handle
        self.driver.switch_to.window(self.driver.window_handles[-1])
        next_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, "apxt-c8-multiselect-next-btnInnerEl"))
        )
        self.driver.execute_script("arguments[0].click();", next_button)
        next_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, "apxt-c8-start-merge-btnInnerEl"))
        )
        self.driver.execute_script("arguments[0].click();", next_button)
        backup_counter = 0
        file_name = f"Combined Pack - {opportunity_name}.pdf"
        file_path = f"C:\\Users\\{OS_USERNAME}\\Downloads\\{file_name}"
        logger.info(f"Searching for file download: {file_path}")
        while True:
            if os.path.exists(file_path):
                break
            elif backup_counter > 90:
                return False
            else:
                time.sleep(3)
                backup_counter += 1
        self.driver.switch_to.window(main_handle)
        return file_path

    def open_opportunity(self, opportunity_id):
        if len(opportunity_id) >= 18:
            opportunity_id = opportunity_id[:15]

        opp_url = "https://trinity-solar.my.salesforce.com/" + opportunity_id
        self.driver.get(opp_url)

    def download_genesis_report(self, report_url) -> str:
        """
        Opens and downloads the Genesis report for saturday RSA's.
        Returns the download csv path. Defaults to user download folder.
        """
        self.reinit_drivers()
        self.driver.get(self.start_url)
        self.login()
        self.driver.get(report_url)
        time.sleep(5)
        iframe = self.driver.find_element_by_css_selector("iframe")
        self.driver.switch_to.frame(iframe)
        buttons = self.driver.find_elements_by_class_name("actionBarButtonGroup")
        last_button = buttons[-1]
        last_button.find_elements_by_css_selector("button")[-1].click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('span[title="Export"]').click()
        time.sleep(1)
        self.driver.switch_to.default_content()
        export_menu = self.driver.find_element_by_class_name("slds-modal__container")
        details_only_button = export_menu.find_elements_by_class_name(
            "slds-visual-picker"
        )[-1]
        details_only_button.click()
        time.sleep(1)
        detail_holder = self.driver.find_element_by_class_name(
            "data-excel-input-holder"
        )
        file_type_selector = detail_holder.find_elements_by_class_name(
            "slds-select_container"
        )[0]
        file_type_selector.click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('option[value="localecsv"]').click()
        time.sleep(1)
        self.driver.find_element_by_css_selector('button[title="Export"]').click()
        while True:
            time.sleep(3)
            dst_path = f"C:\\Users\\{OS_USERNAME}\\Downloads"
            files = os.listdir(dst_path)
            for file in files:
                if "report" in file and "csv" in file and "crdownload" not in file:
                    print(f"Found file {file}")
                    self.close()
                    return os.path.join(dst_path, file)


if __name__ == "__main__":
    portal = SalesforcePortal()
    """
    portal.reinit_drivers()
    start_url = "https://trinity-solar--preprod.sandbox.my.salesforce.com/"
    portal.driver.get(start_url)
    portal.login()
    """
    portal.test("test string")

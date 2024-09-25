from resources.browser import Browser
from resources.config import SALESFORCE_USERNAME, SALESFORCE_PASSWORD, JEFF_SALESFORCE_PASSWORD, JEFF_SALESFORCE_USERNAME
from resources.AutobotEmail.Outlook import Outlook
import resources.customlogging
import logging
import time

logger = logging.getLogger(__name__)


class SalesforceClassicBrowser(Browser):
    """
    A browser for navigating through Salesforce in classic view mode.
    An Outlook instance has to be created for us to receive a 2FA code.
    Due to 2FA a user is required.
    """

    def __init__(self, user):
        super().__init__(user=user)
        self.outlook = Outlook()

    def __repr__(self):
        return f'{type(self)}(user={self.user})'

    def login(self) -> None:
        """
        Logs the user in to Salesforce. Doesn't check if user is currently logged in.
        """
        logger.info('Logging in...')
        self.driver.get(r'https://trinity-solar.my.salesforce.com/')
        self.input_login_info()
        time.sleep(3)  # Let 2FA Load
        if self.check_two_factor_authentication():
            self.handle_two_factor_authentication()

    def input_login_info(self) -> None:
        """
        Inputs the username and password then submits on the current page.
        """
        self.driver.find_element_by_id(
            'username').send_keys(SALESFORCE_USERNAME)
        self.driver.find_element_by_id(
            'password').send_keys(SALESFORCE_PASSWORD)
        self.driver.find_element_by_id('Login').click()

    def handle_two_factor_authentication(self) -> None:
        """
        Handles 2FA for the user currently logging in.
        """
        authentication_code = self.get_two_factor_authentication_code()
        self.input_two_factor_authentication_code(authentication_code)

    def check_two_factor_authentication(self) -> bool:
        """
        Checks the current page to determine if 2FA handling is needed.
        """
        try:
            page_text = self.driver.find_element_by_css_selector('body').text
            if "verify your identity" in page_text:
                return True
        except Exception:
            return False

    def get_two_factor_authentication_code(self) -> str:
        """
        Gets a two factor authentication code from the RPA user email.
        """
        code = None
        while not code:
            time.sleep(10)
            code = self.outlook.get_salesforce_authentication_code()
        return code

    def input_two_factor_authentication_code(self, authentication_code) -> None:
        """
        Inputs a authentication code for Robotic Process Automation.
        Typically only has to be done once per machine.
        """
        self.driver.find_element_by_id(
            'emc').send_keys(str(authentication_code))
        self.driver.find_element_by_id('save').click()

    def open_opportunity_page(self, opportunity_id) -> None:
        """
        Opens the given opportunity in class view mode.
        Works with 18 or 15 digit ids.
        """
        logger.info(f'Opening opportunity page for {opportunity_id}')
        if len(opportunity_id) >= 18:
            opportunity_id = opportunity_id[:15]
        opp_url = "https://trinity-solar.my.salesforce.com/" + opportunity_id
        self.driver.get(opp_url)


class SalesforceLightningBrowser(Browser):
    """
    A browser for navigating through Salesforce in lightning view mode.
    Only used for reports.
    """
    pass

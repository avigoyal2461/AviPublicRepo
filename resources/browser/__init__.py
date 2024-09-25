from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import os
import logging
from types import FunctionType
from ..Configs.chromedriver_config import driver_path

OS_USERNAME = os.environ.get('USERNAME')

logger = logging.getLogger(__name__)

def task(func) -> FunctionType:
        """
        This is a decorator for every function in a portal. Starts and closes drivers whether or not there is an error.
        All functions should be wrapped with this to ensure to open chromedrivers leak.
        """

        def wrapper(self, *args, **kwargs):
            self.start()
            try:
                func(self, *args, **kwargs)
            except Exception as e:
                logger.error(e)
            finally:
                self.close()
        return wrapper

class Browser:
    """
    A chrome browser instance controlled by Selenium using the official chromedriver.
    All chromedriver instances must be closed properly or memory/process leaks occur.
    Browsers without a user will have no cookies and as such will have to jump through 
    some steps which users that have cookies do not. Generally a user should be provided.
    """

    def __init__(self, user=None):
        self.user = user
        self.driver = None

    def start(self):
        """
        Starts a browser session using chrome. Initializes to the user given if available.
        Restarts the existing attached browser in case it is called early to stop process leaks.
        """
        self.close()
        chrome_options = webdriver.ChromeOptions()
        if self.user:
            chrome_options.add_argument(
                f"user-data-dir=C:\\Users\\{OS_USERNAME}\\AppData\\Local\\Google\\Chrome\\User Data\\{self.user}")
        self.driver = webdriver.Chrome(
            options=chrome_options, executable_path=driver_path)
        self.driver.implicitly_wait(10)

    def close(self):
        """
        Stops the current chromedriver. Calling driver.close only closes the current window.
        """
        logger.info('Closing browser...')
        try:
            self.driver.quit()
        except:
            logger.warning('Browser already closed...')

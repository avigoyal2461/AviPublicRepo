# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

from selenium import webdriver
from TSNetReports.TSN_config import report_config, date_config, email_config
from AutobotEmail.Outlook import Outlook
from AutobotEmail.Email import Email
from Configs.chromedriver_config import driver_path
import base64
import time
import os
import datetime
import shutil
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from BotUpdate.ProcessTable import RPA_Process_Table

login_url = r'https://trinity-monitoring.net/login'
enterprise_report_url = r'https://trinity-monitoring.net/reports/enterprise/index.php'
username = os.environ['USERNAME']

class TSReportGenerator:
    def __init__(self):
        self.bot_update = RPA_Process_Table()
        self.name = "TSN_Reports"
        self.bot_update.register_bot(self.name)

        self.report_init_now = datetime.datetime.now()
        self.report_date = self.report_init_now.strftime('%Y-%m-%d')
        self.bot_update.update_bot_status(self.name, f"Starting to process", self.report_date)

        print('Report date: ' + self.report_date)
        self.current_report_owner = ''
        self.all_reports_folder_path = f'C:\\Users\\{username}\\Desktop\\tsreports'
        self.reports_folder_path = self.all_reports_folder_path + '\\TSReports ' + self.report_date
        self.download_folder_path = f'C:\\Users\\{username}\\Downloads'
        self.outlook = Outlook()

    def set_drivers(self):
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument(f"user-data-dir=C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\TSNetReports")  # this is the directory for the cookies
        # self.driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        self.driver.implicitly_wait(10)
        self.main_window = self.driver.current_window_handle


    def run_monthly_reports(self):
        self.set_drivers()
        self.login()
        time.sleep(15)
        code = self.get_verification_code()
        print('Retrieved code: ' + code)
        self.verify_login(code)
        self.run_enterprise_reports()
        self.send_enterprise_reports()
        # self.run_billing_reports()
        self.driver.quit()
        self.bot_update.complete_opportunity(self.name, self.report_date)
        self.bot_update.edit_end()
        print('Report run...')

    def run_enterprise_reports(self):
        self.create_reports_folder()
        for owner in report_config['enterprise_reports']:
            self.current_report_owner = owner['site_name']
            for site_group in owner['site_group']:
                self.create_enterprise_report(site_group, owner['details'])
                self.add_latest_file_to_reports_folder(site_group)

    def run_billing_reports(self):
        for owner in report_config['billing_reports']:
            self.current_report_owner = owner['site_name']
            file_names = []
            self.goto_billing_summary()
            file_names.append(self.create_billing_summary(owner))
            self.send_report_email()

    def create_reports_folder(self):
        if not os.path.exists(self.reports_folder_path):
            os.makedirs(self.reports_folder_path)


    def login(self):
        self.driver.get(login_url)
        self.driver.find_element_by_id('username').send_keys('powerautomateteam@trinity-solar.com')
        self.driver.find_element_by_id('password').send_keys('Solar2023!')
        self.driver.find_element_by_css_selector('input[value="Log in"]').click()
        time.sleep(5)

    def get_verification_code(self):
        print('Retrieving verification code...')
        return self.outlook.get_ts_net_verification_code()

    def verify_login(self, code):
        self.driver.find_element_by_id('securityCode').send_keys(code)
        self.driver.find_element_by_id('submit-button').click()

    def goto_enterprise_report(self):
        self.driver.switch_to.window(self.main_window)
        self.driver.find_element_by_name('jumpToInput').click()
        self.driver.find_element_by_css_selector('option[value="/reports/enterprise/index.php"]').click()


    def create_enterprise_report(self, site, details):
        """Creates report of the previous month on the first day of the current month."""
        self.driver.get(enterprise_report_url)
        time.sleep(3)
        # Set name
        self.driver.find_element_by_id('siteGroupId').click()
        print(site)
        self.driver.find_element_by_css_selector('option[value="' + site['value'] + '"]').click()
        # Set start date
        self.driver.find_element_by_id('startTimeInput').click()
        day_picker = self.driver.find_element_by_class_name('datepicker-days')
        day_picker.find_element_by_class_name('prev').click()
        self.driver.find_elements_by_xpath('//td[text()="1"]')[0].click()
        self.driver.find_element_by_xpath('//td[text()="Start Date"]').click()
        # set end date
        self.driver.find_element_by_id('endTimeInput').click()
        day_picker = self.driver.find_element_by_class_name('datepicker-days')
        day_picker.find_element_by_class_name('prev').click()
        last_day = self.last_day_of_last_month()
        day_picker.find_elements_by_xpath(f'//td[text()="{last_day}"]')[-1].click()
        self.driver.find_element_by_xpath('//td[text()="End Date"]').click()
        # set device readings
        self.driver.find_element_by_css_selector('input[value="device"]').click()
        # set details
        self.driver.find_element_by_id('detailsAddresses').click()
        if 'Meter reading dates' in details:
            self.driver.find_element_by_id('detailsReadingDates').click()
        self.driver.find_element_by_id('button-submit').click()
        self.driver.find_element_by_css_selector('button[onclick="exportToFile(\'pdf\')"]').click()

    def add_latest_file_to_reports_folder(self, site_group):
        time.sleep(8)
        report_folder_name = self.current_report_owner + ' ' + self.report_date
        report_folder_path = self.reports_folder_path +'\\' + report_folder_name
        # Get last downloaded file path
        download_folder = os.listdir(self.download_folder_path)
        file_names = [self.download_folder_path + '\\' + file_name for file_name in download_folder]
        sorted_downloads = sorted(file_names, key=os.path.getmtime, reverse=True)
        print(sorted_downloads)
        downloaded_report_path = sorted_downloads[0]
        # Create report folder if it doesn't exist
        if not os.path.exists(report_folder_path):
            os.makedirs(report_folder_path)
        # Move and rename report download
        shutil.move(downloaded_report_path, report_folder_path + '\\' + site_group['name'] + '.pdf')
        print(f'Moved {downloaded_report_path} report download to {report_folder_path}...')
        time.sleep(2)

    def get_most_recent_download_path(self):
        pass


    def goto_billing_summary(self):
        pass

    def create_billing_summary(self, site):
        pass

    def send_enterprise_reports(self):
        for file_name in os.listdir(self.reports_folder_path):
            self.send_enterprise_report(f'{self.reports_folder_path}\\{file_name}')
            

    def send_enterprise_report(self, folder_path):
        folder_name = os.path.basename(folder_path)
        owner = folder_name.replace(f' {self.report_date}', '')
        email_addresses = email_config[owner] 
        email = Email(subject='Trinity Solar Monthly Report')
        email.set_body('Your monthly report is now available!\nFor any questions or concerns please contact the Monitoring dept Monitoring@trinity-solar.com')
        email.add_recipients(email_addresses)

        print(email_addresses)
        # for item in email_addresses:
        #     print(item)
        email.add_cc('monitoring@trinity-solar.com')
        email.add_cc('jeff.macdonald@trinity-solar.com')
        email.add_cc('powerautomateteam@trinity-solar.com')
        for file_name in os.listdir(folder_path):
            content = self.get_file_bytes_from_path(f'{folder_path}\\{file_name}')
            email.add_attachment(content, file_name)
            print('Added attachment')
        response = self.outlook.send_email(email)
        # print(response.status_code)

    def get_file_bytes_from_path(self, path):
        with open(path, "rb") as file_contents:
            encoded_string = base64.b64encode(file_contents.read())
            return encoded_string.decode('utf-8')

    def last_day_of_last_month(self):
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)
        month = lastMonth.month
        return date_config[str(month)]['last']

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    reports = TSReportGenerator()
    reports.run_monthly_reports()

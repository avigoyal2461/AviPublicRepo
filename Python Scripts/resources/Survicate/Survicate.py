import fnmatch
import os
import sys
sys.path.append(os.environ['autobot_modules'])

import time
from SurvicateBrowser import SurvicateBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from AutobotEmail.RPA_email import RPA_email
from Config import receiver_email,Sharepoint_userName,Sharepoint_password,Survicate_sharepoint_URL,Survicate_sharepoint_relative_URL,report_download_survicatepath,Chromedriver_Settings,florida_customer_sat,postinstall,post_pto,florida_customer_report, postinstall_report,post_pto_report,export_link,new_report,florida_customer_new_report,postinstall_new_report,post_pto_new_report,exception_email
from customlogging import logger
import sched
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import pandas as pd
from Sharepoint.connection import SharepointConnection
from selenium.common.exceptions import TimeoutException
from time import sleep
import schedule
from pathlib import Path


class Survicate():
    """
    This class is the main class which includes following processes:
    Downloading the reports from the site 'home-c36.nice-incontact.com'.
    process the reports and upload the file to sharepoint
    """
    def __init__(self):
        self.driver = Chromedriver_Settings()

    def CreateDownloadLink(self,ReportUrl,Reportname):
        """This function is used to download the reports"""
        try:
            logger.info(f'Survicate Reports Automation – Download Reports starting.')
            self.driver.get(ReportUrl)
            time.sleep(20)
            export_button = self.driver.find_element(By.CSS_SELECTOR,
                                                'button.s-new-button.has-icon.icon-align-left.type-icon.s-small[type="button"]')
            export_button.click()
            time.sleep(5)
            first_radio_button = self.driver.find_element(By.CLASS_NAME, 's-radio')
            first_radio_button.click()
            time.sleep(3)
            request_button = self.driver.find_element(By.CSS_SELECTOR,
                                                 'button.s-new-button.color-brand.air-left-double[type="button"]')
            request_button.click()
            logger.info(f'Survicate Reports Automation – Created Download Link -'+Reportname+'.')
            return
        except TimeoutException:
            raise TimeoutException("Timeout exception occurred during the report downloading process.")
        except Exception as ex:
            # logger.error(f'Survicate Reports Automation – {str(ex).strip()}')
            # ProcessException(str(ex).strip())
            # RingCentralBrowser(self.driver).Logout()
            raise
    def DownloadReport(self,ReportName):
        try:
            self.driver.get(export_link)
            time.sleep(10)
            table_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 's-table.air')))

            tbody_element = table_element.find_element(By.TAG_NAME, 'tbody')
            rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                post_pto_link = row.find_elements(By.XPATH, ".//a[text()='"+ReportName+"']")
                third_cell = row.find_element(By.XPATH, "./td[3]")
                third_cell_text = third_cell.text
                if post_pto_link and third_cell_text == 'XLSX':
                    last_column_link = row.find_elements(By.XPATH, ".//td[last()]//a")
                    if last_column_link:
                        last_column_link[0].click()
                        break
        except Exception as e:
            raise

    def rename_latest_file(self,new_name):
        folder = Path(report_download_survicatepath)
        files = [f for f in folder.iterdir() if f.is_file()]
        if not files:
            logger.info("Survicate Reports Automation – Survicate Reports Automation – No files found in the folder.")
            return
        latest_file = max(files, key=os.path.getmtime)
        new_file_name = new_name + latest_file.suffix
        latest_file.rename(folder.joinpath(new_file_name))
        logger.info(f"Survicate Reports Automation – The downloaded file has been renamed to: {new_file_name}")

    # def CreateExcelFile():
    #
    #     input_excel_file = dummy_excel_path+florida_customer_report
    #     df = pd.read_excel(input_excel_file)
    #     field_names = df.columns.tolist()
    #
    #     new_df = pd.DataFrame(columns=field_names)
    #     output_excel_file = new_report+florida_customer_report
    #     new_df.to_excel(output_excel_file, index=False)


    def CreatePostInstallReport(self):

        source_file_path = report_download_survicatepath+postinstall_report+".xlsx"
        source_df = pd.read_excel(source_file_path)

        destination_df = pd.DataFrame()
        destination_df['date'] = source_df['Date & Time (UTC)']
        destination_df['visitor_uuid'] = source_df['Respondent uuid']
        destination_df['page'] = source_df['Page']
        destination_df['Q#1: How satisfied are you with your recent installation?'] = source_df['Q#1: How satisfied are you with your recent installation?']
        destination_df['Q#2: What could we have done better?'] = source_df['Q#2: What could we have done better?']
        destination_df['Q#3: Were you home for your solar installation?'] = source_df['Q#3: Were you home for your solar installation?']
        destination_df['Q#4: Did your crew leader properly introduce themselves?'] = source_df['Q#4: Did your crew leader properly introduce themselves?']
        destination_df['Q#5: Did your crew leader discuss the system design and work to be done with you?'] = source_df['Q#5: Did your crew leader discuss the system design and work to be done with you?']
        destination_df['Q#6: Did a Trinity team member discuss the next steps with you?'] = source_df['Q#6: Did a Trinity team member discuss the next steps with you?']
        destination_df['Q#7: Please provide any additional information to help us improve our work!'] = source_df['Q#7: Please provide any additional information to help us improve our work!']
        destination_df['Q#8: Thank you message'] = source_df['Q#8: Thank you for your feedback and welcome to the Trinity Solar family!']
        destination_df['mkt_tok'] = source_df['mkt_tok']
        destination_df['loc'] = source_df['loc']
        destination_df['Loc2'] = source_df['Loc']
        destination_df['Office'] = source_df['Office']
        destination_df['first_name'] = source_df['first_name']
        destination_df['last_name'] = source_df['last_name']
        destination_df['email'] = source_df['email']
        destination_df['Smartlook URL'] = source_df['Smartlook session']

        output_excel_file = new_report + postinstall_new_report
        destination_df.to_excel(output_excel_file, index=False)

        logger.info(f"Survicate Reports Automation – New Excel file created : {postinstall_new_report}")

    def CreateFloridaReport(self):

        source_file_path = report_download_survicatepath+florida_customer_report+".xlsx"
        source_df = pd.read_excel(source_file_path)

        destination_df = pd.DataFrame()
        destination_df['date'] = source_df['Date & Time (UTC)']
        destination_df['visitor_uuid'] = source_df['Respondent uuid']
        destination_df['page'] = source_df['Page']
        destination_df['Q#1: How satisfied are you with your Trinity Solar experience?'] = source_df['Q#1: How satisfied are you with your Trinity Solar experience?']
        destination_df['Q#2: What could we have done better?'] = source_df['Q#2: What could we have done better?']
        destination_df['Loc'] = source_df['Loc']
        destination_df['Office'] = source_df['Office']
        destination_df['mkt_tok'] = source_df['mkt_tok']
        destination_df['first_name'] = source_df['first_name']
        destination_df['last_name'] = source_df['last_name']
        destination_df['email'] = source_df['email']
        destination_df['Smartlook URL'] = source_df['Smartlook session']

        output_excel_file = new_report + florida_customer_new_report
        destination_df.to_excel(output_excel_file, index=False)

        logger.info(f"Survicate Reports Automation – New Excel file created : {florida_customer_new_report}")


    def CreatePostPTOReport(self):

        source_file_path = report_download_survicatepath+post_pto_report+".xlsx"
        source_df = pd.read_excel(source_file_path,header=[0, 1])

        destination_df = pd.DataFrame()
        destination_df['date'] = source_df['Date & Time (UTC)']
        destination_df['visitor_uuid'] = source_df['Respondent uuid']
        destination_df['page'] = source_df['Page']
        destination_df['Q#1: How likely are you to recommend Trinity Solar to a friend or colleague?'] = source_df[('Q#1: How likely are you to recommend Trinity Solar to a friend or colleague?','Score')]
        destination_df['Q#2: Can you please take a moment to rate each aspect of your experience? (Sales)'] = source_df[('Q#2: Can you please take a moment to rate each aspect of your experience?','Sales')]
        destination_df['Q#2: Can you please take a moment to rate each aspect of your experience? (Installation)'] = source_df[('Q#2: Can you please take a moment to rate each aspect of your experience?','Installation')]
        destination_df['Q#2: Can you please take a moment to rate each aspect of your experience? (Communication)'] = source_df[('Q#2: Can you please take a moment to rate each aspect of your experience?','Communication')]
        destination_df['Q#2: Can you please take a moment to rate each aspect of your experience? (Overall Timeline)'] = source_df[('Q#2: Can you please take a moment to rate each aspect of your experience?','Overall Timeline')]
        destination_df['Q#2: Can you please take a moment to rate each aspect of your experience? (Overall Expectations)'] = source_df[('Q#2: Can you please take a moment to rate each aspect of your experience?','Overall Expectations')]
        destination_df["Q#3: Is there anything we could improve on or that you'd like to add?"] = source_df["Q#3: Is there anything we could improve on or that you'd like to add?"]
        # destination_df[''] = source_df['Q#4: Congrats on going green and making a positive impact on the environment! Help your friends do the same with our referral program and get $1000!']
        destination_df['Q#4: Call-to-action button'] =source_df['Q#4: Congrats on going green and making a positive impact on the environment! Help your friends do the same with our referral program and get $1000!']
        destination_df['Loc'] = source_df['Loc']
        destination_df['Office'] = source_df['Office']
        destination_df['mkt_tok'] = source_df['mkt_tok']
        destination_df['first_name'] = source_df['first_name']
        destination_df['last_name'] = source_df['last_name']
        destination_df['email'] = source_df['email']
        destination_df['Smartlook URL'] = source_df['Smartlook session']

        output_excel_file = new_report + post_pto_new_report
        destination_df.to_excel(output_excel_file, index=False)

        logger.info(f"Survicate Reports Automation – New Excel file created : {post_pto_new_report}")

    def ProcessAutomation(self):
        """All processes will be completed within this function. Report downloads,
        processing, and uploads in SharePoint are done through this function."""
        try:
            file_list = os.listdir(report_download_survicatepath)
            for reportfile in file_list:
                report_file_path = os.path.join(report_download_survicatepath, reportfile)
                os.remove(report_file_path)
                logger.error(f'Survicate Reports Automation – Files "{reportfile}" deleted from survicate report')

            file_list = os.listdir(new_report)
            for reportfile in file_list:
                report_file_path = os.path.join(new_report, reportfile)
                if os.path.isfile(report_file_path):
                    os.remove(report_file_path)
                    logger.error(f'Survicate Reports Automation – Files "{reportfile}" deleted from New report')

            logger.info(f'Survicate Reports Automation - Selenium initialisation..')
            SurvicateBrowser(self.driver).Login()

            time.sleep(15)
            self.CreateDownloadLink(florida_customer_sat,florida_customer_report)
            time.sleep(15)
            self.CreateDownloadLink(postinstall,postinstall_report)
            time.sleep(15)
            self.CreateDownloadLink(post_pto,post_pto_report)
            time.sleep(15)

            # florida_customer_download_link=Outlook().get_survicate_report_mail(florida_customer_report)
            # postinstall_download_link=Outlook().get_survicate_report_mail(postinstall_report)
            # post_pto_download_link=Outlook().get_survicate_report_mail(post_pto_report)

            self.DownloadReport(florida_customer_report)
            time.sleep(8)
            self.rename_latest_file(florida_customer_report)
            self.DownloadReport(postinstall_report)
            time.sleep(8)
            self.rename_latest_file(postinstall_report)
            self.DownloadReport(post_pto_report)
            time.sleep(8)
            self.rename_latest_file(post_pto_report)

            time.sleep(40)
            SurvicateBrowser(self.driver).Logout()

            time.sleep(4)
            self.CreateFloridaReport()
            time.sleep(8)
            self.CreatePostInstallReport()
            time.sleep(8)
            self.CreatePostPTOReport()
            time.sleep(20)
            sharepoint = SharepointConnection()
            sharepoint.url = Survicate_sharepoint_URL
            sharepoint.relative_url = Survicate_sharepoint_relative_URL

            status1 = sharepoint.uploadFile(new_report + florida_customer_new_report, florida_customer_new_report, '')
            logger.info(f'Survicate Reports Automation – File - {florida_customer_new_report} uploaded to sharpoint')
            time.sleep(10)
            status2 = sharepoint.uploadFile(new_report + postinstall_new_report, postinstall_new_report, '')
            logger.info(f'Survicate Reports Automation – File - {postinstall_new_report} uploaded to sharpoint')
            time.sleep(10)
            status3 = sharepoint.uploadFile(new_report + post_pto_new_report, post_pto_new_report, '')
            logger.info(f'Survicate Reports Automation – File - {post_pto_new_report} uploaded to sharpoint')
            time.sleep(10)
            if status1==False or status2==False or status3==False:
                raise AssertionError('Failed to upload file')


        except Exception as ex:
            SurvicateBrowser(self.driver).Logout()
            raise


"""Connect to sharepoint"""
def get_sharepoint_client():
    user_credentials = UserCredential(Sharepoint_userName, Sharepoint_password)
    ctx = ClientContext(Survicate_sharepoint_URL).with_credentials(user_credentials)
    return ctx

"""For sending exception mail"""
def ProcessException(reason=''):
    try:
        failed_reason = ''
        if reason:
            failed_reason = '\nReason : ' + reason
        email = RPA_email()
        email_subject = "Survicate Reports Automation – Failed"
        email_text = (
                "Dear Team,\n\nSurvicate Reports Automation – Failed." + failed_reason + "\n\nThanks and Regards,"
                                                                         "\nRPA Team"
        )
        email.send(exception_email, email_subject, email_text)
    except Exception as mailex:
        logger.error(f'Survicate Reports Automation - Error occurred during execution: {mailex}')
    return

"""For sending sucess mail"""
def ProcessSuccessMail():
    try:
        email = RPA_email()
        email_subject = "Survicate Reports Automation – Success"
        email_text = (
            "Dear Team,\n\nProcess completed successfully.\n\nThanks and Regards,"
            "\nRPA Team"
        )
        email.send(receiver_email, email_subject, email_text)
        logger.info(f'Survicate Reports Automation - Success mail sent.')
    except Exception as ex:
        logger.error(f'Survicate Reports Automation - Error occurred from success mail sending section: {ex}')
        return

"""Main function and scheduler calls this function."""
def Scheduled_task():
    try:
        print("------------------------------start-------------------------------")
        Survicate().ProcessAutomation()
        ProcessSuccessMail()
        logger.info(f'Survicate Reports Automation - Process completed.')

    except Exception as ex:
        logger.error(f'Survicate Reports Automation - Error occurred during execution: {ex}')
        ProcessException(str(ex).strip())
        sleep(1800)
        Scheduled_task()

if __name__ == "__main__":
    logger.info(f'Survicate Reports Automation - Process starting.')

    schedule.every().day.at("03:15").do(Scheduled_task)
    #Scheduled_task()
    #schedule.every().day.at("11:10").do(Scheduled_task)

    while True:
        schedule.run_pending()
        time.sleep(1)
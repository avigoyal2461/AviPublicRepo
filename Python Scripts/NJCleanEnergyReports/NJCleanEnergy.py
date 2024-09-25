#PANDAS VERSION 1.3.1 *****************************************************************
#********************************************************************************
#REQUIRED REQUIRED REQUIRED PANDAS 1.3.1
#PANDAS 1.3.1
#PANDAS 1.3.1
#***************************************************************************
#****************************************************************************
import pandas as pd #1.3.1
import os
from datetime import datetime, date
# import datetime
from CompanyAlias import CONTRACTOR_COMPANIES, OR_CONTRACTOR_COMPANIES, AND_CONTRACTOR_COMPANIES
import dataframe_image as dfi #0.1.5
from reportlab.pdfgen import canvas
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from reportlab.lib.pagesizes import A4, letter
from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image, ImageOps
import glob
import time
# import openpng
import numpy as np
from selenium import webdriver
#pip install excel2img
import excel2img as exi

# ** see if sum can take multiple decimal places - right now it takes none, it would round better if i could take 2 **
# ** SEE LINE 1018 **
#raw pdf save on github : https://github.com/trinity-development/AutoBot/tree/master/assets
"""
GENERATES THE PDF REPORT FOR NJ CLEAN ENERGY
"""

MONTH_CODES = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}
FULL_MONTH_CODES = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

QUARTERS = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9],
    4: [10, 11, 12]
}

LAST_MONTH = datetime.now().month - 1
# LAST_MONTH = 11
# LAST_MONTH = datetime.now().month - 2
INT_LAST_MONTH = datetime.now().month - 1
# INT_LAST_MONTH = 11
# INT_LAST_MONTH = datetime.now().month - 2
#sets a last month integer that does not get converted to a month
TEMP_LAST_MONTH = INT_LAST_MONTH
# TEMP_LAST_MONTH = datetime.now().month - 2

#if month is january, set last month to december rather than "0"
if LAST_MONTH == 0:
    LAST_MONTH = 12
if TEMP_LAST_MONTH == 0:
    TEMP_LAST_MONTH = 12
if INT_LAST_MONTH == 0:
    INT_LAST_MONTH = 12

STRING_LAST_MONTH = str(LAST_MONTH)

LAST_MONTH = MONTH_CODES[LAST_MONTH]
CURRENT_YEAR = datetime.now().year
# CURRENT_YEAR = datetime.now().year - 1
CURRENT_MONTH = datetime.now().month
# CURRENT_MONTH = datetime.now().month - 1
# CURRENT_MONTH = 12
TWO_MONTHS_AGO = datetime.now().month - 2
# TWO_MONTHS_AGO = datetime.now().month - 3
# TWO_MONTHS_AGO = 10

#if month is febuary, set 2 months ago to december
if TWO_MONTHS_AGO == 0:
    TWO_MONTHS_AGO = 12
#if month is january, set 2 months ago to november
# if TWO_MONTHS_AGO == 1:
#     TWO_MONTHS_AGO = 11
if TWO_MONTHS_AGO == -1:
    TWO_MONTHS_AGO = 11
# if TWO_MONTHS_AGO ==

#If the month is January, change current year to the previous year because the report will be for the previous year December.
# if CURRENT_MONTH == 1:
#     CURRENT_YEAR == CURRENT_YEAR - 1

LAST_YEAR = datetime.now().year - 1 #still unused
LAST_FIVE_YEARS = range(CURRENT_YEAR - 5, CURRENT_YEAR + 1)

LAST_TWO_YEARS = CURRENT_YEAR, CURRENT_YEAR - 1

if CURRENT_MONTH == 1:
    # CURRENT_YEAR = CURRENT_YEAR - 1
    CURRENT_YEAR = datetime.now().year - 1
    LAST_YEAR = int(CURRENT_YEAR) - 1
    LAST_FIVE_YEARS = range(CURRENT_YEAR - 5, CURRENT_YEAR + 1)
    LAST_TWO_YEARS = CURRENT_YEAR, CURRENT_YEAR - 1

EXPORT_FOLDER = "C:\SkeduloInfo"
SAVE_FOLDER = "C:\Hold"
#temp file is the first file name for backlog that will save "previous month data"
temp_file_name = f'TOTAL INSTALLS {str(TWO_MONTHS_AGO)}.png'
Previous_Month_backlog_install_path = os.path.join(os.getcwd(), SAVE_FOLDER, temp_file_name)

backlog_quarter_file_name = f'BACKLOG BASED ON RECEIVED {str(TWO_MONTHS_AGO)}.png'
previous_month_quarter_backlog_install_path = os.path.join(os.getcwd(), SAVE_FOLDER, backlog_quarter_file_name)
print(previous_month_quarter_backlog_install_path)

# EXPORT_FOLDER = r'./temp'


class NJCleanEnergy:
    """
    An NJ Clean Energy report generator.
    """
    # TEST_INSTALLATION_REPORT_PATH = r'C:\SkeduloInfo\install.xlsx'
    # TEST_PIPELINE_REPORT_PATH = r'C:\SkeduloInfo\pipeline.xlsx'
    # TEST_INSTALLATION_REPORT_PATH = r'./assets/install.xlsx'
    # TEST_PIPELINE_REPORT_PATH = r'./assets/pipeline.xlsx'

    def __init__(self) -> None:
        #make sure pandas is running 1.3.1
        self.download_reports()
        #make sure pandas is running 1.3.1
        #make sure pandas is running 1.3.1
        # print(Image.__version__)
        # exit()

        # self.pipeline_df = pd.read_excel(xlsx_paths['pipeline'], sheet_name='TI - PIPELINE')
        # self.installation_df = pd.read_excel(xlsx_paths['install'], sheet_name='TI - INSTALLED')

        list_of_files_after_download = glob.glob('C:\Hold\*.xlsx')
        self.list_files = list_of_files_after_download

        # list_after_clean = glob.glob(r'C:\Users\dood2\Desktop\AtomPython\MY_NJCE\*.xlsx')
        # print(f"THIS IS THE LIST: {list_after_clean}")
        # self.installation_df = pd.read_excel(list_of_files_after_download[0], sheet_name= 'TI - INSTALLED')
        # self.pipeline_df = pd.read_excel(list_of_files_after_download[1], sheet_name='TI - PIPELINE
        # print(self.list_files)
        # exit()
        # print(list_of_files_after_download)
        self.installation_df = pd.read_excel(list_of_files_after_download[0], sheet_name= 'TI - Installed')
        self.installationADI_df = pd.read_excel(list_of_files_after_download[0], sheet_name='ADI - Installed')
        self.pipeline_df = pd.read_excel(list_of_files_after_download[1], sheet_name='TI - PIPELINE')
        self.pipelineADI_df = pd.read_excel(list_of_files_after_download[1], sheet_name='ADI - PIPELINE')

        # self.installation_df = pd.read_excel(list_after_clean, sheet_name= 'TI - Installed')
        # self.pipeline_df = pd.read_excel(list_after_clean[1], sheet_name='TI Pipeline')


        print('Updating columns...')
        self.set_installation_columns()
        self.set_installationADI_columns()
        self.set_pipeline_columns()
        self.set_pipelineADI_columns()
        self.convert_company_aliases(self.installation_df)
        self.convert_company_aliases(self.installationADI_df)
        self.convert_company_aliases(self.pipeline_df)
        self.convert_company_aliases(self.pipelineADI_df)
        # print(self.installation_df[])
        self.unique_pipeline_companies = self.pipeline_df['Contractor_Company'].unique()
        self.unique_pipelineADI_companies = self.pipelineADI_df['Contractor_Company'].unique()
        list1 = list(self.unique_pipeline_companies)
        list2 = list(self.unique_pipelineADI_companies)
        self.unique_pipeline_companies = list1 + list2
        self.unique_pipeline_companies = [*set(self.unique_pipeline_companies)]

        self.unique_companies = self.installation_df['Contractor_Company'].unique()
        self.unique_companiesADI = self.installationADI_df['Contractor_Company'].unique()
        list1 = list(self.unique_companies)
        list1 = list(self.unique_companiesADI)
        self.unique_companies = list1 + list2
        self.unique_companies = [*set(self.unique_companies)]
        # self.unique_companies = self.installation_df['Contractor_Company'].unique()
        # print(self.unique_companies)
        # for value in self.unique_companies:
        #     print(value)
        # quit()
        # self.unique_interconnections = self.pipeline_df['Interconnection_Type'].unique()
        # self.unique_interconnections = self.pipelineADI_df['Interconnection_Type'].unique()
        self.unique_interconnections = self.installation_df['Interconnection_Type'].unique()
        print(self.unique_interconnections)
        # quit()
        # [
        #     'TI_Application_Number',
        #     # 'SRP Registration_Number',
        #     'Program',
        #     'Premise_Last_Name',
        #     'Premise_Company',
        #     'Premise_Installation_Address_Commercial_Only',
        #     'Premise_City',
        #     'Premise_Zip',
        #     'County_Code',
        #     'Calculated_Total_System_Size',
        #     'Customer_Type',
        #     # 'Third_Party_Ownership',
        #     # 'Grid_BTM',
        #     # "Interconnection_Type"
        #     'Interconnection_Type',
        #     'Third Party Ownership',
        #     'Project_Type',
        #     'Land_Use_Type'
        #     'Subsection',
        #     'EDC_Program',
        #     'Contractor_Company',
        #     'Electric_Utility_Name',
        #     'Status',
        #     # "Land_Use_Type",
        #     'Application_Received_Date',
        #     # 'Registration_Received_Date',
        #     'Acceptance_Date',
        #     'Expiration_Date',
        #     # 
        self.unique_install_type = self.pipeline_df['Customer_Type'].unique()
        # print("--------------------------")
        # print(self.pipeline_df.columns)
        # print(self.pipeline_df['Interconnection_Type'])
        # print(self.pipeline_df['Third Party Ownership'])
        # print(self.pipeline_df['Project_Type'])
        # print(self.pipeline_df['Land_Use_Type'])
        # print(self.pipeline_df['Subsection'])
        # print(self.pipeline_df['EDC_Program'])
        # print(self.pipeline_df['Contractor_Company'])
        # print(self.pipeline_df['Electric_Utility_Name'])
        # print(self.pipeline_df['Status'])
        # print(self.pipeline_df['Application_Received_Date'])
        # # print(self.unique_interconnections)
        # quit()
        # exit()

    def download_reports(self):
        """
        Downloads the reports from the solar data website
        """
        # chrome_options = webdriver.ChromeOptions()
        chrome_options = Options()
        prefs = {'download.default_directory' : 'C:\Hold'}
        # chrome_options.add_experimental_option("detach", True)
        # chrome_options.add_argument(prefs)
        chrome_options.add_experimental_option('prefs', prefs)
        # chrome_options.add_experimental_option('prefs', prefs)
        print("Selected Download Folder")

        # driver = webdriver.Chrome(ChromeDriverManager().install())#, options=chrome_options)
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        # driver = webdriver.Chrome(executable_path="C:\ChromeDriver\chromedriver.exe", chrome_options=chrome_options)
        # driver = webdriver.Chrome(executable_path="C:\ChromeDriver\chromedriver.exe", options=chrome_options)

        print("Successfully initiated chromedriver")

        # driver.maximize_window()
        #NJ CLEAN ENERGY DATA
        driver.get("http://www.njcleanenergy.com/SRPREPORTS")

        time.sleep(2)
        # driver.find_element(by=By.XPATH, value='//*[@id="emc"]').click()
        # driver.find_element_by_xpath('fauydvuy uyv')
        driver.find_element(by=By.XPATH, value='//*[@id="content"]/div[4]/div/ul[2]/li[1]/a').click()
        print("Downloading Install Images...")
        time.sleep(3)

        #xpath is found by right clicking the element, and copying xpath link : inspect, right click the highlighted element, copy, copy xpath link
        # driver.find_element('//*[@id="content"]/div[4]/div/ul[2]/li[4]/a').click() #pipeline data
        driver.find_element(by=By.XPATH, value='/html/body/div/div[5]/div[4]/div/ul[2]/li[4]/div/a').click()
        print("Downloading Pipeline...")
        # time.sleep(3)

        driver.find_element(by=By.XPATH, value='//*[@id="content"]/div[4]/div/ul[2]/li[2]/a').click() #installation data
        print("Downloading Installed...")
        time.sleep(10)

        print("Waiting 60 seconds...")
        time.sleep(60)
        #await <--- waits for the download to finish
        print("Quitting Chrome...")
        driver.quit()

    def pre_gen_path_tpo(self):
        """
        Creates and returns the image path of the TPO Count,
        This image is found from the Installation Data Excel, pregenerated image
        """
        tpo_name = "tpo.png"

        tpo_folder = os.path.join(os.getcwd(), EXPORT_FOLDER, tpo_name)
        print(self.list_files[2])
        # file_path = self.list_files[]
        tpo_image_path = exi.export_img(self.list_files[2], tpo_folder, "TPO Summary", None)
        time.sleep(3)
        tpo_image_path = os.path.join(os.getcwd(), EXPORT_FOLDER, tpo_name)
        print(tpo_image_path)
        time.sleep(3)
        # tpo = tpo_image_path.save(tpo_name)

        return tpo_image_path

    def pre_gen_path_installation(self):
        """
        Creates and returns the image path of the Installation Count by County,
        This image is found from the Installation Data Excel, pregenerated image
        """

        installation_name = 'installation.png'

        installation_folder = os.path.join(os.getcwd(), EXPORT_FOLDER, installation_name)
        time.sleep(3)
        installation_count_image_path = exi.export_img(self.list_files[2], installation_folder, "Installations by County", None)
        time.sleep(3)
        installation_county_image_path = os.path.join(os.getcwd(), EXPORT_FOLDER, installation_name)

        return installation_county_image_path

    def generate_report_images(self) -> list: #generate_install_count_by_type_year
        """
        Generate the report table images, returning a list of the photo paths.
        """
        # Install Count By Year
        print('Generating images for Install Count By Year And Quarters...')
        install_sum_yearly_path = self.generate_install_sum_report_yearly_image()
        install_sum_quarterly_path = self.generate_install_sum_report_quarterly_image(CURRENT_YEAR)
        install_sum_quarterly_previous_year_path = self.generate_install_sum_report_quarterly_image(CURRENT_YEAR - 1)
        #creates a global self variable allowing for check further down in order to keep these tables the same size
        self.install_sum_quarterly_path = install_sum_quarterly_path
        self.install_sum_quarterly_previous_year_path = install_sum_quarterly_previous_year_path

        # Install Count By Month
        print('Generating images for Install Count By Month...')
        install_sum_path = self.generate_install_sum_report_image(CURRENT_YEAR)
        install_sum_previous_year_path = self.generate_install_sum_report_image(CURRENT_YEAR - 1)

        #Installed Count by Type and Year
        print('Generating images for Install Count by Type and Year')
        install_count_type = self.generate_install_count_by_type_year()

        # Installed kW Monthly
        print('Generating images for Installed kW Monthly...')
        system_size_monthly_path = self.generate_installed_system_size_report_image(CURRENT_YEAR)
        system_size_monthly_previous_year_path = self.generate_installed_system_size_report_image(CURRENT_YEAR - 1)

        #Installed Type Last five Years
        print('Generating images for Installed Type for Last five years...')
        install_type_five_years = self.generate_install_count_by_type_year()

        #Installed kW Yearly
        print('Generating images for Installed kW Yearly...')
        total_size_yearly_path = self.generate_system_size_report_image_yearly()

        # Installed kW Grid/BTM
        print('Generating images for Installed kW Grid/BTM...')
        size_per_connection_path = self.generate_system_size_per_connection_report_image()

        # Third Party Owned
        print('Generating images for Third Party Owned...')
        third_party_path = self.generate_third_party_ownership_report_image()

        # Average Acceptance PTO
        print('Generating images for Average Acceptance PTO...')
        pto_path = self.generate_pto_report_image()

        #total install by recieved date
        print('Generating images for Average Installs by Received Date...')
        received_date_installs_path = self.generate_install_count_by_recieved_date()
        self.received_date_installs_path = received_date_installs_path

        print("Generating Images for Backlog Installs Based on Received Date...")
        backlog_received_path = self.generate_backlog_by_quarter_based_on_recieved()
        self.backlog_received_path = backlog_received_path
        #backlog, kw size
        print('Generating Images for Backlog kw by Receieved Date...')
        backlog_kw_path = self.generate_backlog_kw()

        return {
            'Install Count By Year': [
                install_sum_yearly_path,
                install_sum_quarterly_path,
                install_sum_quarterly_previous_year_path,

            ],
            'Install Count By Month': [
                install_sum_path,
                install_sum_previous_year_path
            ],
            'Install Count by Type': [
                install_count_type
            ],
            'Installed kW Monthly': [
                system_size_monthly_path,
                system_size_monthly_previous_year_path
            ],
            'Installed kW Yearly': [
                total_size_yearly_path
            ],
            'Installed kW Grid/BTM': [
                size_per_connection_path
            ],
            'Third Party Owned': [
                third_party_path
            ],
            'Average Acceptance PTO': [
                pto_path
            ],
            'Installs by Recieved Date': [
                received_date_installs_path,
                Previous_Month_backlog_install_path
                #INPUT LAST MONTH REPORT'S IMAGE PATH, AND SAVE THIS MONTH'S PATH TO THAT FOLDER, AND THEN REMOVE IT
            ],
            'Backlog Installs based on Receieved Date':[
                backlog_received_path,
                previous_month_quarter_backlog_install_path
            ],
            'Backlog KW based on Receieved Date':[
                backlog_kw_path
            ]
        }

    def set_installation_columns(self) -> None:
        # print(self.installation_df.shape)
        # print(self.installation_df.columns)
        # quit()
        self.installation_df.columns = [
            'Project_Number',
            'Program',
            'Premise_Last_Name',
            # 'TI_Application_Number',
            # 'Registration_Number',
            'Premise_Company',
            'Premise_Installation_Address_Commercial_Only',
            'Premise_City',
            'Premise_Zip',
            'County_Code',
            'PTO_Date',
            'Calculated_Total_System_Size',
            'Customer_Type',
            'Interconnection_Type',
            'Third_Party_Ownership',
            # 'Grid_BTM',
            'Project_Type',
            'Land_Use_Type',
            'Subsection',
            'Self_Install',
            # 'EDC_Program',
            'Contractor_Company',
            'Electric_Utility_Name',
            'Status',
            'Registration_Received_Date',
            'Acceptance_Date',
            'Completion_Date'
        ]
        self.installation_df['Installs'] = 1
        # self.installation_df['PTO_Date'] = pd.to_datetime(self.installation_df['PTO_Date'])
        # self.installation_df['Acceptance_Date'] = pd.to_datetime(self.installation_df['Acceptance_Date'], format='%Y-%m-%d')
        print(self.installation_df['Acceptance_Date'])
        print(self.installation_df['PTO_Date'])
        # pto = pd.to_datetime(self.installation_df['PTO_Date'], format='%Y-%m-%d').dt.date
        # self.installation_df['Acceptance_Date'] = self.installation_df['Acceptance_Date'].apply(pd.to_datetime)
        # self.installation_df['PTO_Date'] = self.installation_df['PTO_Date'].apply(pd.to_datetime)
        
        ################################################# DATETIME FIX
        values = []
        for row in self.installation_df['PTO_Date']:
            try:
                row = str(row)
                row = row.split(" ")[0]
                datetime_object = datetime.strptime(row, '%Y-%m-%d')
            except Exception as e:
                datetime_object = row
            # print(datetime_object)
            values.append(datetime_object)

        self.installation_df['temp_pto'] = values
        self.installation_df.drop('PTO_Date', axis=1)
        self.installation_df['PTO_Date'] = self.installation_df['temp_pto'].apply(pd.to_datetime)
        ##################################################

        # self.installation_df['PTO_Date'] = self.installation_df['PTO_Date'].apply(pd.to_datetime)
        self.installation_df['PTO_Acceptance_Days'] = (
            self.installation_df['PTO_Date'] - self.installation_df['Acceptance_Date']).dt.days
        # self.installation_df['PTO_Acceptance_Days'] = (
        #     pto - self.installation_df['Acceptance_Date']).dt.days
        print(self.installation_df['PTO_Date'])

    def set_installationADI_columns(self) -> None:
        self.installationADI_df.columns = [
            'ADI_Application_Number',
            'Program',
            # 'Registration_Number',
            'Premise_Last_Name',
            'Premise_Company',
            'Premise_Installation_Address_Commercial_Only',
            'Premise_City',
            'Premise_Zip',
            'County_Code',
            'PTO_Date',
            'Calculated_Total_System_Size',
            'Customer_Type',
            'Interconnection_Type',
            'Third_Party_Ownership',
            # 'Grid_BTM',
            'Project_Type',
            'Land Use Type',
            'Subsection',
            'Self_Install',
            # 'EDC_Program',
            'Contractor_Company',
            'Electric_Utility_Name',
            'Status',
            # 'Subsection',
            # 'Energy Year',
            # 'Contractor_Company',
            # 'Application_Received_Date'
            'Registration_Received_Date',
            'Acceptance_Date',
            'Completion_Date'
        ]
        self.installationADI_df['Installs'] = 1
        self.installationADI_df['PTO_Acceptance_Days'] = (
            self.installationADI_df['PTO_Date'] - self.installationADI_df['Acceptance_Date']).dt.days
        
        print(self.installationADI_df['PTO_Acceptance_Days'])
        # quit()pip 

        # print(self.installationADI_df['PTO_Date'])
        # quit()
    def set_pipeline_columns(self) -> None:
        """
        Set column values for the xlsx dataframe.
        """
        self.pipeline_df.columns = [
            # 'SRP Registration_Number',
            'TI_Application_Number',
            'Program',
            'Premise_Last_Name',
            'Premise_Company',
            'Premise_Installation_Address_Commercial_Only',
            'Premise_City',
            'Premise_Zip',
            'County_Code',
            'PTO'
            'Calculated_Total_System_Size',
            'Customer_Type',
            # 'Third_Party_Ownership',
            # 'Grid_BTM',
            # "Interconnection_Type"
            'Interconnection_Type',
            'Third Party Ownership',
            'Project_Type',
            'Land_Use_Type',
            'Subsection',
            'Self_Install',
            # 'EDC_Program',
            'Contractor_Company',
            'Electric_Utility_Name',
            'Status',
            # "Land_Use_Type",
            'Registration_Received_Date',
            'Application_Received_Date',
            'Acceptance_Date',
            'Expiration_Date',
            # 'Placeholder'
        ]
        self.pipeline_df['Installs'] = 1
        # self.pipeline_df['PTO_Acceptance_Days'] = (
        #     self.pipeline_df['PTO_Date'] - self.pipeline_df['Acceptance_Date']).dt.days

    def set_pipelineADI_columns(self) -> None:
        """
        Set column values for the xlsx dataframe.
        """
        self.pipelineADI_df.columns = [
            'ADI_Application_Number',
            'Program',
            # 'Registration_Number', #(Transferred to TI)
            'Premise_Last_Name',
            'Premise_Company',
            'Premise_Installation_Address', #(Commercial Only)
            'Premise_City',
            'Premise_Zip',
            'County_Code',
            # 'PTO',
            'Calculated_Total_System_Size',
            'Customer_Type',
            'Interconnection_Type',
            'Third_Party_Ownership',
            'Project_Type',
            'Land_Use_Type',
            'Subsection',
            'Self_Install',
            # 'EDC_Program',
            'Contractor_Company',
            'Electric_Utility_Name',
            'Status',
            'Registration_Received_Date',
            'Application_Received_Date',
            'Acceptance_Date',
            'Expiration_Date'
        ]
        # self.pipelineADI_df.columns = [
        #     'ADI_Application_Number',
        #     # 'Registration_Number',
        #     'Program',
        #     'Premise_Last_Name',
        #     'Premise_Company',
        #     'Premise_Installation_Address_Commercial_Only',
        #     'Premise_City',
        #     'Premise_Zip',
        #     'County_Code',
        #     'Calculated_Total_System_Size',
        #     'Customer_Type',
        #     'Interconnection_Type',
        #     'Third_Party_Ownership',
        #     # 'Grid_BTM',
        #     # "Interconnection_Type"
        #     'Third Party Ownership'
        #     'Project_Type',
        #     # 'Subsection',
        #     "Land_Use_Type",
        #     'EDC_Program',
        #     'Contractor_Company',
        #     'Electric_Utility_Name',
        #     'Status',
        #     'Application_Received_Date',
        #     # 'Registration_Received_Date',
        #     'Acceptance_Date',
        #     'Expiration_Date',
        #     # 'Placeholder'
        # ]
        self.pipelineADI_df['Installs'] = 1

    def convert_company_aliases(self, df) -> None:
        """
        Converts all the Contractor Company names to the format expected for the dataframe.
        """
        # Direct company aliasing
        for contractor_company in CONTRACTOR_COMPANIES:
            df.loc[df['Contractor_Company'].str.contains(
                contractor_company, na=False, case=False), 'Contractor_Company'] = CONTRACTOR_COMPANIES[contractor_company]

        # Specific case company aliasing
        df.loc[(df['Contractor_Company'].str.contains('Solar Energy Systems', na=False, case=False)) & (
            ~df['Contractor_Company'].str.contains('Arosa', na=False, case=False)), 'Contractor_Company'] = 'Solar Energy Systems'
        df.loc[(df['Contractor_Company'].str.contains('Pro Custom', na=False, case=False)) & (
            ~df['Contractor_Company'].str.contains('Momentum', na=False, case=False)), 'Contractor_Company'] = 'Pro Custom Solar'
        df.loc[(df['Contractor_Company'].str.contains('Solar Me', na=False, case=False)) & (
            ~df['Contractor_Company'].str.contains('Medix', na=False, case=False)), 'Contractor_Company'] = 'Solar Me'
        df.loc[(df['Contractor_Company'].str.contains('DC Solar', na=False, case=False)) & (
            ~df['Contractor_Company'].str.contains('AC', na=False, case=False)), 'Contractor_Company'] = 'DC Solar'
        df.loc[(df['Contractor_Company'].str.contains('SI Solar', na=False, case=False)) & (
            ~df['Contractor_Company'].str.contains('ISI', na=False, case=False)), 'Contractor_Company'] = 'SI Solar'
        df.loc[(df['Contractor_Company'].str.contains('Smart Energy', na=False, case=False)) & (
            ~df['Contractor_Company'].str.contains('Northeast', na=False, case=False)), 'Contractor_Company'] = 'Smart Energy Group'

        # Multiple Part Company Aliasing
        for and_contractor_company in AND_CONTRACTOR_COMPANIES:
            first_query = AND_CONTRACTOR_COMPANIES[and_contractor_company][0]
            second_query = AND_CONTRACTOR_COMPANIES[and_contractor_company][1]
            search_query = (df['Contractor_Company'].str.contains(first_query, na=False, case=False)) & (
                df['Contractor_Company'].str.contains(second_query, na=False, case=False))
            df.loc[search_query,
                   'Contractor_Company'] = and_contractor_company

        # Conditional Part Company Aliasing
        for or_contractor_company in OR_CONTRACTOR_COMPANIES:
            first_query = OR_CONTRACTOR_COMPANIES[or_contractor_company][0]
            second_query = OR_CONTRACTOR_COMPANIES[or_contractor_company][1]
            search_query = (df['Contractor_Company'].str.contains(first_query, na=False, case=False)) | (
                df['Contractor_Company'].str.contains(second_query, na=False, case=False))
            df.loc[search_query,
                   'Contractor_Company'] = or_contractor_company

    def get_install_sum_report_yearly(self):
        """
        Get a dataframe representing the top 10 sum of installs for current year, with past
        5 years data.
        Sheet 1.
        """
        # Years in ascending order starting 5 years ago.
        years = [str(year) for year in LAST_FIVE_YEARS]
        columns = ["Company"] + years + ['Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)
        # Add installs per company
        for company in self.unique_companies:
            data = {'Company': company}
            for year in LAST_FIVE_YEARS:
                installs = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                     (self.installation_df['PTO_Date'].dt.year == year)), "Installs"].sum()
                temp = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                    (self.installationADI_df['PTO_Date'].dt.year == year)), "Installs"].sum()

                installs = installs + temp
                data[str(year)] = installs
            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)

        df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        df['Company'] = df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total

        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def generate_install_sum_report_yearly_image(self) -> str:
        """
        Creates a table image for the install sum yearly report. Returns image path.
        finished
        """
        STRING_CURRENT_YEAR = str(CURRENT_YEAR)

        df_styled = self.get_install_sum_report_yearly()

        second_high = df_styled[STRING_CURRENT_YEAR].values[0] #finds the second highest value (this is the highest value that is not the total) in order to pick the max value the gradient is applied to
        second_high = int(second_high)

        highest_value = df_styled[STRING_CURRENT_YEAR].max() #finds the max value (the total) in order to apply the green color
        highest_value = int(highest_value)

        df_styled = df_styled.style.background_gradient(axis=0, subset=STRING_CURRENT_YEAR, vmax=second_high, cmap='YlOrRd')
        # df_styled.set_caption(f"ALL INSTALL COUNT BY YEAR")
        # df.style.set_table_attributes("style='display:inline'").set_caption('Caption table')
        # df_styled = df_styled.set_table_attributes("font-weight:'bold'").set_caption(f"test")
        # df_styled = df_styled.set_title("TEST")
        df_styled = df_styled.set_caption(f"ALL INSTALL COUNT BY YEAR").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])

        df_styled.apply(lambda x: ['border: 2px solid black' if v == " " else 'border: 2px solid black' for v in x], axis=1)
        df_styled.apply(lambda x: ['background-color: green' if v == highest_value else 'border: 2px solid black' for v in x], axis=1)

        file_name = f'TOTAL INSTALLS YEARLY {str(CURRENT_YEAR)}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path

    def get_install_sum_report_quarterly(self, year):
        """
        Creates a dataframe with top 10 companies by install total, with installs per quarter.
        Sheet 2.
        """
        quarter_cols = ['Q' + str(quarter) for quarter in QUARTERS]
        columns = ["Company"] + quarter_cols + ['Total']
        df = pd.DataFrame(columns=columns)

        for company in self.unique_companies:
            data = {'Company': company}
            for quarter in QUARTERS:
                installs = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                     (self.installation_df['PTO_Date'].dt.month.isin(QUARTERS[quarter])) &
                                                     (self.installation_df['PTO_Date'].dt.year == year)), "Installs"].sum()

                temp = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                     (self.installationADI_df['PTO_Date'].dt.month.isin(QUARTERS[quarter])) &
                                                     (self.installationADI_df['PTO_Date'].dt.year == year)), "Installs"].sum()
                installs = temp + installs
                data['Q' + str(quarter)] = installs
            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)

        df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        df['Company'] = df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total

        df = df.reset_index(drop=True)

        return df.astype(int, errors='ignore')

    def generate_install_sum_report_quarterly_image(self, year) -> str:
        """
        Creates a table image for the install sum quarterly report. Returns image path.
        finished
        """
        CURRENT_YEAR_STRING = str(CURRENT_YEAR)
        df_styled = self.get_install_sum_report_quarterly(year)

        second_high = df_styled['Total'].values[0] #finds the second highest value (this is the highest value that is not the total) in order to pick the max value the gradient is applied to
        second_high = int(second_high)
        highest_value = df_styled['Total'].max() #finds the max value (the total) in order to apply the green color
        highest_value = int(highest_value)

        df_styled = df_styled.style.background_gradient(axis=0, subset='Total', vmax=second_high, cmap='YlOrRd')
        df_styled.apply(lambda x: ['background-color: green' if v == highest_value else 'border: 2px solid black' for v in x], axis=1)

        # df_styled = df_styled.style.background_gradient(axis=0, subset='Total', cmap='YlOrRd')
        df_styled = df_styled.set_caption(f"INSTALL COUNT ({year}),BY QUARTER - BASED ON PTO DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled.set_caption(f"INSTALL COUNT ({year}),BY QUARTER - BASED ON PTO DATE")
        df_styled.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)

        file_name = f'TOTAL INSTALLS QUARTERLY {year}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path

    def get_install_sum_report_monthly(self, year):
        """
        Creates a dataframe with top 10 companies by install total, with installs per month for current
        year and last year.
        Sheet 4.
        """
        months = [MONTH_CODES[month_code] for month_code in MONTH_CODES]
        columns = ["Company"] + months + ['Total']
        df = pd.DataFrame(columns=columns)
        for company in self.unique_companies:
            data = {'Company': company}
            for month in MONTH_CODES:
                installs = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                     (self.installation_df['PTO_Date'].dt.month == month) &
                                                     (self.installation_df['PTO_Date'].dt.year == year)), "Installs"].sum()

                temp = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                     (self.installationADI_df['PTO_Date'].dt.month == month) &
                                                     (self.installationADI_df['PTO_Date'].dt.year == year)), "Installs"].sum()
                installs = temp + installs
                data[MONTH_CODES[month]] = installs
            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)

        # df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        # df['Company'] = df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total

        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def generate_install_sum_report_image(self, year) -> str:
        """
        Creates a table image for the install sum report. Returns image path.
        finished
        """
        df_styled = self.get_install_sum_report_monthly(year)

        # second_high = df_styled[LAST_MONTH].values[0] #finds the second highest value (this is the highest value that is not the total) in order to pick the max value the gradient is applied to
        # second_high = int(second_high)
        # highest_value = df_styled[LAST_MONTH].max() #finds the max value (the total) in order to apply the green color
        # highest_value = int(highest_value)

        # df_styled = df_styled.style.background_gradient(axis=0, subset=LAST_MONTH, vmax=highest_value - 1, cmap='YlOrRd')
        # df_styled.apply(lambda x: ['background-color: green' if v == highest_value else 'border: 2px solid black' for v in x], axis=1)

        df_styled = df_styled.style.background_gradient(axis=0, subset=LAST_MONTH, cmap='YlOrRd')
        df_styled = df_styled.set_caption(f"ALL INSTALL COUNT ({year}) - BASED ON PTO DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled.set_caption(f"ALL INSTALL COUNT ({year}) - BASED ON PTO DATE")
        df_styled.apply(lambda x: ['border: 2px solid black' if v == ' ' else 'border: 2px solid black' for v in x], axis = 1)

        file_name = f'TOTAL INSTALLS MONTHLY {year}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path

    def get_install_count_by_type_year(self):
        """
        Creates a df checking for the top 5 companies with based on installation types
        Takes a long time to run, 
        finished
        """
        # self.unique_install_type
        temp_install_type = 'Residential'
        years = [str(year) for year in LAST_TWO_YEARS]
        columns = ["Company"] + years + ['Total']
        columns_index = ["Company"] + ['Install_Type'] + years + ['Total'] + ['Index']
        reset_column = ["Company"] + ['Install Type'] + years + ['Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)

        #this df finds the top performers with residential, then uses the companies found to determine how they perform with the other install types, then removes nan
        for company in self.unique_companies:
            data = {'Company': company,
                    'Install_Type': temp_install_type
                    }
            for year in LAST_TWO_YEARS:
                installs = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                     (self.installation_df['PTO_Date'].dt.year == year) &
                                                     (self.installation_df['Customer_Type'].str.contains(temp_install_type))), "Installs"].sum()

                temp = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                     (self.installationADI_df['PTO_Date'].dt.year == year) &
                                                     (self.installationADI_df['Customer_Type'].str.contains(temp_install_type))), "Installs"].sum()
                installs = temp + installs
                data[str(year)] = installs
            df = df.append(data, ignore_index=True)

        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        #takes top 6 companies in the residential area
        top_five_df = df.nlargest(6, 'Total')
        # Convert float to int for presentation
        top_five_df["Total"] = top_five_df["Total"].astype(int)

        df = top_five_df.dropna()
        df = df.reset_index(drop=True)

        #indexes all the companies in the top 6 df, this is to help combine the rest of the install types
        index_list = []
        x = 1
        while x <= df.shape[0]:
            index_list.append(x)
            x += 1
        df['Index'] = index_list
        #resort df by total
        df = df.nlargest(6, 'Total')
        #init the new df that will take the top companies and fill information about their other install types.
        top_company_list = df['Company']
        #df_temp is the value of the rest of the install types (not residential) of the top 6 performing companies, this temp df is used to merge with the main df to return the top 6 companies all install type installs
        df_temp = pd.DataFrame(columns=columns)

        for install_type in self.unique_install_type:
            for company in top_company_list:
                data = {'Company': company,
                        'Install_Type': install_type
                        }
                for year in LAST_TWO_YEARS:
                    try:
                        installs = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                            (self.installation_df['PTO_Date'].dt.year == year) &
                                                            (self.installation_df['Customer_Type'].str.contains(install_type))), "Installs"].sum()

                        temp = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                            (self.installationADI_df['PTO_Date'].dt.year == year) &
                                                            (self.installationADI_df['Customer_Type'].str.contains(install_type))), "Installs"].sum()
                    except:
                        installs = 0
                        temp = 0
                    installs = temp + installs
                    data[str(year)] = installs
                df_temp = df_temp.append(data, ignore_index=True)
        df_temp["Total"] = df_temp[columns[1:-1]].sum(axis=1)
        df_temp["Total"] = df_temp["Total"].astype(int)
        df_temp = df_temp.dropna()

        #remove values equal to 0, or residential
        df_temp = df_temp[df_temp.Total != 0]
        df_temp = df_temp[df_temp.Install_Type != 'Residential']

        #assign index values to the temp df, this will be used to merge and sort the final df
        x = 0
        index_list = []
        temp_company_list = []
        temp_company_list = df_temp['Company']
        temp_company_list = list(temp_company_list)
        top_company_list = list(top_company_list)

        for company in temp_company_list:
            if company in top_company_list:
                the_index = df.loc[df["Company"] == company, "Index"]

                the_index = int(the_index)
                index_list.append(the_index)

        df_temp['Index'] = index_list
        concat_df = df.append(df_temp)
        concat_df = concat_df.sort_values(['Index', 'Total'], ascending=[True, False])

        concat_df = concat_df.drop(columns=["Index"])

        # concat_df.loc['Column_Total']= concat_df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        # concat_df['Company'] = concat_df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total

        concat_df = concat_df.reset_index(drop=True)
        concat_df = concat_df.rename(columns={"Install_Type": "Install Type"})
        concat_df = concat_df[reset_column]

        # print(concat_df)
        return concat_df.astype(int, errors='ignore')

    def generate_install_count_by_type_year(self):
        """
        Creates an image for the install type (residential, municipal, commercial etc)
        finished
        """
        STRING_CURRENT_YEAR = str(CURRENT_YEAR)
        df_styled = self.get_install_count_by_type_year()

        # second_high = df_styled[STRING_CURRENT_YEAR].values[0] #finds the second highest value (this is the highest value that is not the total) in order to pick the max value the gradient is applied to
        # second_high = int(second_high)
        # highest_value = df_styled[STRING_CURRENT_YEAR].max() #finds the max value (the total) in order to apply the green color
        # highest_value = int(highest_value)
        #
        # df_styled = df_styled.style.background_gradient(axis=0, subset=STRING_CURRENT_YEAR, vmax=second_high, cmap='YlOrRd')
        # df_styled.apply(lambda x: ['background-color: green' if v == highest_value else 'border: 2px solid black' for v in x], axis=1)
        df_styled = df_styled.style.background_gradient(axis=0, subset=STRING_CURRENT_YEAR, cmap='YlOrRd')
        df_styled = df_styled.set_caption(f"INSTALL COUNT BY TYPE & YEAR - BASED ON PTO DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled = df_styled.set_caption(f"INSTALL COUNT BY TYPE & YEAR - BASED ON PTO DATE")
        df_styled = df_styled.apply(lambda x: ['border: 2px solid black' if v == ' ' else 'border: 2px solid black' for v in x], axis = 1)
        file_name = f'INSTALL COUNT BY TYPE AND YEAR.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path


    def get_sum_of_installed_system_size_report(self, year):
        """
        Creates a dataframe with the total sum of system size by month. Creates for year given.
        Sheet 6.
        """
        months = [MONTH_CODES[month_code] for month_code in MONTH_CODES]
        columns = ["Company"] + months + ['Total']
        df = pd.DataFrame(columns=columns)
        for company in self.unique_companies:
            data = {'Company': company}
            for month in MONTH_CODES:
                total_system_size = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                              (self.installation_df['PTO_Date'].dt.month == month) &
                                                              (self.installation_df['PTO_Date'].dt.year == year)), "Calculated_Total_System_Size"].sum()

                temp_total_system_size = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                              (self.installationADI_df['PTO_Date'].dt.month == month) &
                                                              (self.installationADI_df['PTO_Date'].dt.year == year)), "Calculated_Total_System_Size"].sum()

                total_system_size = temp_total_system_size + total_system_size
                data[MONTH_CODES[month]] = total_system_size
            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)
        df = df.reset_index(drop=True)

        return df.astype(int, errors='ignore')

    def generate_installed_system_size_report_image(self, year) -> str:
        """
        Creates a table image for the total system size. Returns image path.
        """
        df_styled = self.get_sum_of_installed_system_size_report(year)
        df_styled = df_styled.style.background_gradient(axis=0, subset=LAST_MONTH, cmap='YlOrRd')
        df_styled = df_styled.set_caption(f"INSTALLED kW, BASED ON PTO DATE ({year})").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled = df_styled.set_caption(f"INSTALLED kW, BASED ON PTO DATE ({year})")
        df_styled.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis = 1)
        # df_styled.apply(lambda x: [
        #                 'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)
        file_name = f'TOTAL SIZE MONTHLY {year}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        # dfi.export(df_styled, export_path, table_conversion='matplotlib')
        return export_path

    def get_third_party_ownership_yearly(self):
        """
        Get a dataframe representing the count per year of third party installs
        for the last five years.
        Sheet 7.
        """
        # Years in ascending order starting 5 years ago.
        columns = ['Year', 'No', 'Yes', 'Total']
        # columns = ['Year', 'Yes', 'No', 'Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)
        # Add installs per company
        for year in LAST_FIVE_YEARS:
            data = {'Year': str(year)}
            # col = self.installation_df.loc[self.installation_df['PTO_Date'].dt.year ==
            #                                year, 'Third_Party_Ownership']
            # col = self.installation_df.loc[self.installation_df['PTO_Date'].dt.year ==
            #                                year, 'Grid_BTM']
            col = self.installation_df.loc[self.installation_df['PTO_Date'].dt.year ==
                                           year, 'Third_Party_Ownership']

            col2 = self.installationADI_df.loc[self.installationADI_df['PTO_Date'].dt.year ==
                                           year, 'Third_Party_Ownership']
            #col1, TI
            try:
                yes_count = col.value_counts().Yes
                # data['Yes'] = yes_count
            except AttributeError:
                # data['Yes'] = 0
                yes_count = 0 #if undoing, this line must be commented

            try:
                no_count = col.value_counts().No
                # data['No'] = no_count
            except AttributeError:
                # data['No'] = 0
                no_count = 0

            #col 2, ADI
            try:
                yes_count2 = col2.value_counts().Yes
                # data['Yes'] = yes_count
            except AttributeError:
                # data['Yes'] = 0
                yes_count2 = 0

            try:
                no_count2 = col2.value_counts().No
                # data['No'] = no_count
            except AttributeError:
                # data['No'] = 0
                no_count2 = 0

            data['Yes'] = yes_count + yes_count2
            data['No'] = no_count + no_count2

            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        df = df.fillna(0)

        df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        df['Year'] = df['Year'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total

        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def generate_third_party_ownership_report_image(self) -> str:
        """
        Creates a table image for the third party ownership. Returns image path.
        """
        df_styled = self.get_third_party_ownership_yearly()

        df_styled['Total'] = [f'<b>{x}</b>' for x in df_styled['Total']] #boldens grand total to the right

        df_styled = df_styled.style.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis = 1)
        df_styled = df_styled.set_caption(f"3rd PARTY OWNERSHIP, BASED ON PTO DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled.set_caption(f"3rd PARTY OWNERSHIP, BASED ON PTO DATE")
        file_name = f'THIRD PARTY OWNERSHIP {str(CURRENT_YEAR)} {LAST_MONTH}.png'
        # file_name = f'THIRD PARTY OWNERSHIP {str(CURRENT_YEAR)} {MONTH_CODES[datetime.now().month - 1]}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path

    def get_sum_of_install_size_yearly(self):
        """
        Get a dataframe representing the total sum of installs per year, showing top
        10 companies in descending order.
        Sheet 8.
        """
        # Years in ascending order starting 5 years ago.
        years = [str(year) for year in LAST_TWO_YEARS]
        columns = ["Company"] + years + ['Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)
        # Add installs per company
        for company in self.unique_companies:
            data = {'Company': company}
            for year in LAST_TWO_YEARS:
                installs = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                     (self.installation_df['PTO_Date'].dt.year == year)), "Calculated_Total_System_Size"].sum()

                temp = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                     (self.installationADI_df['PTO_Date'].dt.year == year)), "Calculated_Total_System_Size"].sum()
                installs = temp + installs
                data[str(year)] = installs
            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Total"] = df[columns[1:-1]].sum(axis=1)
        top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)

        # df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        # df['Company'] = df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total


        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def generate_system_size_report_image_yearly(self) -> str:
        """
        Creates a table image for the total system size yearly. Returns image path.
        """
        STRING_CURRENT_YEAR = str(CURRENT_YEAR)
        df_styled = self.get_sum_of_install_size_yearly()

        # second_high = df_styled[STRING_CURRENT_YEAR].values[0] #finds the second highest value (this is the highest value that is not the total) in order to pick the max value the gradient is applied to
        # second_high = int(second_high)
        # highest_value = df_styled[STRING_CURRENT_YEAR].max() #finds the max value (the total) in order to apply the green color
        # highest_value = int(highest_value)
        #
        # df_styled = df_styled.style.background_gradient(axis=0, subset=STRING_CURRENT_YEAR, vmax=second_high, cmap='YlOrRd')
        # df_styled.apply(lambda x: ['background-color: green' if v == highest_value else 'border: 2px solid black' for v in x], axis=1)
        df_styled = df_styled.style.background_gradient(axis=0, subset=STRING_CURRENT_YEAR, cmap='YlOrRd')
        df_styled = df_styled.set_caption(f"INSTALLED kW, TOTAL - BASED ON PTO DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled = df_styled.set_caption(f"Installed KW, Total - Based on PTO Date")
        df_styled = df_styled.apply(lambda x: ['border: 2px solid black' if v == ' ' else 'border: 2px solid black' for v in x], axis = 1)
        # df_styled = df_styled.apply(lambda x: [
                        # 'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)
        file_name = f'TOTAL_SIZE_YEARLY_{str(CURRENT_YEAR)}_{LAST_MONTH}.png'
        # file_name = f'TOTAL_SIZE_YEARLY_{str(CURRENT_YEAR)}_{MONTH_CODES[datetime.now().month - 1]}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        # dfi.export(df_styled, export_path, table_conversion='chrome')
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path

    def get_sum_of_system_size_per_interconnection_yearly(self):
        """
        Get a dataframe representing the total sum of system size per
        interconnection type for past 5 years.
        Sheet 10.
        """
        # Years in ascending order starting 5 years ago.
        total_size = 0
        # temp_size = ""
        unique_lowercase_connections = list(
            set([connection.lower() for connection in self.unique_interconnections]))
        columns = ['Year'] + unique_lowercase_connections + ['Grand Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)
        # Add installs per company
        for year in LAST_FIVE_YEARS:
            data = {'Year': str(year)}
            for connection_type in self.unique_interconnections:
                # print(connection_type)


                total_size = self.installation_df.loc[((self.installation_df['PTO_Date'].dt.year == year) &
                                                    (self.installation_df['Interconnection_Type'].str.contains(connection_type))), "Calculated_Total_System_Size"].sum()
                # print(total_size)
                temp_total_size = self.installationADI_df.loc[((self.installationADI_df['PTO_Date'].dt.year == year) &
                                                    (self.installationADI_df['Interconnection_Type'].str.contains(connection_type))), "Calculated_Total_System_Size"].sum()

                total_size = temp_total_size + total_size
                if connection_type.lower() in data:
                    data[connection_type.lower()] += total_size
                else:
                    data[connection_type.lower()] = total_size
            df = df.append(data, ignore_index=True)
        # Convert object type to string for sorting
        df["Grand Total"] = df[columns[1:-1]].sum(axis=1) #grand total to the right of the df
        df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        df['Year'] = df['Year'].replace(np.nan, 'Grand Total') #renames the added 0 at the end of the column to grand total
        df = df.fillna(0)
        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def generate_system_size_per_connection_report_image(self) -> str:
        """
        Creates a table image for the total system size per connection. Returns image path.
        """
        df_styled = self.get_sum_of_system_size_per_interconnection_yearly()
        # df_temp = self.get_sum_of_system_size_per_interconnection_yearly()
        # df_temp = df_styled
        # df_styled = df_styled.style.apply(lambda x: 'bold' + str(df_styled['Total']) + '</b>', axis=1)
        df_styled['Grand Total'] = [f'<b>{x}</b>' for x in df_styled['Grand Total']] #boldens grand total to the right
        # df_styled = df_styled.style.apply(lambda x: ['font-weight: bold' if v == df_.loc[6] else '' for v in x])
        # df_styled['Year'] = [f'<b>{x}</b>' if x == "Grand Total"]

        # df_styled = df_styled.style.applymap('font-weight: bold', subset=pd.IndexSlice[df_styled.index[df_styled.index=='Grand Total'], :])

        # df_styled = df_styled.style.applymap('font-weight: bold',
        #           subset=pd.IndexSlice[df_styled.index[df_styled.index=='Grand Total'], :])
        df_styled = df_styled.style.set_caption(f"INSTALLED kW, GRID/BTM - BASED ON PTO DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df.background_gradient(cmap=cm, axis=1, subset=df.index[-1])
        # df_styled = df_styled.style.set_caption(f"INSTALLED KW, GRID/BTM - BASED ON PTO DATE")
        # df_styled = df_styled.apply(lambda x: ['font-weight: bold' if v == df_temp.loc[6] else '' for v in x], axis = 1)
        # df_styled = df_styled.apply('font-weight: bold', subset=pd.IndexSlice[df_styled.index[df_styled.index==6], :])
        df_styled = df_styled.apply(lambda x: ['border: 2px solid black' if v == ' ' else 'border: 2px solid black' for v in x], axis = 1)
        # df_styled.apply(lambda x: [
                        # 'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)
        file_name = f'INSTALED KW GRID BTM.png'
        # file_name = f'TOTAL_SIZE_PER_CONNECTION{str(CURRENT_YEAR)}{MONTH_CODES[datetime.now().month - 1]}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        # dfi.export(df_styled, export_path)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path

    def get_average_pto_days_monthly(self, year):
        """
        Get a dataframe representing the average pto days for each month of the given year.
        Shows lowest 10.
        Sheet 9.
        """
        print(year)
        # quit()
        COMPANIES = ['Momentum Solar', 'Tesla',
                     'Vivint', 'Sunrun', 'Trinity Solar']
        months = [MONTH_CODES[month_code] for month_code in MONTH_CODES]
        columns = ["Company"] + months
        # columns = ["Company"] + months + ['Average']
        df = pd.DataFrame(columns=columns)
        for company in COMPANIES:
            data = {'Company': company}
            # totals = {'Company': company}
            for month in MONTH_CODES:
                # somedf = self.installationADI_df.loc[(self.installationADI_df['Contractor_Company'] == "Trinity Solar") & (self.installationADI_df['PTO_Date'].dt.month == 1) & (self.installationADI_df['PTO_Date'].dt.year == 2023)]
                # for value in somedf:
                #     print(value)
                # print(somedf['Contractor_Company'])
                # print(somedf['PTO_Date'])
                # print(somedf['PTO_Acceptance_Days'].mean())
                # print(somedf)
                # quit()

                average_pto_days = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                                                             (self.installation_df['PTO_Date'].dt.month == month) &
                                                             (self.installation_df['PTO_Date'].dt.year == year)), "PTO_Acceptance_Days"].mean()

                temp_average_pto_days = self.installationADI_df.loc[((self.installationADI_df['Contractor_Company'] == str(company)) &
                                                             (self.installationADI_df['PTO_Date'].dt.month == month) &
                                                             (self.installationADI_df['PTO_Date'].dt.year == year)), "PTO_Acceptance_Days"].mean()
                
                # print(month)
                # print(average_pto_days)
                # print(temp_average_pto_days)

                # total_pto_days = self.installation_df.loc[((self.installation_df['Contractor_Company'] == str(company)) &
                #                                              (self.installation_df['PTO_Date'].dt.month == month) &
                #                                              (self.installation_df['PTO_Date'].dt.year == year)), "Installs"].sum()
                                                             # (self.installation_df['PTO_Date'].dt.year == year)), "PTO_Acceptance_Days"].mean()
                # print(type(average_pto_days))
                if type(average_pto_days) == float:
                    average_pto_days = temp_average_pto_days
                elif type(temp_average_pto_days) == float:
                    average_pto_days = average_pto_days
                else:
                    average_pto_days = average_pto_days + temp_average_pto_days
                    average_pto_days = average_pto_days / 2
                # average_pto_days = temp_average_pto_days
                # print(average_pto_days)

                # print(data)
                data[MONTH_CODES[month]] = average_pto_days
            new_df = pd.DataFrame(data=data, columns=columns, index=[0])
                # print(data)
                # totals[MONTH_CODES[month]] = total_pto_days
            # if company == "Trinity Solar":
                # print(df)
                # quit()
            # df = df.append(data, ignore_index=True)
            df = pd.concat([df, new_df], sort=False)
            # df = df.append(totals, ignore_index=True)
        # Convert object type to string for sorting
        df['Average'] = df[columns[1:-1]].mean(axis=1)
        # df["Total"] = df[columns[1:-1]].sum(axis=1)
        # total = []
        # total = df['Total']
        total = df['Average']

        #takes all the totals and splices so i have the totals rather than averages
        total = list(total)
        # print(total)
        # ** take total of the total column rather than by month **
        total = total[1::2]
        # print(total)

        #finds the total days from start of year to now
        #takes the value and averages for each company
        # days = self.days()
        # averages = []
        #
        # for value in total:
        #     averages.append(value / days)
        # print(averages)
        # exit()

        # ** total sum of days / total sum of installs **

        # df = df.drop(['Total'])
        # df['Average'] = df['Total'].mean(axis=1)
        # Replace NaN with 0
        df = df.fillna(0)


        # df = df.drop(labels=[1,3,5,7,9], axis=0)
        # df = df.drop(columns=['Total'])
        # df["Average"] = averages

        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def days(self):
        """
        Finds the total number of days from the start of the year until the start of the current month
        """
        d0 = date(CURRENT_YEAR, 1, 1)
        d1 = date(CURRENT_YEAR, CURRENT_MONTH, 1)
        delta = d1 - d0

        # self.generate_pto_report_image()
        return delta.days

    def generate_pto_report_image(self) -> str:
        """
        Creates a table image for the average pto day report. Returns image path.
        """

        df_styled = self.get_average_pto_days_monthly(
            CURRENT_YEAR)
        df_styled = df_styled.style.set_caption(f"AVERAGE PTO - ACCEPTANCE, BASED ON PTO").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled = df_styled.style.set_caption(
            # f"AVERAGE PTO, Acceptance, Based on PTO")
        df_styled = df_styled.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else '' for v in x], axis = 1)
        df_styled = df_styled.apply(lambda x: [
                        'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)
        file_name = f'AVG PTO {str(CURRENT_YEAR)} {LAST_MONTH}.png'
        # file_name = f'AVG PTO {str(CURRENT_YEAR)} {MONTH_CODES[datetime.now().month - 1]}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        # dfi.export(df_styled, export_path)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        return export_path


    def get_install_count_by_recieved_date(self):
        """
        Get a dataframe representing the total sum of installs per year
        based on the date recieved
        """
        # Years in ascending order starting 5 years ago.
        # companies = ['Vivint', 'Vision Solar LLC', 'Sunrun', 'Tesla', 'Momentum Solar', 'Suntuity', 'Bright Planet Solar', 'Trinity Solar', 'Posigen NJ LLC', 'SunnyMac']
        years = [str(year) for year in LAST_FIVE_YEARS]
        columns = ["Company"] + years + ['Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)
#**

        for company in self.unique_pipeline_companies:
            data = {'Company': company}
            for year in LAST_FIVE_YEARS:
                try:
                    installs = self.pipeline_df.loc[((self.pipeline_df['Contractor_Company'] == str(company)) &
                                                    # (self.pipeline_df['Registration_Received_Date'].dt.month == MONTH) &
                                                        (self.pipeline_df['Application_Received_Date'].dt.year == year)), "Installs"].sum()

                    temp = self.pipelineADI_df.loc[((self.pipelineADI_df['Contractor_Company'] == str(company)) &
                                                    # (self.pipeline_df['Registration_Received_Date'].dt.month == MONTH) &
                                                        (self.pipelineADI_df['Application_Received_Date'].dt.year == year)), "Installs"].sum()
                except Exception as e:
                    print(f"encounttered exceptions {e}")
                    installs = 0
                    temp = 0
                installs += temp
                data[str(year)] = installs
            df = df.append(data, ignore_index=True)

        df["Total"] = df[columns[1:-1]].sum(axis=1)
        top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)

        # df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
        # df['Company'] = df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total

        df = df.reset_index(drop=True)
        return df.astype(int, errors='ignore')

    def generate_install_count_by_recieved_date(self) -> str:
        """
        Creates a table image for the install count by recieved date for the top 10 companies.
        Returns image path.
        """
        df_styled = self.get_install_count_by_recieved_date()
        df_styled = df_styled.style.set_caption(f"BACKLOG, INSTALL COUNT BASED ON RECEIVED DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled = df_styled.style.set_caption(
            # f"BACKLOG, INSTALL COUNT BASED ON RECEIVED DATE")

        df_styled = df_styled.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else '' for v in x], axis = 1)
        df_styled = df_styled.apply(lambda x: [
                        'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)
        file_name = f'TOTAL INSTALLS {str(TEMP_LAST_MONTH)}.png'
        temp_file_name = f'TOTAL INSTALLS {str(TEMP_LAST_MONTH)}.png'
        # anothertemp =  f'TOTAL INSTALLS {str(TWO_MONTHS_AGO)}.png'
        # another_export = os.path.join(os.getcwd(), SAVE_FOLDER, anothertemp)
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        save_for_next_month_path = os.path.join(os.getcwd(), SAVE_FOLDER, temp_file_name)
        # os.remove(save_for_next_month_path)
        # dfi.export(df_styled, export_path)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        df_styled = df_styled.set_caption(f"PREVIOUS MONTH DATA")
        dfi.export(df_styled, save_for_next_month_path, table_conversion='chrome')
        # dfi.export(df_styled, save_for_next_month_path)
        return export_path


    def find_top_performers_backlog(self) -> list:
        """
        helper method in order to determine who the top performers are in order to find a company list to generate how many installs each company has on backlog
        """
        last_year = CURRENT_YEAR - 1
        two_years = CURRENT_YEAR - 2
        three_years = CURRENT_YEAR - 3
        four_years = CURRENT_YEAR - 4
        five_years = CURRENT_YEAR - 5
        # print(five_years)

        last_year = str(last_year)
        two_years = str(two_years)
        three_years = str(three_years)
        four_years = str(four_years)
        five_years = str(five_years)
        now = str(CURRENT_YEAR)

        # LAST_FIVE_YEARS = [five_years, four_years, three_years, two_years, last_year, now]
        # print(now)
        #finds the top 10 performers of the last 5 years, does not rank by quarter, prints the companies i will be using to determine quarter leaders
        # try:
#**
        temp_col = ['Company'] + [five_years] + [four_years] + [three_years]+ [two_years] + [last_year] + [now]
        # print(LAST_FIVE_YEARS)
        # quit()
        print(temp_col)
        # quit()
        temp = pd.DataFrame(columns=[temp_col], dtype='Int64')
        # print(temp)
        # quit()
        for company in self.unique_pipeline_companies:
            the_data = {'Company': company}
            for year in LAST_FIVE_YEARS:
            # print(year)
                some_installs = self.pipeline_df.loc[((self.pipeline_df['Contractor_Company'] == str(company)) &
                                (self.pipeline_df['Application_Received_Date'].dt.year == year)), "Installs"].sum()

                temp_some_installs = self.pipelineADI_df.loc[((self.pipelineADI_df['Contractor_Company'] == str(company)) &
                                (self.pipelineADI_df['Application_Received_Date'].dt.year == year)), "Installs"].sum()

                some_installs += temp_some_installs
                # print(f"this is my added value: {some_installs}")
                the_data[str(year)] = int(some_installs)
            # print(f"this is the data {the_data}")
            # # try:
            # new_df = pd.DataFrame(columns=[temp_col], data=the_data)
            # new_df = pd.DataFrame.from_dict(the_data, orient='index')
            # print(new_df)
            # quit()
            # print(type(the_data))
            # for value in the_data.keys():
            #     print(the_data.get(value))
            #     print(type(the_data.get(value)))
            # if the_data:
                # temp = pd.concat([temp, new_df], sort=False)
            temp = temp.append(the_data, ignore_index=True)
            # else:    
            #     print("EMPTY")
            # temp = pd.concat(the_data, temp, ignore_index=True)
            # temp = temp.concat(the_data, ignore_errors=True)
            # except:
                # pass
        # print(the_data)
        # print(temp)
        temp['Total'] = temp[temp_col[1:-1]].sum(axis=1)
        top_ten = temp.nlargest(10, "Total")
        temp = top_ten.fillna(0)
        # temp = top_ten["Total"] = top_ten.fillna(0)
        temp = temp.reset_index(drop=True)
        # print(temp)
        company_list = temp['Company'].tolist()
        return company_list

    def get_backlog_by_quarter_based_on_recieved(self, year):
                """
                Creates a dataframe with top 10 companies by backlog based on recieved date, with installs per quarter.
                merges tables from the last 2 years, each quarter has to be named by year.
                """

                # quarter_cols = ['Q' + str(quarter) for quarter in QUARTERS]
                # year =  CURRENT_YEAR
                quarter_cols = [str(year) + ' Qtr1', str(year) + ' Qtr2',  str(year) + ' Qtr3', str(year) + ' Qtr4']
                columns = ["Company"] + quarter_cols + ['Total ' + str(year)]
                df = pd.DataFrame(columns=columns)

                company_list = self.find_top_performers_backlog()
                print(company_list)

                for company in company_list:
                # for company in self.unique_companies:
                    data = {'Company': company}
                    for quarter in QUARTERS:
                        # print(quarter)
                        try:
                            installs = self.pipeline_df.loc[((self.pipeline_df['Contractor_Company'] == str(company)) &
                                                            (self.pipeline_df['Application_Received_Date'].dt.year == year)) &
                                                            (self.pipeline_df['Application_Received_Date'].dt.month.isin(QUARTERS[quarter])), "Installs"].sum()

                            temp = self.pipelineADI_df.loc[((self.pipelineADI_df['Contractor_Company'] == str(company)) &
                                                            (self.pipelineADI_df['Application_Received_Date'].dt.year == year)) &
                                                            (self.pipelineADI_df['Application_Received_Date'].dt.month.isin(QUARTERS[quarter])), "Installs"].sum()
                        except:
                            installs = 0
                            temp = 0
                        installs += temp
                        #breaks down each table by year, adds the year of the table to the front
                        if quarter == 1:
                                # print('yes')
                            data[str(year) + ' Qtr' + str(quarter)] = installs
                        else:
                            data[str(year) + ' Qtr' + str(quarter)] = installs

                    df = df.append(data, ignore_index=True)
                # Convert object type to string for sorting
                df["Total " + str(year)] = df[columns[1:-1]].sum(axis=1)
                # df = df.drop_duplicates(subset=['Company'])
                top_ten_df = df.nlargest(10, "Total " + str(year))
                # Convert float to int for presentation
                top_ten_df["Total " + str(year)] = top_ten_df["Total " + str(year)].astype(int)
                df = df.reindex(columns = columns)
                df = top_ten_df.fillna(0)
                df = df.reset_index(drop=True)
                return df.astype(int, errors='ignore')

    def generate_backlog_by_quarter_based_on_recieved(self) -> str:
        """
        Generates an image for backlog receieved orders based on year and QUARTERS
        """

        year =  CURRENT_YEAR
        last_year = CURRENT_YEAR - 1
        quarter_cols = [str(year) + ' Qtr1', 'Qtr2', 'Qtr3', 'Qtr4']
        columns = ["Company"] + quarter_cols + ['Total']
        df = pd.DataFrame(columns=columns)

        df = self.get_backlog_by_quarter_based_on_recieved(year)
        last_year_df = self.get_backlog_by_quarter_based_on_recieved(last_year)
        merged_df = pd.merge(left = last_year_df, right = df, right_on='Company', left_on='Company')

        merged_df = merged_df.style.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else '' for v in x], axis = 1)
        merged_df = merged_df.apply(lambda x: [
            'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)

        merged_df = merged_df.set_caption(f"BACKLOG BY QUARTER, BASED ON RECEIVED DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])

        # merged_df = merged_df.set_caption(
        # f"BACKLOG BY QUARTER, BASED ON RECEIVED DATE")

        file_name = f'BACKLOG BASED ON RECEIVED {str(CURRENT_YEAR)}.png'

        quarter_file_name = f'BACKLOG BASED ON RECEIVED {str(TEMP_LAST_MONTH)}.png'
        second_save_for_next_month_path = os.path.join(os.getcwd(), SAVE_FOLDER, quarter_file_name)

        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        # dfi.export(merged_df, export_path, table_conversion='matplotlib')
        dfi.export(merged_df, export_path, table_conversion='chrome')
        # dfi.export(merged_df, export_path)

        merged_df = merged_df.set_caption("PREVIOUS MONTH DATA")
        # dfi.export(merged_df, second_save_for_next_month_path)
        dfi.export(merged_df, second_save_for_next_month_path, table_conversion='chrome')
        # dfi.export(merged_df, second_save_for_next_month_path, table_conversion='matplotlib')
        return export_path

    def get_backlog_kw(self):
        """
        Creates a table of the backlog system size total, based on top 10 companies
        """
        # LAST_TWO_YEARS = CURRENT_YEAR, CURRENT_YEAR - 1
        years = [str(year) for year in LAST_TWO_YEARS]
        columns = ["Company"] + years + ['Total']
        # Create empty dataframe
        df = pd.DataFrame(columns=columns)
#**
        for company in self.unique_pipeline_companies:
            data = {'Company': company}
            for year in LAST_TWO_YEARS:
                try:
                    installs = self.pipeline_df.loc[((self.pipeline_df['Contractor_Company'] == str(company)) &
                                                    # (self.pipeline_df['Registration_Received_Date'].dt.month == MONTH) &
                                                    (self.pipeline_df['Application_Received_Date'].dt.year == year)), "Calculated_Total_System_Size"].sum()

                    temp = self.pipelineADI_df.loc[((self.pipelineADI_df['Contractor_Company'] == str(company)) &
                                                    # (self.pipeline_df['Registration_Received_Date'].dt.month == MONTH) &
                                                    (self.pipelineADI_df['Application_Received_Date'].dt.year == year)), "Calculated_Total_System_Size"].sum()
                except:
                    installs = 0
                    temp = 0
                installs += temp
                data[str(year)] = installs
            df = df.append(data, ignore_index=True)

        df["Total"] = df[columns[1:-1]].sum(axis=1)

        #because trinity solar is not among the top 10, find it in the current data set and pull it to concat later
        top_ten_df = df.nlargest(10, "Total")

        # if "Trinity Solar" not in top_ten_df['Company']:
        #     trin_df = df.loc[df['Company'] == 'Trinity Solar']

        #     current = int(trin_df[str(CURRENT_YEAR)])
        #     last = int(trin_df[str(CURRENT_YEAR - 1)])
        #     total = current + last
        #     trin_data ={
        #     'Company': trin_df['Company'],
        #     str(CURRENT_YEAR) : current,
        #     str(CURRENT_YEAR - 1): last,
        #     'Total': total
        #     }

        #     final_trin_df = pd.DataFrame(trin_data, columns=columns)

        #     top_ten_df = df.nlargest(9, "Total")
        #     # Convert float to int for presentation
        #     top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        #     df = top_ten_df.fillna(0)
        #     df = df.reset_index(drop=True)
        #     df_concat = pd.concat([df, final_trin_df])

        #     df = df_concat.reset_index(drop=True)
        # # except Exception as e:
        # # print(f'TRINITY DATA INCOMPLETE, {e}')

        # top_ten_df = df.nlargest(10, "Total")
        # Convert float to int for presentation
        top_ten_df["Total"] = top_ten_df["Total"].astype(int)
        df = top_ten_df.fillna(0)
        df = df.reset_index(drop=True)
    # df = df_concat.nlargest(11, "Total")

        return df.astype(int, errors='ignore')

    def generate_backlog_kw(self) -> str:
        """
        Generates an image of backlog system size
        """
        df_styled = self.get_backlog_kw()
        df_styled = df_styled.style.set_caption(f"BACKLOG, kW BASED ON RECEIVED DATE").set_table_styles([{
        'selector': 'caption',
        'props': [
        ('color', 'black'),
        ('font-size', '16px'),
        ('font-weight', 'bold')
        ]
        }])
        # df_styled = df_styled.style.set_caption(
            # f"BACKLOG, KW BASED ON RECEIVED DATE")
        df_styled = df_styled.apply(lambda x: ['border: 2px solid black' if v == 'Trinity Solar' else '' for v in x], axis = 1)
        df_styled = df_styled.apply(lambda x: [
                        'background: yellow' if v == 'Trinity Solar' else 'border: 2px solid black' for v in x], axis=1)
        file_name = f'BACKLOG, KW {str(CURRENT_YEAR)}.png'
        export_path = os.path.join(os.getcwd(), EXPORT_FOLDER, file_name)
        dfi.export(df_styled, export_path, table_conversion='chrome')
        # dfi.export(df_styled, export_path)
        return export_path

    def last_day_of_month(self):
        """
        prints the last day of last month
        """
        # print(INT_LAST_MONTH)
        if (INT_LAST_MONTH) == 2:
            if CURRENT_YEAR % 4 != 0:
                return 28
            else:
                return 29

        end_in_30 = [4, 6, 9, 11]

        if INT_LAST_MONTH in end_in_30:
            return 30
        else:
            return 31
        # d = date(CURRENT_YEAR + int(CURRENT_MONTH/12), CURRENT_MONTH%12+1, 1)-datetime.timedelta(days=1)
        # return d
        # if (INT_LAST_MONTH) % 2 == 1:
        #     return 31
        # else:
        #     return 30

    def create_title_page(self) -> str:
        """
        Creates a styled title page for the report using an image base
        Image base is a blue background with trinity solar written, along with a green bottom
        "My String\n"
        """
        STRING_CURRENT_YEAR = str(CURRENT_YEAR)
        prev_month = FULL_MONTH_CODES[TEMP_LAST_MONTH]
        today = date.today()
        tday = today.strftime("%d, %Y")

        existing_pdf_path = os.path.join(os.getcwd(), "Publication.pdf")
        TEMP_PATH = os.path.join(os.getcwd())
        words_pdf = os.path.join(TEMP_PATH, f'Word_Page.pdf')
        title_page_path = os.path.join(os.getcwd(), f"Title_Page.pdf")
        # file_name = os.path.join(TEMP_PATH, f'Title_Page.pdf')

        c = canvas.Canvas(words_pdf, pagesize = letter)
        existing_pdf = PdfFileReader(open(existing_pdf_path, "rb"))
        output = PdfFileWriter()

        page = existing_pdf.getPage(0)
        # output.addPage(page)

        # MAX_HEIGHT = 792
        MAX_HEIGHT = 600
        # MAX_WIDTH = 615
        #true max width is 615
        MAX_WIDTH = 500
        CENTER = MAX_WIDTH // 2
        MID = MAX_HEIGHT // 2
        QUARTER = MID // 2
        HALF_CENTER = CENTER // 2

        #set color to white, font type and size
        c.setFillColorRGB(255, 255, 255)
        c.setFont('Helvetica',20)

        through_date = self.last_day_of_month()
        #reset current month just incase code has been run late - we would like this date to ALWAYS be today
        CURRENT_MONTH = datetime.now().month
        #starts at the left of page, written above the middle
        cen = 615 // 2
        c.drawCentredString(cen, MID + 70, "Data through " + str(prev_month) + " " + str(through_date) + ", " + STRING_CURRENT_YEAR)
        c.drawCentredString(cen, MID + 40, "Prepared for Trinity Solar " + f"{FULL_MONTH_CODES[CURRENT_MONTH]}" + " " + tday)
        # c.drawCentredString(cen, MID + 70, "Data through Data through January 31, 2023")
        # c.drawCentredString(cen, MID + 40, "Prepared for Trinity Solar February 28, 2023")
        c.save()

        word_pdf_reader = PdfFileReader(words_pdf, "rb")
        page.mergePage(word_pdf_reader.getPage(0))
        output.addPage(page)

        outputStream = open(title_page_path, 'wb')
        output.write(outputStream)
        outputStream.close()

        return title_page_path

    def generate_report_pdf(self) -> str:
        """
        Generates a report pdf and returns the file path.
        """
        TEMP_PATH = os.path.join(os.getcwd(), 'temp')
        ASSETS_PATH = os.path.join(os.getcwd(), 'assets')
        # BASE_PATH = os.path.join(ASSETS_PATH, 'NJCleanEnergyPDFBase.png')
        BASE_IMAGE_PATH = r"C:\Users\dood2\Desktop\AtomPython\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.png"
        BASE_IMAGE_PATH = r"C:\Users\AviGoyal\Desktop\PythonCode\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.png"
        # BASE_IMAGE_PATH = r"C:\Users\RPA_Bot_7\Desktop\NJ Clean Energy\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.png"
        BASE_PDF_PATH = r"C:\Users\dood2\Desktop\AtomPython\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.pdf"
        BASE_PDF_PATH = r"C:\Users\AviGoyal\Desktop\PythonCode\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.pdf"
        # BASE_PDF_PATH = r"C:\Users\RPA_Bot_7\Desktop\NJ Clean Energy\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.pdf"
        REPORT_PATH = os.path.join(TEMP_PATH, f'FINISHED_REPORT_{STRING_LAST_MONTH}_{CURRENT_YEAR}.pdf')
        # REPORT_PATH = os.path.join(TEMP_PATH, f'FINISHED REPORT {datetime.now().month - 1}_{CURRENT_YEAR}.pdf')
        print('Creating pdf...')
        # report_paths = 1
        TITLE_PAGE = self.create_title_page()
        #generates images
        report_paths = self.generate_report_images()
        # report_paths = self.generate_pto_report_image()
        pages = []
        #adds the title page first
        pages.append(TITLE_PAGE)

        for report_index, page_header in enumerate(report_paths):
            # print(page_header)

            MAX_HEIGHT = 792

            # MAX_HEIGHT = 3000

            MAX_WIDTH = 595

            # MAX_WIDTH = 2000

            CENTER = MAX_WIDTH // 2

            # Prep canvas
            image_path = r"C:\Users\dood2\Desktop\AtomPython\NJCleanEnergyReports\assests\NJCleanEnergyPDFBase.png"
            print('Prepping canvas...')
            file_name = os.path.join(TEMP_PATH, f'Report Page {report_index + 1}.pdf')
            # file_name = r"C:\Users\dood2\Desktop\AtomPython\MY_NJCE\temp\Report_Page_1.pdf"
            # file_name.replace(" ", "")

            c = canvas.Canvas(file_name, pagesize = letter)
            width, height = letter
            # c = canvas.Canvas(file_name, pagesize=A4, width=1000)
            c.setFontSize(20)
            # print("after canvas creation")

            c.drawImage(BASE_IMAGE_PATH, 0, 0, width=MAX_WIDTH, height=842)
            # c.drawImage(BASE_IMAGE_PATH, 0, 0, width=MAX_WIDTH, height=942) #doesnt fix the table that broke, installed kw... no idea why thats happening, maybe need to remove the total column that im adding..
            # c.drawImage(BASE_IMAGE_PATH, 0, 0, width=MAX_WIDTH, height=700)
            # c.drawImage(BASE_IMAGE_PATH, 0, 0, width=MAX_WIDTH, height=MAX_HEIGHT)

            # c.drawImage(BASE_IMAGE_PATH, 0, 0, width=5000, height=2500)

            # c.drawCentredString(2500, 1250, page_header)
            # c.drawImage(BASE_PATH, 0, 0, width=MAX_WIDTH, height=842)
            # c.drawCentredString(MAX_WIDTH // 2, MAX_HEIGHT // 2, page_header)

            # Add each image to canvas
            for index, image_path in enumerate(report_paths[page_header]):
                print('Calculating table location...')
                print(report_paths[page_header])
                TABLE_COUNT = len(report_paths[page_header])
                # Calculate y max of each table
                MAX_Y = (MAX_HEIGHT // TABLE_COUNT)

                # Get image width and height
                with Image.open(image_path) as image:
                    img_width, img_height = image.size
                    if img_height > 425:
                        img_height = 370
                    # print(image.size)
                # Check img height bounds
                if img_height > MAX_Y:
                    new_height = MAX_Y - 10
                    # print(img_height)
                    # new_height = MAX_Y - 20
                else:
                    new_height = img_height

                # Check img width bounds
                if img_width > MAX_WIDTH:
                    new_width = MAX_WIDTH - 10
                    x = 10
                else:
                    new_width = img_width
                    # Get x coordinate to center image
                    x = CENTER - img_width // 2

                # Calculate y coord for bottom left of table
                # print(TABLE_COUNT)
                # print(index)
                if TABLE_COUNT > 1:
                    y = MAX_HEIGHT - ((index + 1) * MAX_Y)
                    # y = y - 250
                else: # If only 1 table, center on page
                    y = MAX_HEIGHT // 2
                    # y = y - 350
                print('Drawing table to pdf...')
                # if image_path == self.install_sum_quarterly_previous_year_path:
                #     print("")
                #     c.drawImage(image_path, x, y, height=new_height, width=450)
                # if image_path == self.install_sum_quarterly_path:
                #     print("")
                #     c.drawImage(image_path, x, y, height=new_height, width=450)
                # else:
                c.drawImage(image_path, x, y, height=new_height, width=new_width)
                # c.drawImage(image_path, x, y, height=new_height, width=400)
                # temp_file_name = f"TOTAL INSTALLS {TEMP_LAST_MONTH}"
                # if image_path == os.path.join(os.getcwd(), EXPORT_FOLDER, temp_file_name):
                #     print("Found Previous Month Data For: Backlog, Installs by recieved date, Adding to canvas...")
                #     # c.drawImage(save_for_next_month_path, x, y, height=new_height, width=new_width)
                #     exit()

                # c.drawImage(image_path, x, y, height=1500, width=1500)
                # c.drawImage(image_path, x, y, height=400, width=600)

                #REMOVE THIS IF STATEMENT IN THE FINAL
                if image_path == previous_month_quarter_backlog_install_path:
                # if report_paths[report_index + 1] == "Installs by Receieved Date" or "Backlog Installs based on Received Date":
                    print("Temporary keep method")
                elif image_path == Previous_Month_backlog_install_path:
                    print("Temporary keep method")
                elif image_path == self.received_date_installs_path:
                    print("Save For Next Month, Not Removing...")
                elif image_path == self.backlog_received_path:
                    print("Save For Next Month, Not Removing...")
                else:
                    print("NOT THE PREV PATH")
                    os.remove(image_path)
            c.save()
            pages.append(file_name)

        #creates a pdf for the tpo pregenerated image
        image1 = Image.open(self.pre_gen_path_tpo())
        im1 = image1.convert('RGB')
        imagelist = [im1]
        pregen_tpo_file_name = os.path.join(TEMP_PATH, f'TPO_Image.pdf')

        im1.save(pregen_tpo_file_name, save_all=True, append_images=imagelist)
        time.sleep(2)

        #creates a pdf for the installation county pregenerated image
        image2 = Image.open(self.pre_gen_path_installation())
        im2 = image2.convert('RGB')
        imagelist = [im2]
        pregen_installation_file_name = os.path.join(TEMP_PATH, f'Installation_county_image.pdf')

        im2.save(pregen_installation_file_name, save_all=True, append_images=imagelist)

        pages.append(pregen_tpo_file_name)
        pages.append(pregen_installation_file_name)

        print('Merging pdfs...')
        input_streams = []
        # Get each pdf content
        for input_file in pages:
            input_streams.append(open(input_file, 'rb'))
        # Create base writer
        writer = PdfFileWriter()
        # Add each pdf to writer
        for reader in map(PdfFileReader, input_streams):
            writer.addPage(reader.getPage(0))
        # Write pdf to file
        with open(REPORT_PATH, 'wb') as output_stream:
            writer.write(output_stream)
        # Close input file contents
        for f in input_streams:
            f.close()
        # Delete individual pdfs
        for file_path in pages:
            os.remove(file_path)
        #delete downloaded excel files
        for excel_file in self.list_files:
            os.remove(excel_file)
        print(REPORT_PATH)

        return REPORT_PATH

    def run(self):
        return self.generate_report_pdf()
if __name__ == "__main__":
    a = NJCleanEnergy()
    a.find_top_performers_backlog()
    print(a.generate_report_pdf())

    # a.pre_gen_path_tpo()
    # print(a.get_sum_of_system_size_per_interconnection_yearly())

    # print(a.last_day_of_month())
    # print(a.days())
    # print(a.create_title_page())
    # print(a.create_title_page())
    # print(a.get_sum_of_system_size_per_interconnection_yearly())
    # df.loc['Column_Total']= df.sum(numeric_only=True, axis=0) #unnamed column total, successfully adds to the bottom though
    # df['Company'] = df['Company'].replace(np.nan, 'Total') #renames the added 0 at the end of the column to grand total
    #BELOW IS USED IN THE GENERATE METHOD
    # second_high = df_styled[STRING_CURRENT_YEAR].values[0] #finds the second highest value (this is the highest value that is not the total) in order to pick the max value the gradient is applied to
    # second_high = int(second_high)
    # highest_value = df_styled[STRING_CURRENT_YEAR].max() #finds the max value (the total) in order to apply the green color
    # highest_value = int(highest_value)
    # df_styled = df_styled.style.background_gradient(axis=0, subset=STRING_CURRENT_YEAR, vmax=second_high, cmap='YlOrRd')
    # df_styled.apply(lambda x: ['background-color: green' if v == highest_value else 'border: 2px solid black' for v in x], axis=1)

    # import excel2img
    # print(a.generate_install_sum_report_yearly_image())
    # excel2img.export_img("Excel File Full Path", "Target Image full Path", "Excel SheetName", None)

    # print(a.generate_system_size_report_image_yearly())
    # print(a.generate_third_party_ownership_report_image())

    # print(a.generate_pto_report_image())
    # print(a.generate_install_sum_report_image(CURRENT_YEAR))
    # print(a.pre_gen_path_installation())
    # something = datetime.now().month - 1
    # print(a.pre_gen_path_tpo())
    # print(a.get_backlog_kw())
    # print(a.generate_backlog_kw())
    # print(a.generate_install_count_by_recieved_date())
    # print(a.generate_install_count_by_recieved_date(something + 1))
    # print(a.get_sum_of_system_size_per_interconnection_yearly())
    # print(a.get_install_sum_report_monthly(2021))
    # print(a.get_install_count_by_type_year())
    # print(a.generate_install_count_by_type_year())
    # print(a.generate_install_count_by_type_year()) ###
    # print(a.get_backlog_by_quarter_based_on_recieved(2020))
    # print(a.get_backlog_by_quarter_based_on_recieved(CURRENT_YEAR))
    # print(a.generate_backlog_by_quarter_based_on_recieved())
    # print(a.get_install_count_by_recieved_date())
    # print(a.get_install_sum_report_yearly())
    # print(CURRENT_MONTH)
    # print(CURRENT_YEAR)
    # print(a.get_average_pto_days_monthly(2023))
    # print(a.get_third_party_ownership_yearly())
    # print(a.generate_system_size_per_connection_report_image())
    # print(a.generate_install_sum_report_quarterly_image(CURRENT_YEAR))
    # print(a.generate_install_sum_report_yearly_image())
    # print(a.get_yearly_quarter_install())

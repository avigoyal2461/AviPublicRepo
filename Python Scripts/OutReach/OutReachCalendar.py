import pandas as pd
import glob 
import os
import sys 
# sys.path.append(os.environ['PythonScope'])
sys.path.append(os.environ['autobot_modules'])
#from SalesforceAPI.SFReportToDF import SFReportDF
from SalesforceAPI import SalesforceAPI
# from resources.SalesforceAPI.SFReportToDF import SFReportDF
from Sharepoint.connection import SharepointConnection
# from resources.Sharepoint.connection import SharepointConnection
from BotUpdate.ProcessTable import RPA_Process_Table
from df_styler import Df_Styler
from excel_writer import Excel_Writer
# import win32com.client
import openpyxl
import time
from datetime import datetime
from datetime import timedelta

#site_url = https://trinitysolarsys.sharepoint.com/teams/BTIntranet/Shared%20Documents/Forms/AllItems.aspx?RootFolder=%2Fteams%2FBTIntranet%2FShared%20Documents%2FOutreach%20Tracker&FolderCTID=0x0120005E9DDEDA55C18C488B95DD32B1C3E44A
class OutReachCalendar():
    def __init__(self):
        self.bot_update = RPA_Process_Table()
        self.name = "OutReach_Calendar"
        self.nothing = True
        self.sf_connection = SalesforceAPI()

        self.sharepoint = SharepointConnection()

        self.today = datetime.today()#.strftime('%m-%d-%Y')
        self.bot_update.register_bot(self.name)
        self.bot_update.update_bot_status(self.name, 'Starting Upload', self.today)

        self.day = self.today.day
        self.yesterday = self.today - timedelta(days = 1)

        # self.sharepoint.url = "https://trinitysolarsys.sharepoint.com/teams/BTIntranet"
        self.sharepoint.url = "https://trinitysolarsys.sharepoint.com/sites/17DayTraining"
        # self.sharepoint.relative_url = "/teams/BTIntranet/Shared%20Documents/Outreach%20Tracker/"
        # self.sharepoint.relative_url = "/teams/BTIntranet/Shared%20Documents/"
        self.sharepoint.relative_url = "/sites/17DayTraining/Shared%20Documents/"

        # self.one_drive_url = r"https://trinitysolarsys-my.sharepoint.com/personal/joshuabeach_trinity-solar_com/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fjoshuabeach%5Ftrinity%2Dsolar%5Fcom%2FDocuments&view=0"
        self.sheet_name = "Outreach Coverage Tracker.xlsx"
        self.folder_name = "Outreach%20Coverage%20Tracker"
        self.sheet_name_for_new_month = self.sheet_name.split(".")[0]

        self.download_path = os.path.dirname(os.path.abspath(__file__))
        
        self.excel_location = None
        self.impacted_sheets = ['Variables', 'WT', 'Demo', 'Demo 30 Days','Contracts', 'No Rep', 'Contact', 'Skedulo Data', 'Office Sort', 'SameDay', 'User'] #either use 2 lists or account for self.sheets with single cell changes
        self.sheets_with_single_cell_changes = ['Variables']
        self.upload_first_then_style = ['Contact', 'Office Sort', 'Skedulo Data']

        self.excel_writer = None
        
        # self.sheets_with_multiple_changes = ['WT', 'Demo', 'Contracts', 'No Rep', 'Contact', 'Office Sort'] #unused as of now
        self.reports = {
            'WT': '00O5b000005fOsU',
            'Demo': '00O5b000005wBCh',
            'Demo 30 Days': '00OPl0000004edB',
            'Contracts': '00O5b000005fOuV',
            'No Rep': '00O5b000005fSM3',
            'Contact': '00O5b000005fOsj',
            'Skedulo Data': '00O5b000005f67z',
            'SameDay': '00OPl00000092FV',
            'User': '00O5b000005wEHG'
        }
        print(f"Initialized for {self.today}")

    def Set_Path(self) -> str:
        """
        Sets the path to where we will download the outreach calendar
        """

        FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
        files = glob.glob(f"{FOLDER_PATH}/*.xlsx")

        if isinstance(files, list):
            self.excel_location = fr"{files[0]}"
        else:
            self.excel_location = fr"{files}"
        
        print(self.excel_location)
        return self.excel_location
    
    def download_outreach(self) -> bool:
        """
        downloads the outreach excel sheet from sharepoint
        """
        # return True
        print("Downloading Excel Workbook from SharePoint...")
        # # self.sharepoint.getFile(path=fr"{self.download_path}/{self.sheet_name}", folder="Outreach%20Tracker", file=self.sheet_name)
        self.sharepoint.getFile(path=fr"{self.download_path}/{self.sheet_name}", folder="Outreach%20Coverage%20Tracker", file=self.sheet_name)

        return True
    
    def upload_outreach(self, name=None) -> bool:
        """
        Uploads the finished result to outreach
        """
        print("Uploading Sheet back to SharePoint")
        # self.sharepoint.uploadFile(path=fr"{self.download_path}/{self.sheet_name}", folder="Outreach%20Tracker", file=self.sheet_name)
        if name:
            self.sharepoint.uploadFile(path=fr"{self.download_path}/{self.sheet_name}", folder=f"{self.folder_name}/PreviousMonths", file=name)

        else:
            res = self.sharepoint.uploadFile(path=fr"{self.download_path}/{self.sheet_name}", folder=self.folder_name, file=self.sheet_name)
            while True:
                print(res)
                if not res:
                    try:
                        self.sharepoint.deleteFile(path=f"{self.folder_name}/{self.sheet_name}")
                        time.sleep(10)
                    except:
                        print("File was already removed... Attempting Upload")
                        pass
                    res = self.sharepoint.uploadFile(path=fr"{self.download_path}/{self.sheet_name}", folder=self.folder_name, file=self.sheet_name)
                else:
                    break
                
            #self.sharepoint.deleteFile(path=f"{self.folder_name}/PreviousMonths/Outreach Coverage Tracker-03-31-2023.xlsx")
            #time.sleep(10)
            #res = self.sharepoint.uploadFile(path=fr"{self.download_path}/{self.sheet_name}", folder=f"{self.folder_name}/PreviousMonths", file="Outreach Coverage Tracker-03-31-2023.xlsx")
            
        print("Sheet uploaded")

        return True
    
    def load_excel_workbook(self, sheet) -> pd.DataFrame:
        """
        Loads the Excel sheet for use
        """
        #skips set rows on specific sheets.. currently only Office Sort contains extra data
        print(f"Refreshing Excel Formula Data for {sheet}...")
        self.excel_writer.refresh_sheet()
        if sheet == "Office Sort":
            skip_row = 11
        else:
            skip_row = 0

        df = pd.read_excel(self.excel_location, sheet_name=sheet, index_col=None, skiprows=skip_row)
        print(df)
        return df

    
    def write_to_excel(self, sheet, df) -> bool:
        """
        Uses excel_writer to style each sheet using given DF
        """
        if " " in sheet:
            sheet = sheet.replace(" ", "_")

        writerattribute = getattr(self.excel_writer, sheet)
        result = writerattribute(df)

        return result
    
    def style_list(self, sheet, new_df=None) -> pd.DataFrame:
        """
        Styles List based on requirements
        """
        if " " in sheet:
            sheet = sheet.replace(" ", "_")
        dfattribute = getattr(Df_Styler, sheet)
        styled_df = dfattribute(new_df)
        
        return styled_df

    def download_report(self, sheet_name) -> pd.DataFrame:
        """
        Downloads reports from SF, returns each as DF
        Given sheet name to correspond with self.reports value to pull data
        """
        reportId = self.reports.get(sheet_name)
        df = self.sf_connection.get_report(reportId=reportId)

        return df
    
    def run(self):
        """
        Runs outreach calendar updates
        """
        self.download_outreach()
        self.excel_location = self.Set_Path()
        self.excel_writer = Excel_Writer(self.excel_location, self.impacted_sheets)

        if self.day == 1:
            self.upload_outreach(name=f"{self.sheet_name_for_new_month}-{self.yesterday.strftime('%m-%d-%Y')}.xlsx")

        for sheet in self.impacted_sheets:
            if sheet in self.reports.keys(): #if the value requires data from salesforce
                new_df = self.download_report(sheet)
                if sheet in self.upload_first_then_style:
                    print("Writing sheet then pulling data")
                    self.write_to_excel(sheet, new_df)
                    time.sleep(10)
                    
                    new_df = self.load_excel_workbook(sheet)
                styled_df = self.style_list(sheet, new_df)
                excel = styled_df.to_csv(f"{self.download_path}/{sheet}.csv")

                # print(styled_df)
                print(sheet)
                self.write_to_excel(sheet, styled_df)

            else: #if the sheet is only being updated / formatted, or has single cell change, this will send None under new_df 

                old_df = self.load_excel_workbook(sheet)
                styled_df = self.style_list(sheet, old_df)
                # print(styled_df)
                print(sheet)
                self.write_to_excel(sheet, styled_df)

        self.excel_writer.refresh_sheet()
        #self.excel_writer.protect_workbook()

        time.sleep(3)
        # print("Finished... Not Uploading sheet for demo")
        try:
            self.upload_outreach()
            
            self.bot_update.complete_opportunity(self.name, self.today)
            self.bot_update.edit_end()
        except Exception as e:
            print(f"Could not upload sheet...{e}")
            self.bot_update.edit_end()
        
if __name__ == "__main__":
    a = OutReachCalendar()
    a.run()


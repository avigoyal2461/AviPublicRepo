import os
import pandas as pd
import time
import openpyxl
from BoxUploads import BoxUploads
from Sitecapture_Project_Creation import SiteCaptureProjectCreation
import sys
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.PAEmail import PowerAutomateEmail
# sys.path.append(r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\SiteCapture")
# from Email import Email

class ReadSiteCapExcel():
    def __init__(self):
        self.bot_name = "Sitecapture_Installs_Uploader"
        self.updater = SiteCaptureProjectCreation()
        self.SharepointConnection = self.updater.sharepoint
        self.loc = self.SharepointConnection.local_excel_path
        self.REPORTS_TO_PROCESS = []

        self.uploader = BoxUploads(bot_name=self.bot_name)

    def retrieve_df(self):
        """
        Retrieves the df the created excel file through sharepoint
        looks for sheets that have not been processed
        """
        while True:
            try:
                self.SharepointConnection.connect()
                break
            except Exception as e:
                print(e)
                print("Trying Sharepoint connection again")
                time.sleep(10)

        xl = pd.ExcelFile(self.loc, engine='openpyxl')
        df = xl.parse("Sheet1")
        counter = 0
        # print(df['Processed'])
        # try:
        print("Parsing Data")
        project_ids = []
        opp_ids = []
        names = []
        while True:
            try:
                if df.iloc[counter].at['Processed'] == "NO":
                    self.REPORTS_TO_PROCESS.append(df.iloc[counter])
                    project_ids.append(df.at[counter, 'New_Project_Id'])
                    opp_ids.append(df.at[counter, 'Opportunity_ID'])
                    names.append(df.at[counter, 'Name'])
                    # df.at[counter, 'Processed'] = "YES"
                    # print(df)
                    counter += 1
                    print("Moving to Next Entry")
                else:
                    counter += 1
                    # continue
            except:
                print("No more entries to parse through")
                break

        print("Posting to box")
        post_count = 0
        self.updater.register_bot(self.bot_name, logs=f"In Queue:{len(opp_ids)}")

        for counter, opp_id in enumerate(opp_ids):
            success = self.uploader.run_sitecapture_task(opp_id, project_ids[counter], names[counter])
        # post_count, finished_ids = self.uploader.run_sitecapture_task(opp_ids, project_ids, names)
            if success:
                self.SharepointConnection.post(project_ids[counter])
                post_count += 1
        
        self.updater.edit_end()
        
    def run(self):
        self.retrieve_df()

if __name__ == "__main__":
    a = ReadSiteCapExcel()
    # a.retrieve_df()
    a.run()

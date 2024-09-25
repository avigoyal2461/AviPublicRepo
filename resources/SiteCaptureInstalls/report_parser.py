import pandas as pd
import time
from datetime import datetime
import os
import glob
import csv
import sys
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.Outlook import outlook
from SalesforceAPI import SalesforceAPI
import re

# JEFF_ACCOUNT_ID = r'ea418f30-8802-4378-bb92-e9b48b1c3b02'
PA_ACCOUNT_ID = r'19889a32-5ffd-4343-853c-044e8f02af7e'
#
#IN ORDER TO FINISH THIS CODE NEEDS TO GET MOVED INTO THE SERVER SO THAT THE BOX UPLOAD CAN BE CALLED FROM POWER AUTOMATE
#https://us.flow.microsoft.com/manage/environments/Default-f1006ee5-f888-4308-92ea-fcaebe1c0b5e/flows/9cf3da9d-7a19-48dd-b89a-d07062c7fb8f/details
#
class SiteCaptureExcel():

    def __init__(self):
        """
        Logs into Salesforce, downloads and parses a report to retrieve next people to create a sitecapture project for (job installs)
        """
        OS_USERNAME = os.environ['USERNAME']
        
        #self.salesforce = SFReportDF()
        self.salesforce = SalesforceAPI()
        # self.download_folder = r"C:\Users\dood2\Desktop\AtomPython\SiteCapture\Downloads"
        self.download_folder = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads"
        self.download_folder = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads"

        #format datetime for tomorrow's date to pull necessary people for tomorrow's installation
        today = datetime.today()
        tday = today.strftime ("%m-%d-%Y")
        self.tomorrow = pd.to_datetime(tday) + pd.DateOffset(days=1)
        self.two_days = pd.to_datetime(tday) + pd.DateOffset(days=2)

        self.tomorrow = self.tomorrow.strftime("%m/%d/%Y")
        self.two_days = self.two_days.strftime("%m/%d/%Y")
        
        print(self.tomorrow)
        # self.tomorrow =
        self.verification_checker = False
        self.FULLPERSONLIST = []

    def create_df(self, monday=None, tuesday=None, nodate=True, report=None):

        df1 = self.salesforce.get_report(report)

        counter = 1
        # while True:
        for value in df1.values:
            # try:
            print(counter)
            # time.sleep(3)
            person_list = list(value)
            person = []
            for value in person_list:
                person.append(value)
            total = len(person)

            if nodate:
                    self.FULLPERSONLIST.append(person)
                    counter += 1
                    
            elif monday != None or tuesday != None:
                if person[total - 2] == monday or person[total - 2] == tuesday:
                    resp = ""
                    self.FULLPERSONLIST.append(person)

                    counter += 1
                else:
                    # print("SKIPPING")
                    counter += 1
                    continue
            # elif:
                # if person[total - 2] == self.two_days:
                # if person[total - 2] == self.two_days or person[total - 2] == self.tomorrow or person[total - 2] == "11/25/2022" or person[total - 2] == "11/26/2022" or person[total - 2] == "11/28/2022":
            elif person[total - 2] == self.tomorrow or person[total - 2] == self.two_days:
                resp = ""
                self.FULLPERSONLIST.append(person)

                counter += 1
            else:
                print("skipping")
                counter += 1
                continue
            # except:
            #     print("broke the loop")
            #     break
    def manual(self):
        self.FULLPERSONLIST = []
        # self.login('https://trinity-solar.my.salesforce.com/00O5b000005vrDQ')
        # self.export(True)
        self.create_df(nodate=True, report='00O5b000005vrDQ')
        # os.remove(self.file[0])
        
        return self.FULLPERSONLIST
    
    def run_weekend(self, monday, tuesday):
        self.FULLPERSONLIST = []

        # self.login('https://trinity-solar.my.salesforce.com/00O5b000005oKrx')
        # self.export(True)
        self.create_df(monday=monday, tuesday=tuesday, report='00O5b000005oKrx')
        # os.remove(self.file[0])
        
        return self.FULLPERSONLIST
    
    def run(self):
        print("running")
        self.FULLPERSONLIST = []
        
        # self.login()
        # self.export()
        # self.file = [r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\report1657649985008.csv"]
        # self.file = r'C:\Users\dood2\Desktop\AtomPython\SiteCapture\Downloads\report1657649985008.csv' #temp when i cant login to download, currently the file path is built from the export method
        self.create_df(report='00O5b000005fQEb')
        # os.remove(self.file[0])
        time.sleep(10)
        # print("Removing File")
        # os.remove(self.file[0])
        
        return self.FULLPERSONLIST
    # def glob_test(self):
    #
    #     list_of_files_after_download = glob.glob(f"{self.download_folder}/*csv")
    #     print(list_of_files_after_download)
if __name__ == "__main__":
    a = SiteCaptureExcel()
    #report = a.create_df(report='00O5b000005fQEb')
    #print(a.FULLPERSONLIST)
    #print(report)
    # a.glob_test()
    a.run()
#password
#Login
#lexNoThanks
"""
#template for tomorrow
        tempdate = str(self.tomorrow).split(" ")[0]
        tempdate = str(tempdate).split("-")
        tempmonth = int(tempdate[1])
        tempday = int(tempdate[2])
        tempmonth = str(tempmonth)
        tempday = str(tempday)
        self.tomorrow = tempmonth + "/" + tempday + "/" + str(tempdate[0])

        #template for 2 days from now
        tempdate = str(self.two_days).split(" ")[0]
        tempdate = str(tempdate).split("-")
        tempmonth = int(tempdate[1])
        tempday = int(tempdate[2])
        tempmonth = str(tempmonth)
        tempday = str(tempday)
        self.two_days = tempmonth + "/" + tempday + "/" + str(tempdate[0])
        
        # quit()
"""
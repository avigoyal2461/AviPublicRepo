from report_parser import SiteCaptureExcel
import json
import re
import requests
import os
import time
import pandas as pd
import openpyxl
from datetime import datetime
import sys
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.PAEmail import PowerAutomateEmail
# sys.path.append(r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\contractcreation")
from API_Connector import API_Connector
from BotUpdate.ProcessTable import RPA_Process_Table

class SiteCaptureProjectCreation():
    def __init__(self):
        """
        Creates projects in Sitecapture, run every hour
        """
        #https://us.flow.microsoft.com/manage/environments/Default-f1006ee5-f888-4308-92ea-fcaebe1c0b5e/flows/f0bd598c-dc9d-45cb-8cbb-2bbdcd964dfa/details
        self.json_url = "https://prod-150.westus.logic.azure.com:443/workflows/942e415811a943f3890cf6bca427bfd6/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=iDbmXpDa9O78BDLUEEZcPbPUuHIZQrbYA45QM48yuEA"
        self.SITECAP = SiteCaptureExcel()
        self.PEOPLE_LIST = []
        self.weekend_list = []
        # self.projects_location = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\temp\project_id.xlsx"
        self.projects_location = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads\temp\project_id.xlsx"
        self.name = "Sitecapture_Installs"
        self.function = f"{self.name}_Creation"
        self.sharepoint = API_Connector()
        #downloads the logs excel sheet to ensure that we are not creating duplicates
        
        self.bot_update = RPA_Process_Table()

        self.weekdays = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
        }

        self.NEXT_SUNDAY_TEMPLATE = {
        "Monday": 6,
        "Tuesday": 5,
        "Wednesday": 4,
        "Thursday": 3,
        "Friday": 2,
        "Saturday": 1,
        "Sunday": 0
        }

        self.NEXT_SATURDAY_TEMPLATE = {
        "Monday": 12,
        "Tuesday": 11,
        "Wednesday": 10,
        "Thursday": 9,
        "Friday": 8,
        "Saturday": 7,
        "Sunday": 6
        }

        self.NEXT_MONDAY_TEMPLATE = {
        "Monday": 7,
        "Tuesday": 6,
        "Wednesday": 5,
        "Thursday": 4,
        "Friday": 3,
        "Saturday": 2,
        "Sunday": 1
        }
        
        self.NEXT_TUESDAY_TEMPLATE = {
        "Monday": 8,
        "Tuesday": 7,
        "Wednesday": 6,
        "Thursday": 5,
        "Friday": 4,
        "Saturday": 3,
        "Sunday": 2
        }
        self.today_int = int(datetime.today().weekday())
        today_weekday = self.weekdays[self.today_int]
        # print(today_weekday)
        # if today_weekday == "Thursday" or today_weekday == "Friday":
        self.next_monday = self.create_date_template_Monday()
        print(f"THIS IS NEXT MONDAY - {self.next_monday}")
        # self.next_saturday = self.create_date_template_saturday()
        self.next_tuesday = self.create_date_template_Tuesday()
        print(f"THIS IS NEXT TUESDAY - {self.next_tuesday}")
        
            
    def create_date_template_saturday(self):
        """
        Determines the dates of next saturday from what today is
        """
        today = datetime.today()
        # print(today)
        tday = today.strftime("%m-%d-%Y")

        today_int = int(datetime.today().weekday())
        today_weekday = self.weekdays[today_int]
        print(f"Today is : {today_weekday}")

        saturday_template = self.NEXT_SATURDAY_TEMPLATE[today_weekday]
        nextweek_saturday = pd.to_datetime(tday) + pd.DateOffset(days=saturday_template)

        tempdate = str(nextweek_saturday)
        tempdate = tempdate.split(" ")[0]
        temp3,temp1,temp2 = tempdate.split("-")

        nextweek_saturday = temp1 + "/" + temp2 + "/" + temp3
        # print(nextweek_saturday)
        return nextweek_saturday

    def create_date_template_Monday(self):
        """
        Determines the dates of next tuesday from what today is
        """
        today = datetime.today()
        # print(today)
        tday = today.strftime("%m-%d-%Y")
        print(tday)
        # time.sleep(20)
        today_int = int(datetime.today().weekday())
        today_weekday = self.weekdays[today_int]
        print(f"Today is : {today_weekday}")

        monday_template = self.NEXT_MONDAY_TEMPLATE[today_weekday]
        nextweek_monday = pd.to_datetime(tday) + pd.DateOffset(days=monday_template)
        print(nextweek_monday)
        # time.sleep(20)
        tempdate = str(nextweek_monday)
        tempdate = tempdate.split(" ")[0]
        temp3,temp1,temp2 = tempdate.split("-")
        temp3 = int(temp3)
        temp2 = int(temp2)
        temp1 = int(temp1)
        temp3 = str(temp3)
        temp2 = str(temp2)
        temp1 = str(temp1)
        nextweek_monday = temp1 + "/" + temp2 + "/" + temp3

        return nextweek_monday
    
    def create_date_template_Tuesday(self):
        """
        Determines the dates of next tuesday from what today is
        """
        today = datetime.today()
        # print(today)
        tday = today.strftime("%m-%d-%Y")
        print(tday)
        # time.sleep(20)
        today_int = int(datetime.today().weekday())
        today_weekday = self.weekdays[today_int]
        print(f"Today is : {today_weekday}")

        tuesday_template = self.NEXT_TUESDAY_TEMPLATE[today_weekday]
        nextweek_tuesday = pd.to_datetime(tday) + pd.DateOffset(days=tuesday_template)
        print(nextweek_tuesday)
        # time.sleep(20)
        tempdate = str(nextweek_tuesday)
        tempdate = tempdate.split(" ")[0]
        temp3,temp1,temp2 = tempdate.split("-")
        temp3 = int(temp3)
        temp2 = int(temp2)
        temp1 = int(temp1)
        temp3 = str(temp3)
        temp2 = str(temp2)
        temp1 = str(temp1)
        nextweek_tuesday = temp1 + "/" + temp2 + "/" + temp3

        return nextweek_tuesday

    def retrieve_list(self):
        """
        Runs the excel site cap code to retrieve a list full of lists of people
        """
        self.PEOPLE_LIST = self.SITECAP.run()

    def send_request(self):
        # print("???")
        self.register_bot(self.function)
        post_count = 0
        self.retrieve_list()
        xl = pd.ExcelFile(self.projects_location, engine='openpyxl')
        df = xl.parse(xl.sheet_names[0])
        opportunity_ids = df['Opportunity_ID']
        opportunity_ids = list(opportunity_ids)


        people_list = []
        # people_list = [*set(list(self.PEOPLE_LIST))]
        [people_list.append(x) for x in self.PEOPLE_LIST if x not in people_list]
        print("Finished Removing Duplicates")
        weekend_opps = []

        if self.weekend_list:
            # weekend_list = [*set(list(self.weekend_list))]
            weekend_list = []
            
            [weekend_list.append(x) for x in self.weekend_list if x not in weekend_list and x not in people_list]
            
            # print("??????")
            for entry in weekend_list:
                temp_list = entry

                Opportunity_Name = str(temp_list[0])
   
                Opp_lenth = int(len(Opportunity_Name))
                Opportunity_Name = Opportunity_Name[0 : Opp_lenth]
                
                Opportunity_ID = str(temp_list[2])
                weekend_opps.append(Opportunity_ID)
                if Opportunity_ID in opportunity_ids:
                    print("skipping Duplicate")
                    continue
                else:
                    Opportunity_No = str(temp_list[1])
                    Primary_Contact = str(temp_list[5])
                    Account_Name = str(temp_list[6])
                    Install_Date = str(temp_list[9])
                    Install_Date = self.reformat_date(Install_Date)
                    Managing_Office = str(temp_list[3])

                    if "Trinity Solar" in Managing_Office:
                        try:
                            try:
                                tsolar, Managing_Office, contractor = Managing_Office.split(" - ") 
                            except:
                                tsolar, Managing_Office, contractor = Managing_Office.split("-") 
                        except:
                            tsolar, Managing_Office = Managing_Office.split("-")
                        Managing_Office = self.site_to_value(Managing_Office)
                        
                    else:
                        Managing_Office = str(temp_list[4])
                        Managing_Office = self.site_to_value(Managing_Office)

                    params = {
                    "Due_Date" : Install_Date,
                    "Opportunity_Name" : Opportunity_Name,
                    "Opportunity_No" : Opportunity_No,
                    "Primary_Contact" : Primary_Contact,
                    "Managing_Office" : Managing_Office,
                    "Account_Name" : Account_Name,
                    "Opportunity_ID": Opportunity_ID
                    }
                    
                    self.update_bot_status(self.function, "Posting", Opportunity_ID)
                    
    #id is the same as project id
                    resp = requests.post(self.json_url, json=params)
                    time.sleep(1)
                    post_count += 1
                    # self.update_status("Posting")
                    print(f"Posted opportunity")
                    self.complete_opportunity(self.function, Opportunity_ID)
                    # quit()
                    time.sleep(4)

        for value in people_list:
            # print("working")
            temp_list = value

            Opportunity_Name = str(temp_list[0])
            Opp_lenth = int(len(Opportunity_Name))
            Opportunity_Name = Opportunity_Name[0 : Opp_lenth]
            
            Opportunity_ID = str(temp_list[2])

            if Opportunity_ID in opportunity_ids or Opportunity_ID in weekend_opps:
                print("skipping duplicate")
                continue
            else:
                Opportunity_No = str(temp_list[1])
                Primary_Contact = str(temp_list[5])
                Account_Name = str(temp_list[6])
                Install_Date = str(temp_list[9])
                Install_Date = self.reformat_date(Install_Date)
                Managing_Office = str(temp_list[3])

                if "Trinity Solar" in Managing_Office:
                    try:
                        print(Managing_Office)
                        try:
                            tsolar, Managing_Office, contractor = Managing_Office.split(" - ") 
                        except:
                            tsolar, Managing_Office, contractor = Managing_Office.split("-") 
                    except:
                        tsolar, Managing_Office = Managing_Office.split("-")
                        
                    Managing_Office = self.site_to_value(Managing_Office)
                else:
                    Managing_Office = str(temp_list[4])
                    Managing_Office = self.site_to_value(Managing_Office)

                params = {
                "Due_Date" : Install_Date,
                "Opportunity_Name" : Opportunity_Name,
                "Opportunity_No" : Opportunity_No,
                "Primary_Contact" : Primary_Contact,
                "Managing_Office" : Managing_Office,
                "Account_Name" : Account_Name,
                "Opportunity_ID": Opportunity_ID
                }
                self.update_bot_status(self.function, "Posting", Opportunity_ID)

            
#id is the same as project id
                resp = requests.post(self.json_url, json=params)
                time.sleep(2)
                post_count += 1
                print(f"Posted opportunity")
                self.complete_opportunity(self.function, Opportunity_ID)

                # quit()
                time.sleep(4)
        
        self.edit_end()
            
    def reformat_date(self, date):
        """
        Reformats date from m/d/yyy to yyyy/m/d
        """
        date = str(date)
        print(date)
        month, day, year = date.split("/")
        if len(month) == 1:
            month = f"0{month}"
        if len(day) == 1:
            day = f"0{day}"
        date = f"{year}{month}{day}"
        return date
    
    def site_to_value(self, site):
        if "PA" in site[0:3]:
            site = "PA"
            
        if "Wareham" in site:
            site = "Wareham"

        if "FL" in site:
            site = "FL"
            
        SITES = {
        'FL': 12369,
        'MAW': 5589,
        'HQ': 5591,
        'NJ': 5591,
        'MAE': 5588,
        'CT': 5587,
        'PA': 6280,
        'NY- NYC/LI': 5592,
        'NYLI': 5592,
        # 'NYUS': 5593,
        'NYUS': 5592,
        # 'Chester NY': 5593,
        'Chester NY': 5592,
        # 'NY- Lower Hudson': 5593,
        'NY- Lower Hudson': 5592,
        'MD': 5590,
        'Holyoke': 5589,
        'MA- Holyoke': 5589,
        'MA- Wareham': 5588,
        'Wareham': 5588,
        'RI': 5588,
        'NH': 5588
        }
        try:
            office = SITES[site]
        except Exception as e:
            print(f"Could not change office value {e}")
            # quit()
            return site

        return office
    
    def register_bot(self, name=None, logs=None):
        if not name:
            self.function = name
        self.bot_update.register_bot(name, logs=logs)


    def update_status(self, name=None, status=None):
        if not name:
            name = self.function
        self.bot_update.update_status(name)

    def update_bot_status(self, bot_name=None, status=None, identifier=None):
        self.bot_update.update_bot_status(bot_name=bot_name, status=status, identifier=identifier)
        return True
    
    def complete_opportunity(self, bot_name, identifier):
        self.bot_update.complete_opportunity(bot_name=bot_name, identifier=identifier)
    
    def edit_end(self):
        self.bot_update.edit_end()

    def run_manual(self):
        self.sharepoint.connect()
        self.list = self.SITECAP.manual()
        self.run()
        
    def run_weekend(self):
        self.sharepoint.connect()
        self.weekend_list = self.SITECAP.run_weekend(monday=self.next_monday, tuesday=self.next_tuesday)
        # self.weekend_list = self.SITECAP.run_weekend(monday=self.next_monday)
        return True

    def run(self):
        self.sharepoint.connect()
        self.send_request()

if __name__ == "__main__":
    a = SiteCaptureProjectCreation()
    # a.send_request()
    a.run()

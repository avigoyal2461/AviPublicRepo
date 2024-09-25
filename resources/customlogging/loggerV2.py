#an attempt at dataclasses, will not use as i need to send an excel report
from dataclasses import asdict, dataclass
import sys
import os
sys.path.append(os.environ['autobot_modules'])
# import email
import pandas as pd
from datetime import datetime
# import time
import os
# import inspect 
import openpyxl
from AutobotEmail.PAEmail import PowerAutomateEmail

@dataclass(frozen=True, repr=True, order=True)
class SunnovaLogger():
    # def __init__(self):
        # self.cols = ["Date","Contract ID", "Opportunity ID", "Opportunity Name", "Process", "Uploaded"]
    id: int
    Date: str
    Contract_ID: str
    Opportunity_ID: str
    Opportunity_Name: str
    Address: str
    Process: str
    Uploaded: bool
    Comments: str
    Type: str = None

    def create_excel(log_list, location=None, log_name=None, email_subject=None, text=None, html=None):
        if not location:
            if not log_name:
                location = os.path.join(os.getcwd(), "Logs.xlsx")
            else:
                location = os.path.join(os.getcwd(), log_name)
        elif location and not log_name:
            location = os.path.join(os.getcwd(), "Logs.xlsx")
        else:
            location = location
        try:
            os.remove(location)
        except:
            print("Could not remove current log excel sheet")
            pass
        #creates the dir
        try:
            # os.mkdir(self.location)
            wb = openpyxl.Workbook()  # open a workbook
            # ws = wb.active  # get the active worksheet
            wb.save(location)  
        except Exception as e:
            print(f"{e}")

        df = pd.DataFrame.from_dict(log_list)
        df.to_excel(location)
        email = ['jeff.macdonald@trinity-solar.com', 'avigoyal@trinity-solar.com']
        if not email_subject:
            PowerAutomateEmail.send(location, text=text, html=html, email_recipient=email)
        else:
            PowerAutomateEmail.send(location, email_subject=email_subject, text=text, html=html, email_recipient=email)
        return True

def main():
    # print(inspect.getmembers(SunnovaLogger, inspect.isfunction))
    log_list = []
    logs = SunnovaLogger(1, "this date", "this contract", "this opportunity", "this name", "this address", "this process", True, ["something", "else"], "temp?")
    log_list.append(logs)
    comments = ["this", "else"]
    logs = SunnovaLogger(2, "this date2", "this contrac2t", "t2his opportunity", "2this name", "this addrrss2", "2this process", True, comments)
    log_list.append(logs)
    df = pd.DataFrame.from_dict(log_list)
    print(df)
    SunnovaLogger.create_excel(log_list, log_name="test.xlsx")
    # print(logs)
    # print(asdict(logs))
    # print(log_list)
    for entry in log_list:
        print(asdict(entry))
        
if __name__ == "__main__":
    main()

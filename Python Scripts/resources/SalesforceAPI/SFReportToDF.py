import sys
import os
sys.path.append(os.environ['autobot_modules'])
from SalesforceAPI.SFConnection import SFConnection
from io import StringIO
import csv 
import pandas as pd
import requests  

class SFReportDF(SFConnection):
    def __init__(self):
        super().__init__()
        self.sf = super().connect()
        
    def get_report(self, reportId):
        """
        Returns a salesforce report by a given ID
        """
        orgParams = 'https://trinity-solar.my.salesforce.com/' # you can see this in your Salesforce URL
        exportParams = '?isdtp=p1&export=1&enc=UTF-8&xf=csv'

        # Downloading the report:
        reportUrl = orgParams + reportId + exportParams
        reportReq = requests.get(reportUrl, headers=self.sf.headers, cookies={'sid': self.sf.session_id})
        reportData = reportReq.content.decode('utf-8')
        reportDf = pd.read_csv(StringIO(reportData))
        return reportDf

if __name__ == "__main__":
    a = SFReportDF()
    print(a.get_report('00O5b000005fOsU'))

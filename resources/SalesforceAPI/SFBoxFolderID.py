import sys
import os
sys.path.append(os.environ['autobot_modules'])
from SalesforceAPI.SFConnection import SFConnection
from SalesforceAPI.SFQuery import SFQuery

class SFBoxID(SFConnection):
    def __init__(self):
        super().__init__()
        self.sf = super().connect()
    
    def get_box_folder_id(self, opportunityID):
        """
        Returns Box ID by a given Opportunity ID
        """
#         print(self.sf)
        df = SFQuery().Select(f"""SELECT box__Folder_ID__c FROM box__FRUP__c WHERE Opportunity__c = '{opportunityID}' Limit 1""")
        item = list(df['box__Folder_ID__c'])

        return item[0]

if __name__ == "__main__":
    a = SFBoxID()
    print(a.get_box_folder_id("006Pl000004qdJAIAY"))

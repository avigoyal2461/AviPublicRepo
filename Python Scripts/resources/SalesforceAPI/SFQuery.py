import sys
import os
sys.path.append(os.environ['autobot_modules'])
from SalesforceAPI.SFConnection import SFConnection
from simple_salesforce import SFType
import pandas as pd

class SFQuery(SFConnection):
    def __init__(self):
        super().__init__()
        self.sf = super().connect()
        # print(str(self.sf.instance_url))
        # quit()

    def Update(self, sf_item, update_data, id):
        """
        Updates an item in sf, sf_item refers to the table we are updating
        update_data can be given as dictionary - {}
        ex:
        sf_item = Opportunity
        update_data = {}
        update_data['Opportunity__c'] = "ID"
        SFQuery().update(sf_item, update_data)
        """
        sf_type = SFType(sf_item, self.sf.session_id, self.sf.sf_instance)

        updater = sf_type.update(id, update_data)
        return updater

    def Create(self, sf_item, data):
        """
        Creates an item in sf
        sf_item references the field we want to create
        data is json data to reflect the fields we want to create on the item tag
        """
        sf_type = SFType(sf_item, self.sf.session_id, self.sf.sf_instance)

        updater = sf_type.create(data)
        return updater

    def Select(self, query):
        selection = pd.DataFrame(self.sf.query(query)['records'])
        return selection

    def Execute(self, query):
        execution = self.sf.query(query)
        return execution
    
    def QueryAll(self, query):
        execution = self.sf.query_all(query)
        return execution

    def Delete(self, sf_item, id):
        sf_type = SFType(sf_item, self.sf.session_id, self.sf.sf_instance)
        deletion = sf_type.delete(id)

        return deletion

if __name__ == "__main__":
    a = SFQuery()
    #print(a.Update("User", {'IsActive': False}, "0055b00000Sdyhr"))
    #print(a.sf.delete("UserPackageLicense"))

    #a.Update("Opportunity", None)
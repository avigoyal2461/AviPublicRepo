# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import pytesseract
import os
import re
import requests
from Files.FileHandler import FileHandler
from FlexiCapture.Batch import Batch
from FlexiCapture.config import bill_import_path, bill_export_path, batch_path

class ElectricBillReader:
    def __init__(self):
        self.bill_import_path = bill_import_path
        self.bill_export_path = bill_export_path
        self.batch_path = batch_path
        self.queue = []
        self.file_handler = FileHandler()
        self.completed_queue = []

    def new_bill(self, file_location, direct_lead_id):
        new_batch = Batch(self.get_next_batch_number())
        item = {
            'direct_lead_id':direct_lead_id,
            'file_location': file_location,
            'batch': new_batch
            }
        self.queue.append(item)

    def get_next_batch_number(self):
        digit_regex = re.compile(r'\d+')
        nums = []
        for file_name in os.listdir(self.batch_path):
            match = re.search(digit_regex, file_name)
            nums.append(int(match.group()))
        return max(nums) + 1

    def completed_items(self):
        if self.completed_queue:
            return True
        else:
            return False

    def send_completed_items(self):
        for item in self.queue:
            if item['batch'].check_completed():
                self.completed_queue.append(item)
                self.queue.remove(item)
        for item in self.completed_queue:
            self.send_completed_item(item)

    def send_completed_item(self, completed_item):
        batch = completed_item['batch']
        direct_lead = completed_item['direct_lead_id']
        finished_url = r''
        content = batch.get_bill_data()
        batch['direct_lead_id'] = direct_lead
        requests.post(finished_url, json=content)

    # TESTS

    def _test_get_salesforce_token(self):
        params = {
            "grant_type": "password",
            "client_id": "XXX.YYY", # Consumer Key
            "client_secret": "0000000000000000", # Consumer Secret
            "username": "kevin.janssen@trinity-solar.com", # The email you use to login
            "password": "sfautomationpassword + security token" # Concat your password and your security token
        }
        r = requests.post("https://login.salesforce.com/services/oauth2/token", params=params)
        # if you connect to a Sandbox, use test.salesforce.com instead
        access_token = r.json().get("access_token")
        instance_url = r.json().get("instance_url")
        print("Access Token:", access_token)
        print("Instance URL", instance_url)

    def _test_endpoint(self):
        test_url = r'https://trinity-solar--qa.my.salesforce.com/services/apexrest/UtilityBill/v1/Bill/'
        test_content = {'usage':'1234',
                'utility':'Eversource',
                'account_number':'123456',
                'meter_number':'321654',
                'name':'Test User',
                'email':'Test@email.com',
                'direct_lead_id':'DL-999999'
                }
        session = requests.post(test_url, json=test_content)
        print(session.url)
        print(session.text)

if __name__ == "__main__":
    tester = ElectricBillReader()
    tester._test_endpoint()
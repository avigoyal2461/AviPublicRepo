# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import json
import re
import requests
import datetime
import jwt
from Files.FileHandler import FileHandler
from FlexiCapture.Batch import Batch
from queues.BatchQueue import BatchQueue
from FlexiCapture.config import bill_import_path, bill_export_path, batch_path, new_batches_path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s', handlers=[
        logging.FileHandler(r".\logs\batch_handler.log"),
        logging.StreamHandler()
    ])

private_key_path = r'C:\Users\RPAadmin\Desktop\automation\api\resources\FlexiCapture\jwt-key'

class BatchHandler:
    def __init__(self):
        self.bill_import_path = bill_import_path
        self.bill_export_path = bill_export_path
        self.batch_path = batch_path
        self.queue = BatchQueue()
        self.file_handler = FileHandler()
        self.completed_queue = []

    def new_bill(self, file_location, direct_lead_id, callback, req_id):
        """Adds a new bill to the queue."""
        batch_num = self.get_next_batch_number()
        batch_export_path = self.bill_export_path + f'\\Batch HF_ID{str(batch_num)}'
        now = datetime.datetime.now()
        date_time = now.strftime(r"%m/%d/%Y %H:%M:%S")
        item = {
            'direct_lead_id':direct_lead_id,
            'file_location': file_location,
            'batch_export_path': batch_export_path,
            'callback':callback,
            'initial_time': date_time,
            'batch_number':str(batch_num),
            'reqid':req_id
            }
        self.queue.add(item)

    def get_next_batch_number(self):
        digit_regex = re.compile(r'\d+')
        nums = []
        for file_name in os.listdir(self.batch_path):
            match = re.search(digit_regex, file_name)
            nums.append(int(match.group()))
        return max(nums) + 1

    def run_completed_batches(self):
        completed = self.queue.get_completed_items()
        for item in completed:
            new_batch = Batch(item['batch_number'])
            info = new_batch.get_info()
            info['direct_lead_id'] = item['direct_lead_id']
            info['reqid'] = item['reqid']
            logging.info(f'Found batch info: {info}')
            callback = item['callback']
            if callback:
                self.send_batch_info(info, url=item['callback'])
            else:
                self.send_batch_info_to_salesforce(info)
            self.queue.remove(new_batch.get_batch_number())
    
    def run_expired_batches(self):
        expired = self.queue.get_expired_items()
        for item in expired:
            req_obj = {
             'usage': '',
             'utility': '',
             'account_number': '',
             'meter_number': '',
             'name': '',
             'email': '',
             'direct_lead_id': item['direct_lead_id'],
             'reqid': item['reqid']
             }
            callback = item['callback']

            if callback:
                self.send_batch_info(info, url=callback)
            else:
                self.send_batch_info_to_salesforce(info)
    
    def _test_run_completed_batch(self, completed_item):
        new_batch = Batch(completed_item['batch_number'])
        info = new_batch.get_info()
        logging.info(f'Found batch info: {info}')

    def send_batch_info(self, info, url):
        try:
            logging.info(f'Sending batch info to {url}')
            response = requests.post(url, json=info)
            logging.info(response.text)
        except Exception as e:
            logging.error(f'Error: {e}')
            response = None
        return response

    def send_batch_info_to_salesforce(self, info):
        token = self.jwt_login()
        headers = {
            'Authorization':f'Bearer {token}'
        }
        try:
            response = requests.post(url, json=info, headers=headers)
        except:
            response = None
        return response


    def _completed_items(self):
        if self.completed_queue:
            return True
        else:
            return False

    def _send_completed_items(self):
        """Sends completed items from the queue to the completed queue."""
        for item in self.queue:
            if item['batch'].check_completed():
                self.completed_queue.append(item)
                self.queue.remove(item)
        for item in self.completed_queue:
            self.send_completed_item(item)

    def _send_completed_item(self, completed_item):
        batch = completed_item['batch']
        direct_lead = completed_item['direct_lead_id']
        finished_url = completed_item['callback']
        content = batch.get_bill_data()
        batch['direct_lead_id'] = direct_lead
        requests.post(finished_url, json=content)

    def _get_new_batches(self):
        batches = []
        batches_queued = os.listdir(new_batches_path)
        if not batches_queued:
            return None
        for new_batch in batches_queued:
            try:
                if '.json' in new_batch:
                    data = json.loads(os.path.join(new_batches_path, new_batch))
                    batches.append(data)
            except:
                logging.error(f'Unable to access new batch request: {new_batch}...')

        return batches

    def _process_new_batches(self):
        new_batches = self.get_new_batches
        if new_batches:
            for new_batch in new_batches:
                pass

    def get_all_batches_percent_success(self):
        """Returns a float of the success rate out of 1."""
        success = 0
        fail = 0
        for file_name in os.listdir(self.bill_export_path):
            batch_number = file_name.replace('Batch HF_ID','')
            new_batch = Batch(batch_number)
            info = new_batch.get_info()
            info['direct_lead_id'] = 'test_id'
            if info['usage']:
                success += 1
            else:
                fail += 1
        return success / (success + fail)

    def get_all_batches_rate_percent_success(self):
        """Returns a float of the success rate out of 1."""
        success = 0
        fail = 0
        for file_name in os.listdir(self.bill_export_path):
            batch_number = file_name.replace('Batch HF_ID','')
            new_batch = Batch(batch_number)
            info = new_batch.get_info()
            info['direct_lead_id'] = 'test_id'
            if info['usage']:
                success += 1
            else:
                fail += 1
        return success / (success + fail)

    # TESTS

    def _test_get_salesforce_token(self):
        params = {
            "grant_type": "password",
            "client_id": "3MVG9FxR3Tq3eZN.nPcbwB724b0LoxJKrOB0Ad6.onPCahvgDwTdLPfnrp9stPy8IK_9NiawSy5Buk1pgMIuM", # Consumer Key
            "client_secret": "E1C325BD757C7D631A43FE6CA96E8A7576C7B775132B2D81B20082FD61E3A217", # Consumer Secret
            "username": "kevin.janssen@trinity-solar.com", # The email you use to login
            "password": "sfautomationpasswordpWODhD38gmATjGERCWhq3WJB6" # Concat your password and your security token
        }
        r = requests.post("https://login.salesforce.com/services/oauth2/token", params=params)
        # if you connect to a Sandbox, use test.salesforce.com instead
        logging.info(r.text)
        access_token = r.json().get("access_token")
        instance_url = r.json().get("instance_url")
        return access_token

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
        auth = {'Authorization': 'Bearer ' + self.jwt_login()}
        response = requests.post(test_url, json=test_content, headers=auth)
        return response

    def jwt_login(self):
        endpoint = 'https://test.salesforce.com'
        consumer_id = r'3MVG9d3kx8wbPieFvpNsDXbIc8VIajncBd4TzD8CLqfZF_C0v7s19CV2GZQzVfj_k_AjDqe6sUE8A9yA_q4l5'
        with open(r'C:\Users\RPAadmin\Desktop\automation\api\resources\FlexiCapture\ebillapi.key', 'r') as key_file:
            private_key = key_file.read()
        jwt_payload = jwt.encode(
            { 
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
                'iss': consumer_id,
                'aud': endpoint,
                'sub': 'kevin.janssen@trinity-solar.com.stagingfc'
                # 'sub': 'kevin.janssen@trinity-solar.com'
            },
            private_key,
            algorithm='RS256'
        )
        result = requests.post(
            endpoint + '/services/oauth2/token',
            data={
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': jwt_payload
            }
        )
        body = result.json()
        try:
            sf_token = body['access_token']
        except:
            sf_token = None
        return sf_token


if __name__ == "__main__":
    test_item = {
        'direct_lead_id':'direct_lead_id',
        'file_location': 'file_location',
        'batch_export_path': r'C:\Users\RPA_Bot_4\Desktop\ExportData\batch_export_path3',
        'callback':'callback',
        'initial_time': datetime.datetime.now(),
        'batch_number': '455'
    }
    tester = BatchHandler()
    response = tester.get_all_batches_rate_percent_success()
    logging.info(response)
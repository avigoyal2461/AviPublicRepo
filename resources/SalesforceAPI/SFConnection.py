
import os
import json
import requests
import sys
from requests.adapters import HTTPAdapter, Retry
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceAuthenticationFailed
sys.path.append(os.environ['autobot_modules'])
from config import SFDC_API_ASSERTION, SFDC_API_ENDPOINT, SALESFORCE_PREPROD_URL, PREPROD_ASSERTION

def request_session():
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = request_session()
# CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
# CONFIG_PATH = '\\'.join([CONFIG_PATH, 'config.json'])

class SFConnection():
    def __init__(self):
        # self.connection = self.connect()
        # with open(CONFIG_PATH) as config_file:
        #     configjson = json.load(config_file)
        #     configjwt = configjson["JWT"]
        #     config_file.close()
        # self.assertion = configjwt['assertion']
        self.assertion = SFDC_API_ASSERTION
        
    def connect(self):
            """
            Simple SFDC using JWT authentication token
            rather than username password
            """
            result = requests.post(
                SFDC_API_ENDPOINT,
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': self.assertion
                }
            )
            body = result.json()

            if result.status_code != 200:
                raise SalesforceAuthenticationFailed(body['error'], body['error_description'])
            
            return Salesforce(instance_url=body['instance_url'], session_id=body['access_token'], session=session)

    def connect_staging(self):
        """
        Simple SFDC using JWT authentication into staging
        """
        result = requests.post(
                SALESFORCE_PREPROD_URL,
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': PREPROD_ASSERTION
                }
            )
        body = result.json()

        if result.status_code != 200:
            raise SalesforceAuthenticationFailed(body['error'], body['error_description'])
            
        return Salesforce(instance_url=body['instance_url'], session_id=body['access_token'], session=session)

import os
import sys
sys.path.append(os.environ['autobot_modules'])
from customlogging import logger
from AutobotEmail.graph_config import app_id, app_secret, tenant_id, account_id, PA_ACCOUNT_ID
import requests
import time
import re


credentials = (app_id, app_secret)


class Outlook:
    def __init__(self):
        self.access_token = self.get_new_access_token()
        self.account_id = account_id

    def get_new_access_token(self):
        logger.info('Getting outlook access token...')
        request_body = f"""client_id={app_id}
                        &scope=https%3A%2F%2Fgraph.microsoft.com%2F.default
                        &client_secret={app_secret}
                        &grant_type=client_credentials"""
        access_token_request = requests.post(
            f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token', data=request_body)
        if str(access_token_request.status_code) != '200':
            logger.warning('Bad response, trying again...')
            time.sleep(10)  # Minor delay in case of api issues
            return self.get_new_access_token()
        return access_token_request.json()['access_token']

    # Send functions

    def send_email(self, email):
        self.access_token = self.get_new_access_token()
        response = self.create_email(email)
        email_json = response.json()
        email_id = email_json['id']
        headers = {'Authorization': 'Bearer ' + self.access_token,
                   'Content-Type': 'application/json'}
        send_email_response = requests.post(
            f'https://graph.microsoft.com/v1.0/users/{self.account_id}/messages/{email_id}/send', headers=headers)
        return send_email_response

    def create_email(self, email):
        self.access_token = self.get_new_access_token()
        email_json = email.json()
        headers = {'Authorization': 'Bearer ' + self.access_token,
                   'Content-Type': 'application/json'}
        create_email_response = requests.post(
            f'https://graph.microsoft.com/v1.0/users/{self.account_id}/messages', json=email_json, headers=headers)
        return create_email_response

    def get_mail(self, user_id=account_id):
        self.access_token = self.get_new_access_token()
        headers = {'Authorization': 'Bearer ' + self.access_token}
        mail_response = requests.get(
            f'https://graph.microsoft.com/v1.0/users/{user_id}/messages', headers=headers)
        return mail_response.json()  # TODO: Validate access to this account
        
    def get_message(self, message_id, user_id=account_id):
        self.access_token = self.get_new_access_token()
        headers = {'Authorization': 'Bearer ' + self.access_token}
        mail_response = requests.get(
            f'https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}', headers=headers)
        return mail_response.json()

    def get_mail_folders(self, user_id=account_id):
        full_data = []
        self.access_token = self.get_new_access_token()
        headers = {'Authorization': 'Bearer ' + self.access_token}
        mail_response = requests.get(
            f'https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders', headers=headers)

        data = mail_response.json()
        for item in data['value']:
            full_data.append(f"{item['displayName']},{item['id']}")

        while '@odata.nextLink' in data:
            next_link = data['@odata.nextLink']
            response = requests.get(next_link, headers=headers)
            data = response.json()
            for item in data['value']:
                full_data.append(f"{item['displayName']},{item['id']}")
        return full_data

    def get_ts_net_verification_code(self):
        self.access_token = self.get_new_access_token()
        first_ten_mailbox = self.get_mail()
        for email in first_ten_mailbox['value']:
            if email['subject'] == 'Security Code':
                code = email['bodyPreview'][23:29]
                return code
        return None

    def get_sunnova_verification_code(self):
        self.access_token = self.get_new_access_token()
        # first_ten_mailbox = self.get_mail(JEFF_ACCOUNT_ID)
        first_ten_mailbox = self.get_mail(PA_ACCOUNT_ID)
        PA_ACCOUNT_ID
        for email in first_ten_mailbox['value']:
            if 'your sunnova code' in email['subject'].lower():
                # groups = re.search(r"is (\d{6})", email['bodyPreview'])

                groups = re.search(r"is (\d{6})", str(email['body']))
                code = groups.group(1)
                return code
        return None

    # def get_salesforce_verification_code(self, account_id=JEFF_ACCOUNT_ID):
    def get_salesforce_verification_code(self, account_id=PA_ACCOUNT_ID):
        self.access_token = self.get_new_access_token()
        first_ten_mailbox = self.get_mail(account_id)
        for email in first_ten_mailbox['value']:
            if 'your identity in Salesforce' in email['subject']:
                message_id = email['id']
                body = self.get_message_body(message_id, account_id)
                # groups = re.search(r"Verification Code: (\d{5})", body)
                groups = re.search(r"Verification Code: (\d{6})", body)
                code = groups.group(1)
                return code
        return None

    def get_message_body(self, message_id, user_id=account_id) -> str:
        message_info = self.get_message(message_id, user_id)
        return message_info['body']['content']


outlook = Outlook()

# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import requests
import logging
from Salesforce.config import task_url


def create_task(related_id, subject, err_message):
    """Creates a Salesforce Task relating to a given ID."""
    content = {
            'error':err_message,
            'opp_id':related_id,
            'subject': subject
        }
    try:
        requests.post(task_url, json=content)
    except:
        logging.info(f'Unable to create salesforce task for {related_id}...')

def get_opportunity_name(opportunity_id) -> str:
    """
    Gets an opportunity name from a given id through power automate flow.

        Parameters:
            opportunity_id (str): A salesforce opportunity id.
        Returns:
            opportunity_name (str): The name for an opportunity.
    """
    url = r'https://prod-51.westus.logic.azure.com:443/workflows/b72459a05e6f4bffa0499903ec32ec6e/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=fZSZ2QDrx4racBMiKHpCd_9GWWZmmWAjlk9h0wN5J7U'
    data = {
        "opportunityID": opportunity_id
    }
    logging.info('Getting opportunity information...')
    response = requests.post(url, json=data)
    try:
        return response.json()['opportunityName']
    except KeyError:
        return ''

def get_opportunity_info(opportunity_id) -> dict:
    """
    Gets information about an opportunity from the id. Uses power automate flow.

        Parameters:

            opportunity_id (str): The opportunity ID.
    """
    url = r'https://prod-110.westus.logic.azure.com:443/workflows/e888900866d34233af514f03446aac0c/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=gKR_zeE0PjrKxekZvo65FNlJxXEPkxIB6FzpY_iXhHo'
    data = {
        "opportunity_id": opportunity_id
    }
    logging.info('Getting opportunity information...')
    response = requests.post(url, json=data)
    return response.json()

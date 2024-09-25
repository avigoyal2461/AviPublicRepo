import requests

from .SalesforcePortal import SalesforcePortal

pathways_url = r'https://prod-140.westus.logic.azure.com:443/workflows/c85ac6e0c20a4cadb02f017469198d2b/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=0-ptX9HU3ZA3_rVd0YjoKQyECwzqp6-wV43qGdQUgco'
#https:/make.powerautomate.com/environments/Default-f1006ee5-f888-4308-92ea-fcaebe1c0b5e/flows/2c92d9de-5121-4e90-816d-32ac841763ab?v3=false&v3survey=true

class Salesforce:
    def __init__(self) -> None:
        self.portal = SalesforcePortal()

    def download_genesis_report(self, report_url) -> str:
        """
        Downloads a report from a given url.
        Returns a string to a genesis report csv file.
        """
        return self.portal.download_genesis_report(report_url)

    def get_street_side_pathways(self, opportunity_id) -> bool:
        """
        Returns if the AHJ for the opp has street side pathways enabled.
        """
        body = {"opportunity_id": opportunity_id}
        res = requests.post(pathways_url, json=body)
        return res.json()['has_pathways'] == 'True'

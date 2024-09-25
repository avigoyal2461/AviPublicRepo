import sys
import os
sys.path.append(os.environ['autobot_modules'])
#from Sunnova.SunnovaPortal import SunnovaPortal
import json
import requests 
import time
from config import SUNNOVA_USERNAME, SUNNOVA_PASSWORD
from requests.auth import HTTPBasicAuth

class SunnovaAPI():
	def __init__(self):
		#self.PANDAS_BASE_URL = r"https://trinityapipanda.azurewebsites.net/api/Sunnova/"
		#self.PANDAS_HEADERS = {
        #    'UserKey': "2ac1a41a-a2e1-4caf-af1c-2aaf4244e2cf",
        #    'accept': "application/json"
        #}

		self.SUNNOVA_BASE_URL = r"https://dealerapi.sunnova.com/"
		self.AUTHENTICATION_URL = self.SUNNOVA_BASE_URL + "authentication"
		self.SUNNOVA_HEADERS = {}
		self.token = None
		
	
	def get_bearer_token(self):
		"""
		Gets a bearer token from sunnova
		"""
		auth = HTTPBasicAuth(SUNNOVA_USERNAME,SUNNOVA_PASSWORD)
		
		resp = requests.get(self.AUTHENTICATION_URL, auth=auth)
		if resp.status_code != 200:
			print("Failed to get token")
			return None

		self.token = resp.json()['token']
		self.SUNNOVA_HEADERS['Authorization'] = f'Bearer {self.token}'

		return self.token

	def get_sunnova_project_id(self, sunnova_id):
		"""
		Gets the sunnova ID using webscraping, expected that we are already logged into the website
		this will search for the project then return the found ID in the url
		"""
		self.get_bearer_token()
		resp = requests.get(self.SUNNOVA_BASE_URL + f"services/v1.1/systemprojects?Sunnova_Id={sunnova_id}", headers=self.SUNNOVA_HEADERS)
		
		items = resp.json()
		sunnova_project_id = items[0]['Id']

		return sunnova_project_id

	def get_project_block_id(self, sunnova_id, search_text=None):
		"""
		Sunnova Request all project blocks to return a specific project block Id
		Required:
			Sunnova ID : The ID that links the Sunnova page to the user, specified in the project blocks page URL
		Not Required: 
			search_text : this will be the project block we want the ID for
		"""
		self.get_bearer_token()
		resp = requests.get(self.SUNNOVA_BASE_URL + f"services/v1.0/systemprojects/{sunnova_id}", headers=self.SUNNOVA_HEADERS)
		#resp = requests.get(self.BASE_URL + "GetProjectBlocks/" + sunnova_id, headers=self.HEADERS)
		items = resp.json()

		if search_text:
			for item in items['Project_Blocks']:
				if item['Name'] == search_text:
					return item['Id']
		else:
			return items
	
	def upload_pdf(self, block_id, pdf_src_path): #***
		"""
		Request upload PDF
		Required: 
			Block ID - Project block ID we want to upload to
			pdf_src_path - local path to pdf path
		This will upload the given file to the given project block
		"""
		self.get_bearer_token()

		files = {'file': (os.path.basename(pdf_src_path),open(pdf_src_path, 'rb'), 'text/pdf')}
		headers = {
			'Authorization': f'Bearer {self.token}',
		}

		resp = requests.post(self.SUNNOVA_BASE_URL + f"services/v1.0/projectblocks/{block_id}/documents", headers=self.SUNNOVA_HEADERS, files=files)
		
		if resp.status_code == 201:
			return True
			
		if "the status is submitted" in str(resp.content.lower()) or "the status is approved" in str(resp.content.lower()):
			return True

		return False

	def download_document(self, block_id, document_id, download_path=None):
		"""
		Requests to download a document from sunnova using the block and document id
		download path is optional, if given we will write to path if not then will return bytes of the pdf.
		"""
		self.get_bearer_token()
		url = self.SUNNOVA_BASE_URL + f"services/v1.0/projectblocks/{block_id}/documents/{document_id}"

		resp = requests.get(url, headers=self.SUNNOVA_HEADERS)

		if download_path:
			with open(download_path, 'rb') as f:
				f.write(resp.content)
				f.close()
			return True
		else:
			return resp
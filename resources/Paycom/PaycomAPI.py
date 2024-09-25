#A paycom API wrapper
import requests
import json
import sys
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime 

sys.path.append(os.environ['autobot_modules'])
from config import PAYCOM_USERNAME, PAYCOM_PASSWORD

class PaycomAPI():
	def __init__(self):
		self.BASE_URL = "https://api.paycomonline.net/v4/rest/index.php/api/v1/"
		self.auth = HTTPBasicAuth(PAYCOM_USERNAME,PAYCOM_PASSWORD)
		self.user_id = None
		self.today = datetime.now().date()

	def get_new_hires(self, ids=False):
		"""
		Requests the Paycom API to return all new hires in a set date range of the last two weeks
		set ids to True if looking for new hire ids in the same range
		"""
		#url = self.BASE_URL + f"newhire/{self.user_id}/customfield"
		url = self.BASE_URL + f"employeenewhire"
		if ids:
			url = self.BASE_URL + f"newhireids"
		resp = requests.get(url, auth=self.auth)
		return resp.json()

	def get_new_hire_information(self, new_hire_id, customfield=None):
		"""
		Requests the Paycom API to return information on a new hire employee
		if customfields, please give as dictionary form for requested fields
		"""
		url = self.BASE_URL + f"newhire/{new_hire_id}"
		if customfield:
			url += "customfield"

		resp = resp.get(url, auth=self.auth)
		return resp.json()

	def get_terminated_employees(self):
		"""
		Requests the Paycom API to return all terminated employees, no date range available
		"""
		url = self.BASE_URL + f"employeeid?eestatus=T&pagesize=500"
		resp = resp.get(url, auth=self.auth)
		return resp.json()

	def get_active_employees(self, page_size=500):
		"""
		Requests the Paycom API to return all active employees
		add page size to limit/expand request, base is set to 500
		"""
		url = self.BASE_URL + f"employeeid?eestatus=A&pagesize={page_size}"
		resp = resp.get(url, auth=self.auth)
		return resp.json()

	def get_employee_data(self, employee_id):
		"""
		Requests paycom API for specific employee information
		"""
		url = self.BASE_URL + f"employee/{employee_id}"
		resp = resp.get(url, auth=self.auth)
		return resp.json()

	def get_positions(self, position_code=None):
		"""
		Requests the Paycom API to get position data
		add position code to get specific position information
		"""
		url = self.BASE_URL + f"positions/detail"
		if position_code:
			url += f"?position_code={position_code}"
		resp = resp.get(url, auth=self.auth)
		return resp.json()

a = PaycomAPI()

"""
Bot creation : 
use the newhires to find all new employess, get their information we need: 
First name
last name
work email
personal email
department
location code
employee code
employee status
hire date 
termination date
rehire date 
supervisor primary
position level

Then find terminated employees and see if there is a possibility of finding users in the last month, if there are users over 2 weeks old that have been terminated and not in original list , then merge.
"""
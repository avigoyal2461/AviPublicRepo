import os
import sys
import pandas as pd
from PyPDF2 import PdfFileReader, PdfFileWriter
import time

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = '\\'.join([LOCAL_PATH, 'Marketo.xlsx'])

sys.path.append(os.environ['autobot_modules'])
from Box.BoxAPI import BoxAPI
from SalesforceAPI import SalesforceAPI

#excel can be uploaded to the same directory as this file and it will be read_excel
class Marketo():
	def __init__(self):
		self.box = BoxAPI(application="Marketo")
		self.sf = SalesforceAPI()
		self.marketo_base_folder_id = "240588577783"


	def main(self):
		"""
		Main method to run the full opportunity
		"""
		df = self.read_excel()
		for opportunity in df['Opportunity Name']:
			print(opportunity)
			opportunity_id = self.get_opportunity_id(opportunity)
			try:
				main_box_folder = self.get_opportunity_box_folder(opportunity_id)
			except Exception as e:
				print(f"Failed to get box folder, {e}")
				print(opportunity)
				continue

			top_file, site_info_documents_folder_id = self.get_genesis_file(main_box_folder)
			if top_file:
				self.upload_file(top_file, site_info_documents_folder_id)
			else:
				print(f"Failed to split top file to folder: {site_info_documents_folder_id}")

	def read_excel(self):
		"""
		Reads Excel file and returns dataframe with opportunities
		"""
		df = pd.read_excel(EXCEL_PATH)

		#cols = ["Opportunity Name", "Billing City", "Primary Finance Partner", "Trinity Salesperson", "Opportunity Owner", "Amount", "System Size, kW-dc", "Price per Watt", "Project Status", "Stage", "Solar Contract Date", "Reason Lost", "Partner", "PPA Rate", "Purchase Method", "Offer $/W"]
		#df.columns = cols

		return df

	def get_opportunity_id(self, name):
		"""
		Gets the opportunity ID from the name in the excel
		"""
		df = self.sf.Select(f"Select Id from Opportunity where name = '{name}'")
		opportunity_id = list(df['Id'])[0]

		return opportunity_id

	def create_box_folder(self, opportunity_id):
		"""
		Creates a box folder in the main marketo folder based on opportunity Id
		"""
		try:
			box_folder_id = self.box.create_folder(f"{opportunity_id}", self.marketo_base_folder_id)
		except Exception as e:
			print(f"failed to create folder, {e}")
			return None

		return box_folder_id

	def upload_file(self, file, box_folder_id):
		"""
		Takes a list of files and uploads them to box based on the box folder id
		"""
		#for file in files:
		self.box.request_upload_file(file, box_folder_id)
		os.remove(file)
		print("Uploaded Files")

	def get_opportunity_box_folder(self, opportunity_id):
		"""
		Gets the main box folder that exists for an opportunity
		"""
		main_box_folder_id = self.sf.get_box_folder_id(opportunity_id)
		
		return main_box_folder_id

	def get_genesis_file(self, main_box_folder_id):
		"""
		Gets the genesis report and splits the document from the main top side view
		"""
		site_info_documents_folder_id = self.box.get_site_info_documents_folder_id(main_box_folder_id)
		response = self.box.request_items_in_folder(site_info_documents_folder_id).json()

		file_id = None
		files = response['entries']
		for file in files:
			if "topview" in file['name'].lower():
				return None, "File already uploaded"
			if "genesis site report.pdf" in file['name'].lower():
				file_id = file['id']

		if not file_id:
			return None, "Could not find File"

		response = self.box.request_download_file(file_id)

		genesis_path = fr"{LOCAL_PATH}\GENESIS SITE REPORT.pdf"
		topside_path = fr"{LOCAL_PATH}\topview.pdf"
		with open(genesis_path, 'wb') as f:
			f.write(response.content)
			f.close()

		pdf = PdfFileReader(genesis_path)
		pdf_writer = PdfFileWriter()

		pdf_writer.addPage(pdf.getPage(0))
		with open(topside_path, 'wb') as out:
			pdf_writer.write(out)

		os.remove(genesis_path)

		file = topside_path
		return file, site_info_documents_folder_id
		
a = Marketo()
a.main()
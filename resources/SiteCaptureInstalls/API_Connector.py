#import all the libraries
#import all the libraries
#Office365-REST-Python-Client
#sharepoint
#office365
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
import os
import sys
import requests
import glob
import time
from zipfile import ZipFile
from PIL import Image
from requests.auth import HTTPBasicAuth
import string
sys.path.append(os.environ['autobot_modules'])
from Sharepoint.connection import SharepointConnection
from SiteCapture.SiteCaptureAPI import SiteCaptureAPI

class API_Connector():
    def __init__(self):
        self.sharepoint = SharepointConnection()
        self.sitecaptureAPI = SiteCaptureAPI(installs=True)
        self.sharepoint.url = 'https://trinitysolarsys.sharepoint.com/sites/PowerAutomate'
        self.sharepoint.relative_url = '/sites/PowerAutomate/Shared%20Documents/'#SE Site Creation Reports/Project_ID.xlsx'
        self.folder = 'SE%20Site%20Creation%20Reports'
        self.file_name = 'Project_ID.xlsx'
        # self.local_excel_path = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\temp\project_id.xlsx"
        self.local_excel_path = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads\temp\project_id.xlsx"
        #`https://us.flow.microsoft.com/manage/environments/Default-f1006ee5-f888-4308-92ea-fcaebe1c0b5e/flows/c79ffe95-526e-4377-bcd5-033f9560be68`
        self.post_to_sharepoint_url = "https://prod-190.westus.logic.azure.com:443/workflows/0249bcde7aaf4db194f5db01f1306d36/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=G8FMDZUvp-WqwkvZihPFLDc-iJC82Gr3bcUsmjsmMNY"
        # os.remove(self.local_excel_path)
        # self.local_report_path = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\tempPics\temp"
        # self.local_pictures_path = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\tempPics\temp.zip"
        # self.extract_file = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\tempPics\temp"

        self.local_report_path = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads\tempPics\temp"
        self.local_pictures_path = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads\tempPics\temp.zip"
        self.extract_file = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads\tempPics\temp"
        
    def connect(self):
        """
        creates a ctx connection with sharepoint
        """
        self.sharepoint.getFile(path=self.local_excel_path, folder=self.folder, file=self.file_name)
        print(f"Successfully Wrote to Excel file... For Details Find.. {self.sharepoint.url}/{self.sharepoint.relative_url}/{self.folder}/{self.file_name}")

    def post(self, project_id):
        """
        Second post - take the project ID and post it back to
        sharepoint excel using sharepoint connection
        """
        #for project_id in project_ids:
        project_id = str(project_id)
        params = {
        "project_id" : project_id
        }
        resp = requests.post(self.post_to_sharepoint_url, json=params)
        time.sleep(3)

    def deleteFile(self, path):
        """
        Deletes a file
        """
        # relative_path = f"{self.relative_url}{Opportunity}/{folder_name}/{file_name}"
        relative_path = path
        while True:
            try:
                ctx_auth = AuthenticationContext(self.url)
                if ctx_auth.acquire_token_for_user(self.username, self.password):
                    ctx = ClientContext(self.url, ctx_auth)
                    target_folder = ctx.web.get_folder_by_server_relative_url(relative_path)
                    break
            except:
                print("retrying Sharepoint connection")
                time.sleep(5)
            try:
                target_folder.delete_object().execute_query()
            except:
                print(f"failed to delete File: {path}")

    def find_pictures(self, project_id):
        """
        Connects to the photos folder on sharepoint using a project id, this project id will have the uploaded pictures ready which are downloaded into a temp zip file
        """
        project_id = str(project_id)
        files = glob.glob(f"{self.local_report_path}\*")
        if len(files) > 0:
            for item in files:
                os.remove(item)
        response = self.sitecaptureAPI.get_project_photos(project_id)
        with open(self.local_pictures_path, 'wb') as output_file:
            output_file.write(response.content)


    def find_report(self, project_id, name):
        """
        Connects to sitecapture and pulls the report from designated page
        """
        # url = f"/sites/PowerAutomate/Shared%20Documents/SE Site Creation Reports/Report_{project_id}.pdf"
        print("setting path")
        # self.local_report_path = r"C:\Users\RPA_Bot_12\Desktop\changes\Downloads\tempPics\temp"
        # self.local_report_path = r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\Downloads\tempPics\temp"
        string.punctuation = string.punctuation.replace(",", "")
        string.punctuation = string.punctuation.replace("-", "")
        name = name.translate(str.maketrans('', '', string.punctuation))
        local_report_path = fr"{self.local_report_path}\Installation Report - {name}.pdf"
        response = self.sitecaptureAPI.get_report(project_id)
        
        with open(local_report_path, 'wb') as output_file:
            output_file.write(response.content)

    def get_pictures_path(self):
        complete_list_directory = []
        print("Waiting 10 seconds...")
        time.sleep(10)
        with ZipFile(self.local_pictures_path, 'r') as zipObj:
            files = zipObj.namelist()
            zipObj.extractall(self.extract_file)
            print(files)

        for counter, file in enumerate(files):
            complete_list_directory.append(fr"{self.extract_file}\{files[counter]}")

        return self.extract_file

if __name__ == "__main__":
    a = API_Connector()
    # a.connect()
    # a.find_pictures(4968542)
    # a.test_pics_path()

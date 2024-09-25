#import all the libraries
#Office365-REST-Python-Client
#sharepoint
#office365
import json, os
import zipfile
# CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
# CONFIG_PATH = '\\'.join([CONFIG_PATH, 'config.json'])
# import config
# with open(CONFIG_PATH) as config_file:
#      config = json.load(config_file)
#      config = config['Sharepoint']

# from config import username, password, url, relative_url
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
import os
import sys
import requests
import glob
from zipfile import ZipFile
from PIL import Image
import time
import shutil
sys.path.append(os.environ['autobot_modules'])
from config import MICROSOFT_USERNAME, MICROSOFT_PASSWORD, SHAREPOINT_BASE_URL, SHAREPOINT_RELATIVE_URL

def Bypass_Header(request):
    """
    Adds a header to the delete Request
    this will bypass any user that may be on the sheet during deletion
    """
    request.headers['Prefer'] = 'bypass-shared-lock'

class SharepointConnection():
    """
    Interactive with the server code found in the same folder, config from config json in same directory
    This code will either pull a file, upload a file, or find a file from the url in config (pointed at shared documents)
    Methods included: 
    -create_folder (creates a folder at a given url)
    -find_folder (finds folder by folder name, **currently base level at shared documents)
    -searchFolder (prints and returns contents from given folder)
    -deleteFile (deletes file at given path(full path to file including the file.pdf etc))
    -uploadFile (uploads a file from required local path, to a given url, folder/file variable) **TBD: or a file thats been read**
    -getFile (downloads a file from sharepoint, takes a full url to the file or a folder/file variable, will take path if given to download file to or create at CWD)
    -unzipFolder (takes a local path to unzip to and a path to zipped folder and returns the files in a folder unzipped)
    """
    
    def __init__(self):
        """
        Inits a connection with sharepoint
        """
        self.username = MICROSOFT_USERNAME
        self.password = MICROSOFT_PASSWORD
        self.url = SHAREPOINT_BASE_URL
        self.relative_url = SHAREPOINT_RELATIVE_URL

        self.folder_list = []
        self.file_list = []
        # self.ctx = self.connect()
        # self.dir = r"C:\test"

    def connect(self):
        """
        creates a ctx connection with sharepoint
        Currently, the ctx object can not be returned and reused so this is a basic method to view if credentials work
        ** will not return False, will attempt to reconnect **
        """
        while True:
            try:
                ctx_auth = AuthenticationContext(self.url)
                if ctx_auth.acquire_token_for_user(self.username, self.password):
                    ctx = ClientContext(self.url, ctx_auth)
                    web = ctx.web
                    # return self.ctx.web

                    ctx = ctx.load(web)
                    ctx = ctx.execute_query()

                    print("Authentication successful")
                    return ctx
            except:
                print("Waiting 10 seconds to retry CTX connection")
                time.sleep(10)
    
    def create_folder(self, folder_name):
        """
        Creates a folder in the original directory (uses self.relative_url)
        This creates a Base Folder with the specific folder_name 
        """
        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            # target_url = ctx
            try:
                ctx = ClientContext(self.url, ctx_auth)
                folder = ctx.web.get_folder_by_server_relative_url(self.relative_url)
                relative_path = f"{self.relative_url}/{folder_name}"
                target_folder = ctx.web.folders.add(relative_path)

                ctx.execute_query()
            except:
                print(f"Failed To Create Folder / Folder Structure for: {folder_name}")
                return None
        return True
        # self.create_file_structure(relative_path)

    def find_folder(self, folder_name):
        """
        Uses the connection and folder ID / builds a relative url to find specific folders
        returns false if cannot find folder
        """
        relative_path = f"{self.relative_url}/{folder_name}"
        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            # print("something")
            try:
                ctx = ClientContext(self.url, ctx_auth)
                folder = ctx.web.get_folder_by_server_relative_url(self.relative_url)
                sub_folders = folder.folders
                ctx.load(sub_folders)

                ctx.execute_query()

                for s_folder in sub_folders:
                    self.folder_list.append(s_folder.properties["Name"])
                    # print(s_folder.properties["Name"]) #returns the folders in the folder
                    
                for folder in self.folder_list:
                    if folder.lower() == folder_name.lower():
                        print(f"Found folder: {folder_name}")
                        return True
                        # try:
                        #     # self.create_file_structure(relative_path)
                        #     print("File Structure is set...")
                        #     return True
                        # except:
                        #     print("File Structure already created.")
                        #     return True

                #if folder is not found and not caught, make it
                # self.make_folder(folder_name)

            except:
                print(f"Failed to search for / find Folder: {folder_name}")
                return False
                # print(f"Failed to search for / find Folder: {folder_name}, Creating folder...")
                # self.make_folder(folder_name)

        return False

    def searchFolder(self, url=None, folder_name=None):
        """
        Requires either a folder name or a URL, will create based off of the relative URL (if relative URL is different please set self.relative_url)
        """
        if url:
            relative_path = f"{self.relative_url}{url}"
        else:
            relative_path = f"{self.relative_url}{folder_name}"

        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            try:
                ctx = ClientContext(self.url, ctx_auth)
                folder = ctx.web.get_folder_by_server_relative_url(relative_path)

                sub_folders = folder.files
                ctx.load(sub_folders)
                ctx.execute_query()
                print(sub_folders)
                # print(sub_folders)
                for s_file in sub_folders:
                    self.file_list.append(s_file.properties["Name"])
                    # print("FOUND Folder")
                    print(s_file.properties["Name"]) #returns the folders in the folder, Project_ID.xlsx is printed
                if len(self.file_list) > 0:
                    return self.file_list
                else:
                    if url:
                        print(f"No Files found under url: {url}")
                    else:
                        print(f"No Files found under url: {folder_name}")
                    # print(f"No Files found under folder: {folder_name} for Opportunity - {Opportunity}...")
                    return None
                # return True
            except:
                if url:
                    print(f"No Files found under url: {url}")
                else:
                        print(f"No Files found under url: {folder_name}")
                return None
        else:
            print("Failed to connect to Sharepoint...")
            return None

    # def searchFolder(self, Opportunity, folder_name): #DEPRECATED
    #     """
    #     Uses the connection and folder ID / builds a relative url to find all files inside of the specific folder (RELATED TO THE RELATIVE URL)
    #     """
    #     ctx_auth = AuthenticationContext(self.url)
    #     if ctx_auth.acquire_token_for_user(self.username, self.password):
    #         try:
    #             ctx = ClientContext(self.url, ctx_auth)
    #             folder = ctx.web.get_folder_by_server_relative_url(f"{self.relative_url}{Opportunity}/{folder_name}")

    #             sub_folders = folder.files
    #             ctx.load(sub_folders)
    #             ctx.execute_query()
    #             print(sub_folders)
    #             # print(sub_folders)
    #             for s_file in sub_folders:
    #                 self.file_list.append(s_file.properties["Name"])
    #                 # print("FOUND Folder")
    #                 print(s_file.properties["Name"]) #returns the folders in the folder, Project_ID.xlsx is printed
    #             if len(self.file_list) > 0:
    #                 return self.file_list
    #             else:
    #                 print(f"No Files found under folder: {folder_name} for Opportunity - {Opportunity}...")
    #                 return None
    #             # return True
    #         except:
    #             print(f"Failed to Find Files For {Opportunity}")
    #             return None
    #     else:
    #         print("Failed to connect to Sharepoint...")
    #         return None
    
    def deleteFile(self, path):
        """
        Deletes a file from a given path (PATH NEEDS TO POINT AT THE FILE)
        """
        relative_path = f"{self.relative_url}{path}"
        
        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            ctx = ClientContext(self.url, ctx_auth)
            target_folder = ctx.web.get_folder_by_server_relative_url(relative_path)
            ctx.before_execute(Bypass_Header)
            try:
                target_folder.delete_object().execute_query()
            except Exception as e:
                print(e)
                print(f"failed to delete File: {path}")
                return False
        return True

    def uploadFile(self, path, file, folder=None, url=None):
        """
        Uploads a given file from a required path
        file will be the name of the file we want to upload / overwrite, FILE IS REQUIRED
        **currently not parsing the path**
        url will be the primary option which is linked to the relative url (NEEDS THE FILE IN THIS VARIABLE), folder and file not needed if given
        folder will be the folder we want to publish this file to (NEEDS FILE TO BE GIVEN)
        """
        if url:
            if not file:
                relative_path = f"{self.relative_url}{url}"

        elif folder:
            if file:
                relative_path = f"{self.relative_url}{folder}"
            else:
                return "Bad Request, Please include: url=url or file=file_name"

        relative_path = f"{self.relative_url}{folder}"
        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            print("Authenticated")
            ctx = ClientContext(self.url, ctx_auth)
            target_folder = ctx.web.get_folder_by_server_relative_url(relative_path)
            try:
                with open(path, 'rb') as content_file:
                    content_file = content_file.read()
                    target_folder.upload_file(file, content_file).execute_query()

            except Exception as e:
                print(e)
                print("Failed to upload file")
                return False
        return True

    def makeDirectoryFile(self, path):
        """
        Takes a given path and creates a file directory
        """
        try:
            path = os.path.join(path)
            # os.mknod(path)
            file = open(path, 'w')
            file.close()
            return path
        except:
            print("Failed to create Directory to write to..")
            # quit()
            pass

    def getFile(self, path, folder=None, file=None, url=None):
        """
        Takes a path which marks where we want to download file - REQUIRED
        Takes a folder which is the folder connected to the shared documents folder: ex - conga OR conga/opportunity
        Takes a file which is either linked to the shared document folder OR the folder given from above
        Takes a url which ignores all fields and builds from the shared document folder
        """
        #loads authentication and gets file
        ctx_auth = AuthenticationContext(self.url)
        print(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            ctx = ClientContext(self.url, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            # print("?")

        if url:
            #check incase url and file were given and url does not contain file
            if file:
                file_url = f"{self.relative_url}{url}/{file}"
            else:
                file_url = f"{self.relative_url}{url}"
        elif folder:
            if file:
                file_url = f"{self.relative_url}{folder}/{file}"
            else:
                file_url = f"{self.relative_url}{folder}"

        self.makeDirectoryFile(path)
        print(file_url)
        #makes the call to open and write to file
        response = File.open_binary(ctx, file_url)
        try:
            with open(path, 'wb') as output_file:
                if file:
                    print(f"Writing information for {file}")
                else:
                    print(f"Writing information for {path}")
                output_file.write(response.content)

        except:
            print("Failed to write files...")
            return None

        return path

    def getFolderItems(self, path, folder=None):
        """
        Takes a path which marks where we want to download file - REQUIRED
        Takes a folder which is the folder connected to the shared documents folder: ex - conga OR conga/opportunity
        """
        # loads authentication and gets file
        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            ctx = ClientContext(self.url, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            # print("?")
        print("Searching Folder")
        if folder:
            folder = ctx.web.get_folder_by_server_relative_url(folder)
            files = folder.files
            ctx.load(files)
            ctx.execute_query()

            for file in files:
                file_name = file.properties["Name"]
                file_path = path + file_name
                try:
                    with open(file_path, 'wb') as local_file:
                        content_response = File.open_binary(ctx, file.serverRelativeUrl)
                        content = content_response.content
                        local_file.write(content)
                except Exception as e:
                    print(e)
                    print("Failed to write files...")
                    return None
        else:
            print("Share point folder not specified...")
            return None
        return True

    def unzipFolder(self, zipFolderPath, localFolderPath):
        """
        Unzips a folder from a given path and sends it to the given local path
        """
        complete_list_directory = []
        with ZipFile(zipFolderPath, 'r') as zipObj:
            files = zipObj.namelist()
            zipObj.extractall(localFolderPath)
            print(files)
        # self.makeDirectoryFolder(fr"{}")
        for counter, file in enumerate(files):
            complete_list_directory.append(fr"{localFolderPath}\{files[counter]}")
        # return complete_list_directory
        return localFolderPath

if __name__ == "__main__":
    sharepoint = SharepointConnection()
    import os
    cwd = os.getcwd()
    document_folder_path = fr"{cwd}/"
    folder_in_sharepoint = '/teams/BTIntranet/Shared Documents/Spotio/'
    print(document_folder_path)

    sharepoint.url = "https://trinitysolarsys.sharepoint.com/teams/BTIntranet"
    sharepoint.relative_url = "/teams/BTIntranet/Shared%20Documents/"
    sharepoint.getFolderItems(path=document_folder_path, folder=folder_in_sharepoint)
    #a.getFile(path=r"C:\Users\AviGoyal\Desktop\Invoice.pdf", url=r"SunnovaInvoices/Trueup/Invoice.pdf")

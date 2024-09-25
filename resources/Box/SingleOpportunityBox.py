import json
import time
import os
import sys
from flask_restful import Resource
from resources.Box.BoxAPI import BoxAPI
from api.box.BoxCallValidate import BoxValidate
# from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc
# from resources.Box.CacheCheck import CacheCheck
from cachetools import TTLCache
from datetime import datetime, timedelta
sys.path.append(os.environ['autobot_modules'])
from Token import token_required

CACHE_DATA = TTLCache(maxsize=50000, ttl=timedelta(hours=3), timer=datetime.now)

@doc(description='Getting all filenames along with its folder names and path details for a parent BoxFolderId of an Opportunity. \
                  This only works for Parent BoxFolderId of an Opportunity', tags=['Single Opportunity Box'])


class SingleOpportunityBox(MethodResource, Resource):  
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @marshal_with(None, code=400, description='A client error occurred when handling the request. \n \
                                               Error: Client did not provide the right parameters or did not have access to the resources, or tried to perform an action that is otherwise not possible.',
                                               apply=False)
    @token_required
    def get(self, box_folder_id=None, app="OneButton"):
        global opportunity_id, opportunity_name, BoxFileDetails, BoxFolderJson, folder_path
        self.box_api = BoxAPI(access_token=None, application=app)
        BoxFileDetails = {} 
        BoxFolderJson = []
        retry_counter = 0
        res = None
        # checker = CacheCheck(box_folder_id)
        # BoxFolderJson = checker.check()
        BoxFolderJson = CACHE_DATA.get(hash(box_folder_id), None)

        if BoxFolderJson or BoxFolderJson != None:
            # checker.write(BoxFolderJson)

            return BoxFolderJson
        BoxFolderJson = []
        while True:
            try:
                BoxValidate(f'Box Request Folder info {box_folder_id} - Single Opportunity details Box fetch')
                res = self.box_api.request_folder_info(box_folder_id)
                break
            except:
                retry_counter += 1
                if retry_counter == 6:
                    if not res:
                        # res = None
                        return 'Box API Issue'
                    break
                time.sleep(1)  
        if res == None:
            return 'Check entered Opportunity Box Folder Id'   
  
        response = res.json()
        opportunity_id = box_folder_id 
        opportunity_name = response['name']           
        item_collection = response['item_collection']
        entries = item_collection['entries'] 
        main_folders_name = []               
        main_folders_id = []
        
        for i in range(len(entries)): 
            main_folders_name.append(entries[i]['name'])               
            main_folders_id.append(entries[i]['id'])

        for i, id in enumerate (main_folders_id):
            folder_path = opportunity_id + f'/{opportunity_name}' + f'/{main_folders_name[i]}'            
            status = self.fetch_sub_folders_files(id)
            if status == 'None':
                # BoxFolderJson = checker.check()
                # BoxFolderJson = CACHE_DATA.get(hash(box_folder_id), None)

                if not BoxFolderJson or BoxFolderJson == "None":
                    return 'Please enter Opportunity Box Folder Id'     
                else:
                    break       
            
                
        BoxFileDetails['BoxFileDetails'] = BoxFolderJson
        # checker.write(BoxFolderJson)
        CACHE_DATA[hash(box_folder_id)] = BoxFileDetails

        return BoxFileDetails    

    def fetch_sub_folders_files(self,id): 
        global folder_path       
        file_path = 'https://trinity-solar.app.box.com/file/'
        BoxValidate(f'Box Request Folder info {id} - Single Opportunity details Box fetch')
        retry_counter = 0
        while True:
            try:
                res = self.box_api.request_folder_info(id)
                break
            except:
                retry_counter += 1
                if retry_counter == 6:
                    res = None
                    break
                time.sleep(1)
        if res != None:
            tempJson = {}
            response = res.json()            
            sub_folder_name = (response['name']).replace(',','')
            sub_folder_id  = response['id']            
            item_collection = response['item_collection']
            entries = item_collection['entries']
            
            for i in range(len(entries)):
                
                if entries[i]['type'] == 'file':
                    file_name = (entries[i]['name'])
                    folder_path += f'/{file_name}'
                    file_id = entries[i]['id']
                    tempJson = {'opportunity_id' : opportunity_id,
                                'folder_name' : sub_folder_name,
                                'folder_id' : sub_folder_id,
                                'file_name' : file_name,
                                'file_id' : file_id,
                                'file_path' : file_path + file_id,
                                'folder_path' : folder_path}
                    BoxFolderJson.append(tempJson)      
                    folder_path = folder_path.replace(f'/{file_name}','')
                if entries[i]['type'] == 'folder':  
                    folder = entries[i]['name']  
                    folder_path += f'/{folder}'        
                    self.fetch_sub_folders_files(entries[i]['id'])
                    folder_path = folder_path.replace(f'/{folder}','')
            return
        else:
            return 'None'

from flask_restful import Resource
from api.box import BoxAppValidation
# from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
import json
import sys
import os
sys.path.append(os.environ['autobot_modules'])
from Token import token_required
# from BotUpdate.ProcessTable import RPA_Process_Table

@doc(description='Gets the contents of a Box folder for an opportunity with a given Get.', tags=['Box Folder Contents'])
class BoxFolderItems(MethodResource, Resource):
    """
    Gets the contents of a box folder.
    """
    @token_required
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @marshal_with(None, code=404, description='Error: Client entered BoxFolderId is invalid', apply=False)
    @marshal_with(None, code=405, description='Error: Client did not provide the right parameters', apply=False)
    def get(self, folder_id=None, app="OneButton"):
        box_api = BoxAppValidation(app).box_api
        res = box_api.request_items_in_folder(folder_id)
        return res.json(), res.status_code

@doc(description='Gets the contents of a parent Box folder inside an opportunity \
                  w.r.t the given OpportunityId and Folder name.', tags=['Parent Box Folder Contents'])
class BoxOpportunityFolderItems(MethodResource, Resource):
    """
    Gets the contents of a box folder inside an opportunity.
    """
    @token_required
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @marshal_with(None, code=400, description='A client error occurred when handling the request. \n \
                                               Error: Client did not provide the right parameters or did not have access to the resources, or tried to perform an action that is otherwise not possible.',
                                               apply=False)
    def get(self, opportunity_id=None, folder_name=None, app="OneButton"):
        box_api = BoxAppValidation(app).box_api
        parent_folder_id = box_api.get_box_folder_id(opportunity_id)
        if not parent_folder_id:
            return {'status': 'opportunity not found'}, 404
        folder_id = box_api.get_folder_id_from_parent(parent_folder_id, folder_name)
        if not folder_id:
            return {'status': 'folder not found'}, 404
        res = box_api.request_items_in_folder(folder_id)
        return res.json(), res.status_code

@doc(description='Getting the Box sharedLink, downloadLink and embedlinks for a given Box file/folder Id.\
                  Box type has to be mentioned whether a file or folder', tags=['Box Links'])
class BoxOpportunitySharedLink(MethodResource, Resource):
    """
    Gets the shareLink for the given BoxId.
    """
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @token_required
    def get(self, box_id=None, box_type=None, user=None, app="OneButton"): 
        # bot_update = RPA_Process_Table()
        # name = "Box_Shared_Link"
        # bot_update.register_bot(name)

        box_api = BoxAppValidation(app).box_api
        if box_type == 'folder':
            response = box_api.request_for_folder_sharedLink(box_id)
        elif box_type == 'file':
            response = box_api.request_for_file_sharedLink(box_id)

        if response.status_code == 200:
            link = response.json()
            shared_link = link['shared_link']
            if not shared_link or shared_link == "None":
                # bot_update.update_bot_status(name, "Creating Link", box_id)
                if box_type == "folder":
                    box_api.create_sharedLink_for_folder(box_id)
                    response = box_api.request_for_folder_sharedLink(box_id)
                else:
                    box_api.create_sharedLink_for_file(box_id)
                    response = box_api.request_for_file_sharedLink(box_id)

                link = response.json()
                shared_link = link['shared_link']

                if not shared_link or shared_link == "None":
                    return link, response.status_code
                    # bot_update.complete_opportunity(name, box_id)
            
            # bot_update.edit_end()

            res = box_api.add_collaborator(user, box_id, box_type)

            shared_link = link['shared_link']['url']
            download_link = link['shared_link']['download_url']
            replaceStr = "https://trinity-solar.box.com/"
            embed1 = "https://trinity-solar.app.box.com/embed/"
            embed2 = shared_link.replace(replaceStr,'')
            embed3 = "?sortColumn=date&view=list" 
            embed_link = embed1 + embed2 + embed3
            # resp_header = dict(response.headers)
            # resp_header['X-Frame-Options'] = 'SAMEORIGIN'
            # resp = make_response({'shared_link': shared_link,
            #         'download_link': download_link,
            #         'embed_link' : embed_link})
            # resp.headers=['X-Frame-Options: SAMEORIGIN']

            # return resp
            return {'shared_link': shared_link,
                    'download_link': download_link,
                    'embed_link' : embed_link,
                    }, 200, {'X-Frame-Options': 'SAMEORIGIN'}         
        else:
            return response.status_code

@doc(description='Getting Contract Folder ID from Parent ID')
class GetBoxContractFolderId(MethodResource, Resource):
    """
    Gets Folder ID From Parent by given folder
    """
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @marshal_with(None, code=400, description='A client error occurred when handling the request. \n \
                                               Error: Client did not provide the right parameters or did not have access to the resources, or tried to perform an action that is otherwise not possible.',
                                               apply=False)
    @token_required
    def get(self, app="OneButton", parent_folder_id=None):
        # print(parent_folder_id)
        box_api = BoxAppValidation(app).box_api
        response = box_api.get_contract_documents_folder_id(parent_folder_id)

        # id = response.json()
        return {
            'folderID': response
        }

@doc(description='Getting Contract Folder ID from Parent ID')
class GetBoxApplicationFolderId(MethodResource, Resource):
    """
    Gets Folder ID From Parent by given folder
    """
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @marshal_with(None, code=400, description='A client error occurred when handling the request. \n \
                                               Error: Client did not provide the right parameters or did not have access to the resources, or tried to perform an action that is otherwise not possible.',
                                               apply=False)
    @token_required
    def get(self, app="OneButton", opportunity_id=None):
        # print(parent_folder_id)
        box_api = BoxAppValidation(app).box_api
        parent_folder_id = box_api.get_box_folder_id(opportunity_id)
        response = box_api.get_applications_folder_id(parent_folder_id)

        # id = response.json()
        return {
            'folderID': response
        }


@doc(description='Getting Base Folder ID from Opportunity ID')
class GetBoxBaseFolder(MethodResource, Resource):
    """
    Gets the Base Folder ID from the given opportunity Id
    """
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @marshal_with(None, code=400, description='A client error occurred when handling the request. \n \
                                               Error: Client did not provide the right parameters or did not have access to the resources, or tried to perform an action that is otherwise not possible.',
                                               apply=False)
    @token_required
    def get(self, app="OneButton", opportunity_id=None):
        if not opportunity_id:
            return None

        box_api = BoxAppValidation(app).box_api
        folder_id = box_api.get_box_folder_id(opportunity_id)
        return {
            'folderID': folder_id
        }
        

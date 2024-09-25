import time

from flask import request, render_template, make_response
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
import os
import sys
from resources.customlogging import logger
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from api.box import BoxAppValidation
from PIL import Image
from io import BytesIO

TEMP_DOWNLOADS_FOLDER = os.path.join(os.getcwd(), 'temp')
sys.path.append(os.environ['autobot_modules'])
from Token import token_required


# @doc(description='Getting complete file details for a given Opportunity BoxFolderId.', tags=['Single Box Opportunity Files'])
# @use_kwargs({'parent_id': fields.Str(required=True, description='Uploaded'),
#              'salesforce_id': fields.Str(required=True, description='Uploaded'),
#              'folder_name': fields.Str(required=True, description='Uploaded'),
#              'key': fields.Str(required=True, description='Uploaded')})
class BoxFile(Resource):
    @token_required
    def post(self):
        """Creates a file in a folder. If given a folder id, will upload directly to that.
        Otherwise will search for a folder in the opportunity with the given name."""
        try:
            app = request.args['app']
        except:
            app = "OneButton"
        image_file = request.files['file']
        file_name = image_file.filename
        # parent_id = request.args['parent_id']
        parent_id = None
        salesforce_id = request.args['salesforce_id']
        folder_name = request.args['folder_name']
        try:
            box_api = BoxAppValidation(app).box_api
        except:
            return {"Failed to connect to BoxAPI", 502}

        if parent_id:
            logger.info(f'Received request for box file upload: {file_name} to parent: {parent_id}')
        else:
            logger.info(f'Received request for box file upload: {file_name} to folder name: {folder_name}')
            dl_folder_id = box_api.get_box_folder_id(salesforce_id)  # gets the main folder of an opportunity id
            if not dl_folder_id:
                return {'status': 'Unable to locate box folder from given id.'}, 403
            parent_id = box_api.get_folder_id_from_parent(dl_folder_id, folder_name)
            if not parent_id:
                box_api.create_box_folder_structure(dl_folder_id)
                parent_id = box_api.get_folder_id_from_parent(dl_folder_id, folder_name)
                if not parent_id:
                    return {'status': 'Unable to find specified folder.'}, 403
            logger.info(f'Found folder id: {parent_id}')
        file_location = os.path.join(TEMP_DOWNLOADS_FOLDER, file_name)
        image_file.save(file_location)
        response = box_api.request_upload_file(file_location, parent_id)
        if response.status_code == 409:
            file_id = response.json()['context_info']['conflicts']['id']
            logger.info('Uploading new file version...')
            response = box_api.request_upload_new_file_version(file_id, file_location, parent_id)
            logger.info(response.status_code)
            logger.info(response.text)
        os.remove(file_location)
        return response.json()

class BoxFilePreFlight(Resource):
    @token_required
    def post(self):
        """Test that the supplied information is correct before uploading a file to box."""
        parser = reqparse.RequestParser()
        parser.add_argument('parent_id', required=True, type=str)
        parser.add_argument('key', required=False, type=str)
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        file_name = request.files['file'].filename
        image_file = args['file']
        parent_id = args['parent_id']
        if image_file:
            logger.info(f'Received request for box file upload: {file_name} to parent: {parent_id}')
            return {'file_name': file_name, 'parent_id': args['parent_id'], 'file_content_status': 'OK'}
        else:
            return {'status': 'Invalid Arguments'}


@doc(description='Gets the file information from Box w.r.t the filename doing a file search. \
    \n Give the file along with its extension like pdf, txt etc.', tags=['Box File Search'])
class BoxSearchFile(MethodResource, Resource):
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @token_required
    def get(self, file_name=None, app="OneButton"):
        box_api = BoxAppValidation(app).box_api
        file_splits = file_name.split('.')
        file_name = file_splits[0]
        file_extension = file_splits[1]
        response = box_api.request_search_file(file_name, file_extension)
        if response.status_code == 200 and response.json()['total_count'] != 0:
            try:
                file_type = response.json()['entries'][0]['type']
                file_name = response.json()['entries'][0]['name']
                file_id = response.json()['entries'][0]['id']
                response = box_api.request_for_file_sharedLink(file_id)
                links = response.json()
                fileJson = {'type': file_type,
                            'fileName': file_name,
                            'fileId': file_id,
                            'sharedLink': links['shared_link']['url'],
                            'downloadLink': links['shared_link']['download_url']}
                return fileJson
            except Exception as error:
                return error
        elif response.status_code == 200 and response.json()['total_count'] == 0:
            return 'status: Box filename invalid'
        else:
            return response.json()


@doc(description='Gets the Image from Box w.r.t the filename doing a file search and displays it along with its filename. \
    \n Give the file along with its extension, either jpg or png', tags=['Box Get Image'])
class BoxImageFile(MethodResource, Resource):
    @marshal_with(None, code=200, description='Box request completed successfully', apply=False)
    @token_required
    def get(self, file_name=None, app="OneButton"):
        box_api = BoxAppValidation(app).box_api
        try:
            name, extension = file_name.split('.')
            response = box_api.request_search_file(
                name, extension)
            if extension != 'jpg' and 'png':
                return 'status : Enter Box image-filename'

            if response.status_code == 200 and response.json()['total_count'] != 0:
                file_name = response.json()['entries'][0]['name']
                file_id = response.json()['entries'][0]['id']
                response = box_api.request_download_file(file_id)
                image = Image.open(BytesIO(response.content))
                image.save(f'static/{file_name}', quality=95)
                return make_response(render_template('BoxImage.html', imagefile=file_name))
            else:
                return 'status : Box filename invalid'
        except Exception as error:
            return error


class BoxFileByFolderID(Resource):
    @token_required
    def post(self):
        """Creates a file in a folder for a given folder ID."""
        try:
            app = request.args['app']
        except:
            app = "OneButton"
        image_file = request.files['file']
        file_name = image_file.filename
        parent_id = request.args['parent_id']

        try:
            box_api = BoxAppValidation(app).box_api
        except:
            return {"Failed to connect to BoxAPI", 502}

        if parent_id:
            logger.info(f'Received request for box file upload: {file_name} to parent: {parent_id}')
        else:
            return {'status': 'Unable to find specified folder.'}, 403
        file_location = os.path.join(TEMP_DOWNLOADS_FOLDER, file_name)
        image_file.save(file_location)
        response = box_api.request_upload_file(file_location, parent_id)
        if response.status_code == 409:
            file_id = response.json()['context_info']['conflicts']['id']
            logger.info('Uploading new file version...')
            response = box_api.request_upload_new_file_version(file_id, file_location, parent_id)
            logger.info(response.status_code)
            logger.info(response.text)
        os.remove(file_location)
        return response.json()
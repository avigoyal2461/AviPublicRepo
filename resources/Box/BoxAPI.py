# Resource Folder Import
import os
import sys

sys.path.append(os.environ["autobot_modules"])

# Imports
import json
import time
import datetime
import secrets
import jwt
import requests
from typing import Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from Box.box_config import BOX_FOLDER_ID_URL, OPP_FOLDER_ID_URL
from customlogging import logger
from SalesforceAPI import SalesforceAPI

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# from api.box.BoxCallValidate import BoxValidate

session = requests.Session()
retry = Retry(total=5, connect=5, backoff_factor=5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)
AUTH_URL = r"https://api.box.com/oauth2/token"
BASE_URL = r"https://api.box.com/2.0"
# POWERAUTOMATETEAM_USER_ID = '16769271298'
RPA_USER_ID = "16769271298"
TIME_DELAY = 45

def get_access_token(application=None) -> tuple:
    """Requests an access token and expiry date."""
    logger.info("Requesting JWT Token for Box API...")
    try:
        with open(r"./resources/Box/kevin_box_jwt.json") as json_file:
            config = json.load(json_file)
    except:
        try:
            with open(r"./Box/kevin_box_jwt.json") as json_file:
                config = json.load(json_file)
        except:
            CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
            CONFIG_PATH = "\\".join([CONFIG_PATH, "kevin_box_jwt.json"])
            with open(CONFIG_PATH) as json_file:
                config = json.load(json_file)

    if application:
        config_setting = application
    else:
        config_setting = "default_BoxAppSettings"

    appAuth = config[config_setting]["appAuth"]
    privateKey = appAuth["privateKey"]
    passphrase = appAuth["passphrase"]
    key = load_pem_private_key(
        data=privateKey.encode("utf8"),
        password=passphrase.encode("utf8"),
        backend=default_backend(),
    )
    claims = {
        "iss": config[config_setting]["clientID"],
        "sub": config["enterpriseID"],  # TODO: Check function as user
        # 'sub': RPA_USER_ID,
        "box_sub_type": "enterprise",
        "aud": AUTH_URL,
        "jti": secrets.token_hex(64),
        "exp": round(time.time() + TIME_DELAY),
    }
    # JWT Assertion
    keyId = config[config_setting]["appAuth"]["publicKeyID"]
    assertion = jwt.encode(claims, key, algorithm="RS512", headers={"kid": keyId})

    params = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
        "client_id": config[config_setting]["clientID"],
        "client_secret": config[config_setting]["clientSecret"],
    }
    init_datetime = datetime.datetime.now()
    print("Getting Access Token")
    logger.info("Getting Access Token")
    response = session.post(AUTH_URL, params, timeout=240)

    RETRY_COUNTER = 0
    """
    while True:
        try:
            print("Getting Access Token")
            response = requests.post(AUTH_URL, params)
            if response:
                break
            else:
                RETRY_COUNTER += 1

            if RETRY_COUNTER == 5:
                break
        except:
            RETRY_COUNTER += 1
            if RETRY_COUNTER == 5:
                logger.info("Retried 5 times, exiting")
                return None
            logger.info("Retrying Access token creation...")
            time.sleep(1)
    """
    data = response.json()
    logger.info("JWT Token Received")
    access_token = data["access_token"]
    expired_in = data["expires_in"]
    expiry_time = init_datetime + datetime.timedelta(0, expired_in)
    return access_token, expiry_time


class BoxAPI:
    """A wrapper for the box API. All direct api call functions begin with 'request' and return a response."""

    def __init__(self, access_token=None, application=None):
        if not access_token:
            self.access_token, self.access_token_expiry_date = get_access_token(
                application=application
            )
        self.application = application
        self.salesforce_api = SalesforceAPI()

    def get_access_token(self):
        """Returns non-expired access token."""
        if not self.access_token:
            self.access_token, self.access_token_expiry_date = get_access_token(application=self.application)

        if datetime.datetime.now() > self.access_token_expiry_date:
            self.access_token, self.access_token_expiry_date = get_access_token(application=self.application)

        return self.access_token

    def get_user(self, user):
        """
        Gets user based on search term, this search term will search box api for the
        most related user, this can be an Id, name, email
        Return: ID.
        """
        url = f"{BASE_URL}/users?filter_term={user}"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "as-user": RPA_USER_ID,
        }

        response = session.get(url, headers=headers, timeout=120)
        try:
            res = response.json()['entries'][0]
            return res['id']
        except Exception as e:
            print(f"Encountered exception, {e}")
            return None

    def add_collaborator(self, user, box_id, item_type="folder"):
        """
        Adds a collaborator to a folder id based on user and box id (file or folder id)
        User may be an ID or an email address
        Type may be either folder or file
        """
        item_type = item_type.lower()
        url = f"{BASE_URL}/collaborations?notify=False"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "as-user": RPA_USER_ID,
        }
        data = {
               "item": {
                 "type": f"{item_type}",
                 "id": box_id
               },
               "accessible_by": {
                 "type": "user",
                 "login": f"{user}"
               },
               "role": "editor"
             }
        res = session.post(url, json=data, headers=headers, timeout=120)
        return res

    def create_box_folder_structure(self, box_opportunity_folder_id):
        EXPECTED_FOLDERS = [
            "Site Info-Designs",
            "Sales Documents",
            "Miscellaneous Documentation",
            "Job Photos",
            "Installation Documents",
            "Contract Documents",
            "Archive",
            "Applications",
            "Accounting",
        ]
        existing_folders = []
        logger.info("Checking box folder structure")
        items_res = self.request_items_in_folder(box_opportunity_folder_id)
        if items_res:
            items = items_res.json()["entries"]
            for item in items:
                existing_folders.append(item["name"])

        for folder in EXPECTED_FOLDERS:
            if folder not in existing_folders:
                logger.info(f"Could not find {folder}, creating folder...")
                self.create_folder(folder, box_opportunity_folder_id)

    def get_dl_folder_id(self, direct_lead_id):
        """Gets the box folder id for a given direct lead id."""
        content = {"direct_lead_id": direct_lead_id}
        response = requests.post(BOX_FOLDER_ID_URL, json=content, timeout=120)
        data = response.json()
        try:
            return data["folder_id"]
        except:
            return None

    def get_box_folder_id(self, salesforce_id):
        """Gets the box folder id for a given salesforce id."""
        #content = {"salesforce_id": salesforce_id}
        #response = requests.post(BOX_FOLDER_ID_URL, json=content, timeout=120)
        #data = response.json()
        #try:
        #    return data["folder_id"]
        #except:
        #    return None
        folder_id = self.salesforce_api.get_box_folder_id(salesforce_id)
        return folder_id

    def get_opp_folder_id(self, opp_id):
        """Gets the box folder id for a given direct lead id."""
        #content = {"opp_id": opp_id}
        #response = requests.post(OPP_FOLDER_ID_URL, json=content, timeout=120)
        #data = response.json()
        #try:
        #    return data["folder_id"]
        #except:
        #    return None
        return self.get_box_folder_id(opp_id)

    def request_upload_folder(self, src_folder_path, dst_folder_id):
        pass

    def request_upload_file(self, src_file_path, dst_folder_id, suffix=""):
        url = r"https://upload.box.com/api/2.0/files/content"
        doc_name_split = os.path.basename(src_file_path).split(".")
        base_name = ".".join(doc_name_split[:-1])
        doc_name = f"{base_name}{suffix}.{doc_name_split[-1]}"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "as-user": RPA_USER_ID,
        }
        attributes = '{"parent":{"id":' + dst_folder_id + '},"name":"' + doc_name + '"}'
        data = {"attributes": attributes}

        # files = {"file": open(src_file_path, "rb")}
        # response = session.post(url, data=data, files=files, headers=headers, timeout=120)

        with open(src_file_path, "rb") as file:
            files = {"file": file}
            response = session.post(
                url, data=data, files=files, headers=headers, timeout=120
            )

        # response = requests.post(url, data=data, files=files, headers=headers)
        logger.info(f"Upload Response:{response}")
        return response

    def request_upload_new_file_version(self, file_id, src_file_path, dst_folder_id):
        url = f"https://upload.box.com/api/2.0/files/{file_id}/content"
        # url = r"https://httpbin.org/anything"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "as-user": RPA_USER_ID,
        }
        doc_name = src_file_path.split("\\")[-1]
        print("Attempting to upload document")
        attributes = '{"parent":{"id":' + dst_folder_id + '},"name":"' + doc_name + '"}'
        data = {"attributes": attributes}
        # files = {"file": open(src_file_path, "rb")}
        # response = session.post(
        #     url, data=data, files=files, headers=headers, timeout=120
        # )
        with open(src_file_path, "rb") as file:
            files = {"file": file}
            response = session.post(
                url, data=data, files=files, headers=headers, timeout=120
            )

        # response = requests.post(url, data=data, files=files, headers=headers)
        logger.info(f"Update Response:{response}")
        return response

    def request_upload_file_preflight_check(
        self, src_file_path, dst_folder_id, suffix=""
    ):
        url = f"{BASE_URL}/files/content"
        doc_name = os.path.basename(src_file_path).split(".")[0] + suffix
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        data = {"name": doc_name, "parent": {"id": dst_folder_id}}
        # logger.info(f'Testing upload of {doc_name} to folder {dst_folder_id}')
        response = requests.options(url, headers=headers, json=data, timeout=120)
        if response.status_code == 200:
            return response
        else:
            logger.info(response.text)
            return None

    def request_folder_info(self, folder_id):
        url = BASE_URL + r"/folders/" + folder_id
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        # logger.info(f'Making request to {url}')
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200:
            return response
        else:
            logger.info(response.text)
            return None

    def request_items_in_folder(self, folder_id):
        try:
            url = f"{BASE_URL}/folders/{folder_id}/items"
            headers = {
                "Authorization": f"Bearer {self.get_access_token()}",
                "Content-Type": "application/json",
                "as-user": RPA_USER_ID,
            }
            logger.info(f"Making request")
            return requests.get(url, headers=headers, timeout=120)
        except:
            return None

    def request_create_folder(self, folder_name, parent_folder_id):
        url = BASE_URL + "/folders/"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        data = {"name": folder_name, "parent": {"id": parent_folder_id}}
        response = session.post(url, headers=headers, json=data, timeout=120)
        if response.status_code == 200 or response.status_code == 201:
            return response
        # elif response.status_code == 409:
        #     folder_id = self.get_folder_id_from_parent(parent_folder_id, folder_name)
        #     return folder_id
        else:
            logger.info(response)
            return None

    def request_download_file(self, file_id) -> Union[object, bool]:
        url = BASE_URL + f"/files/{file_id}/content/"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        logger.info(f"Making request")
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200:
            return response
        else:
            logger.info("box download end point returned error")
            logger.error(response.text)
            return None

    def create_folder(self, folder_name, parent_folder_id):
        status = self.request_create_folder(folder_name, parent_folder_id)
        if status:
            return status.json()["id"]

    def get_job_photos_folder_id(self, parent_folder_id):
        """Gets the Job Photos folder for the parent id."""
        return self.get_folder_id_from_parent(parent_folder_id, "Job Photos")

    def get_sales_folder_id(self, parent_folder_id):
        """Gets the Sales folder for the parent id."""
        res = self.get_folder_id_from_parent(parent_folder_id, "Sales")
        if res:
            return res
        else:
            return parent_folder_id

    def get_engineering_folder_id(self, parent_folder_id):
        """Gets the Engineering folder inside the applications folder id using the parent ID"""
        ap_id = self.get_applications_folder_id(parent_folder_id)
        if ap_id:
            res = self.get_folder_id_from_parent(ap_id, "Engineering")
            if res:
                return res
            else:
                return False
        else:
            return False

    def get_site_info_documents_folder_id(self, parent_folder_id):
        """gets the site info designs inside of the site info designs folder from parent ID"""
        site_id = self.get_site_info_designs_folder_id(parent_folder_id)
        if site_id:
            res = self.get_folder_id_from_parent(site_id, "Site Info Documents")
            if res:
                return res
            else:
                return False
        else:
            return False

    def get_applications_folder_id(self, parent_folder_id):
        """Gets the Contract Documents folder from the parent id."""
        res = self.get_folder_id_from_parent(parent_folder_id, "Applications")
        if res:
            return res
        else:
            return False

    def get_contract_documents_folder_id(self, parent_folder_id):
        """Gets the Contract Documents folder from the parent id."""
        res = self.get_folder_id_from_parent(parent_folder_id, "Contract Documents")
        if res:
            return res
        else:
            return False

    def get_installation_documents_folder_id(self, parent_folder_id):
        """Gets the Sales folder for the parent id."""
        res = self.get_folder_id_from_parent(parent_folder_id, "Installation Documents")
        if res:
            return res
        else:
            return False

    def get_sales_documents_folder_id(self, parent_folder_id):
        """Gets the Sales folder for the parent id."""
        res = self.get_folder_id_from_parent(parent_folder_id, "Sales Documents")
        if res:
            return res
        else:
            return False

    def get_site_info_designs_folder_id(self, parent_folder_id):
        """Gets the Sales folder for the parent id."""
        res = self.get_folder_id_from_parent(parent_folder_id, "Site Info-Designs")
        if res:
            return res
        else:
            return False

    def get_current_system_drawing_folder_id(self, parent_folder_id):
        """Gets the Sales folder for the parent id."""
        res = self.get_site_info_designs_folder_id(parent_folder_id)
        if res:
            res = self.get_folder_id_from_parent(res, "Current System Drawing")
            if res:
                return res
            else:
                return False
        else:
            return False

    def get_installation_from_folder_id(self, parent_folder_id):
        """
        Job Photos/Installation
        """
        res = self.get_job_photos_folder_id(parent_folder_id)
        if res:
            res = self.get_folder_id_from_parent(res, "Installation")
            if res:
                return res
            else:
                return False
        else:
            return False

    # *****************************************

    def get_folder_id_from_parent(self, parent_folder_id, folder_name):
        """Returns a folder id for the requested folder name in a parent folder."""
        # TODO: add optional create param for creating a folder if it does not exist.
        items_res = self.request_items_in_folder(parent_folder_id)
        if items_res:
            items = items_res.json()["entries"]
            for item in items:
                if item["name"] == folder_name:
                    folder_id = item["id"]
                    # logger.info(f'Found folder id: {folder_id}')
                    return folder_id
        return None

    def get_sales_folder_id_from_opportunity_folder(self, opportunity_folder_id):
        job_photos_id = self.get_job_photos_folder_id(opportunity_folder_id)
        return self.get_sales_folder_id(job_photos_id)

    def get_applications_id_from_opportunity_folder(self, opportunity_folder_id):
        items_res = self.request_items_in_folder(opportunity_folder_id)
        if items_res:
            items = items_res.json()["entries"]
            for item in items:
                if item["name"] == "Job Photos":
                    return item["id"]

        return None

    def upload_LOI_file_to_sales_folder(self, opportunity_folder, file_path):
        sales_folder_id = self.get_sales_folder_id_from_opportunity_folder(
            opportunity_folder
        )
        response = self.request_upload_file(file_path, sales_folder_id, suffix=" - LOI")
        return response

    def upload_file_to_applications_folder(self, opportunity_folder, file_path):
        applications_folder_id = self.get_folder_id_from_parent(
            opportunity_folder, "Applications"
        )
        if applications_folder_id:
            response = self.request_upload_file(file_path, applications_folder_id)
            if response.status_code == 409:
                file_id = response.json()["context_info"]["conflicts"]["id"]
                update_response = self.request_upload_new_file_version(
                    file_id, file_path, applications_folder_id
                )
                return update_response
            else:
                return response

    def request_rename_file(self, file_id, file_name):
        url = f"https://api.box.com/2.0/files/{file_id}"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "as-user": RPA_USER_ID,
        }
        data = {"name": file_name}
        response = requests.put(url, json=data, headers=headers, timeout=120)
        logger.info(f"Update Response:{response}")
        return response

    def request_for_folder_sharedLink(self, folder_id):
        url = BASE_URL + r"/folders/" + folder_id + "?fields=shared_link"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        # BoxValidate(f'Box Request folder sharedLink {folder_id} - Get sharedLink for Box_FolderId')
        response = requests.get(url, headers=headers, timeout=120)
        return response

    def request_for_file_sharedLink(self, file_id):
        url = BASE_URL + r"/files/" + file_id + "?fields=shared_link"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        # BoxValidate(f'Box Request file sharedLink {file_id} - Get sharedLink for Box_FileId')
        response = requests.get(url, headers=headers, timeout=120)
        return response

    def create_sharedLink_for_file(self, file_id):
        params = {"shared_link": {}}
        url = BASE_URL + r"/files/" + file_id + "?fields="
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        # BoxValidate(f'Box Create file sharedLink {file_id} - Get sharedLink for Box_FileId')
        requests.put(url, headers=headers, data=json.dumps(params), timeout=120)
        return

    def create_sharedLink_for_folder(self, folder_id):
        params = {"shared_link": {}}
        url = BASE_URL + r"/folders/" + folder_id + "?fields="
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        # BoxValidate(f'Box Create folder sharedLink {folder_id} - Get sharedLink for Box_FolderId')
        requests.put(url, headers=headers, data=json.dumps(params), timeout=120)
        return

    def request_delete_file(self, file_id):
        url = BASE_URL + r"/files/" + file_id
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        response = requests.delete(url, headers=headers, timeout=120)
        return response

    def request_search_file(self, file_name, file_extension, parent_id=None):
        url = (
            BASE_URL
            + r"/search?query="
            + file_name
            + f"&file_extensions={file_extension}"
        )

        if parent_id:
            url += f"&ancestor_folder_ids={parent_id}"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        response = requests.get(url, headers=headers, timeout=120)
        return response

    def request_file_info(self, file_id):
        url = f"{BASE_URL}/files/{file_id}"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        print("Making request")
        return requests.get(url, headers=headers, timeout=120)

    def request_search_folder(self, folder_name, parent_id):
        url = (
            BASE_URL
            + r"/search?query="
            + folder_name
            + "&type=folder"
            + f"&ancestor_folder_ids={parent_id}"
        )
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
            "as-user": RPA_USER_ID,
        }
        response = requests.get(url, headers=headers, timeout=120)
        return response


if __name__ == "__main__":
    file_id = "251616438363"
    folder_id = "42577426969"
    
    api = BoxAPI(access_token=None, application="OneRoof")
    print(api.get_folder_id_from_parent("243141625656", "Site Info-Designs\Site Info Documents"))
    quit()
    id = api.get_opp_folder_id("006Pl000005lD2A")
    print(id)
    quit()
    res = api.create_sharedLink_for_folder("243629461283")
    print(res)
    #print(res.json())
    # res = api.request_rename_file(file_id, r'46 Barbara Drive, Centereach, NY - MEASURE LAYOUT.pdf')
    # res = api.request_folder_info(folder_id)
    if res.ok:
        import pprint

        pprint.pprint(res.json())
    else:
        print(res.text)

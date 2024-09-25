from typing import Tuple

import requests
import io
import zipfile
import os
from requests.models import Response
import urllib.parse
import sys
sys.path.append(os.environ["autobot_modules"])
import shutil
from CC_Phase_I.cc_config import cC_base_dir

from config import (
    SALES_API_KEY,
    SALES_USERNAME,
    SALES_PASSWORD,
    INSTALLS_API_KEY,
    INSTALLS_USERNAME,
    INSTALLS_PASSWORD,
    SITECAPTURE_BASE_URL,
)
import datetime
from dateutil.relativedelta import relativedelta
from customlogging import logger
from requests.auth import HTTPBasicAuth


class SiteCaptureAPI:
    def __init__(self, installs=False) -> None:
        self.BASE_URL = SITECAPTURE_BASE_URL
        if installs:
            self.AUTH = HTTPBasicAuth(INSTALLS_USERNAME, INSTALLS_PASSWORD)
            self.DEFAULT_HEADERS = {
                "API_KEY": INSTALLS_API_KEY,
                "type": "Basic",
                "Username": INSTALLS_USERNAME,
                "Password": INSTALLS_PASSWORD,
            }
        else:
            self.AUTH = (SALES_USERNAME, SALES_PASSWORD)
            self.DEFAULT_HEADERS = {"API_KEY": SALES_API_KEY}

    def search(self, query, last_updated=None, archived=False) -> Response:
        """
        Searches for a project in site capture using a search query.
        """
        req_url = self.BASE_URL + "2_0/projects?search=" + query
        if last_updated:
            date = last_updated  # mm/dd/yyyy format
            time = "00:00:00"  # hh:mm:ss format
            dt = datetime.datetime.strptime(
                date + " " + time, "%m/%d/%Y %H:%M:%S"
            )  # create a datetime object
            result = dt.strftime("%Y%m%d%H%M%S")  # convert to yyyymmddhhmmss format
            print(result)
            req_url += "&last_updated_after=" + result
        if archived:
            req_url += "&is_archived=true"
        logger.info("Search url : "+req_url)
        res = requests.get(url=req_url, headers=self.DEFAULT_HEADERS, auth=self.AUTH)
        return res
    def assigned_user(self, query, last_updated=None, archived=False) -> Response:
        """
        Searches for a project in site capture using a assigned_user query.
        """
        req_url = self.BASE_URL + "2_0/projects?assigned_user=" + query
        if last_updated:
            date = last_updated  # mm/dd/yyyy format
            time = "00:00:00"  # hh:mm:ss format
            dt = datetime.datetime.strptime(
                date + " " + time, "%m/%d/%Y %H:%M:%S"
            )  # create a datetime object
            result = dt.strftime("%Y%m%d%H%M%S")  # convert to yyyymmddhhmmss format
            print(result)
            req_url += "&last_updated_after=" + result
        if archived:
            req_url += "&is_archived=true"
        logger.info("Assigned user url : "+req_url)
        res = requests.get(url=req_url, headers=self.DEFAULT_HEADERS, auth=self.AUTH)
        return res

    def get_project_id(
        self,
        direct_lead_name,
        customer_last_name,
        address=None,
        last_updated_date=None,
        get_roof_type=False,
        archived=False,
        count_sales=0,
    ) -> str:
        """
        Gets a project id. Searches DL name and cross checks on last name.
        """
        if get_roof_type:
            logger.info("Getting Roof Type from SiteCapture")
        
        #Added on  06-03-2024
        logger.info(str(direct_lead_name)+"=="+str(customer_last_name)+"=="+str(address)+"=="+str(last_updated_date)+"=="+str(get_roof_type)+"=="+str(archived)+"=="+str(count_sales))

        # set default date for today
        date = datetime.datetime.now()
        # set value for current month
        current_month = date.strftime("%m")
        # set value for one month ago
        one_month_ago = date - relativedelta(months=1)
        one_month_ago = one_month_ago.strftime("%m")
        # set value for two months ago
        two_months_ago = date - relativedelta(months=2)
        two_months_ago = two_months_ago.strftime("%m")
        # push all month values into one list to compare to
        recent_months = [one_month_ago, current_month, two_months_ago]

        res=None
        if count_sales == 3:       
            if last_updated_date:
                res = self.assigned_user(direct_lead_name+"&max=1000&offset=0", last_updated_date, archived=archived)
            else:
                if direct_lead_name.strip()!='':
                    logger.info("countsales3-else")
                    res = self.assigned_user(direct_lead_name+"&max=1000&offset=0","", archived=archived) 
                    
        else:        
            if "DL-" in direct_lead_name:
                direct_lead_name = direct_lead_name.replace("DL-", "")    
            if last_updated_date:
                res = self.search(direct_lead_name+"&exact_text=true", last_updated_date, archived=archived)
            else:
                if direct_lead_name.strip()!='':
                    res = self.search(direct_lead_name+"&exact_text=true", archived=archived)
        if res is not None and res.status_code == 200:
            logger.info("inside 200")
            search_data = res.json()
            logger.info("length"+str(len(search_data)))
            # if len(search_data) == 1:
            #     if not get_roof_type:
            #         # print(f"returning id, {search_data[0]['id']}")
            #         return search_data[0]["id"]
            #print(search_data)

            for item in search_data:

                logger.info("inside for loop")
                logger.info("item_id : "+str(item["id"]))
                #       #find month from last updated values
                last_updated = item["last_updated"]
                last_updated = str(last_updated)
                last_updated = last_updated.split(":")[0]
                year, month, date = last_updated.split("-")
                # print(f"{month=}")
                # if month not in recent_months:
                #    continue

                logger.info(str(customer_last_name)+ ", Item name : "+str(item["display_line1"]))




                if customer_last_name.lower() in item["display_line1"].lower():
                    #print(item)
                    if get_roof_type:
                        fields = item["fields"]
                        for field in fields:
                            if field["key"] == "type_of_roofing":
                                return field["display_value"]
                    else:
                        #print('-------------------------------else-------'+str(item))
                        return item["id"]
                customer_last_name = customer_last_name.replace(" ", "")

                logger.info("-------------------------------------------------")
                logger.info(str(customer_last_name)+ ", Item name : "+str(item["display_line1"]))

                if customer_last_name.lower() in item["display_line1"].lower():
                    if get_roof_type:
                        fields = item["fields"]
                        for field in fields:
                            if field["key"] == "type_of_roofing":
                                return field["display_value"]
                            elif field["key"] == "type_of_roofing_1":
                                return field["display_value"]
                    else:
                        return item["id"]
                customer_last_name = customer_last_name.replace("'", "")
                if customer_last_name.lower() in item["display_line1"].lower():
                    if get_roof_type:
                        fields = item["fields"]
                        for field in fields:
                            if field["key"] == "type_of_roofing":
                                return field["display_value"]
                    else:
                        return item["id"]
                customer_last_name = customer_last_name.replace("`", "")
                if customer_last_name.lower() in item["display_line1"].lower():
                    if get_roof_type:
                        fields = item["fields"]
                        for field in fields:
                            if field["key"] == "type_of_roofing":
                                return field["display_value"]
                    else:
                        return item["id"]
                customer_last_name = customer_last_name.replace("’", "")
                if customer_last_name.lower() in item["display_line1"].lower():
                    if get_roof_type:
                        fields = item["fields"]
                        for field in fields:
                            if field["key"] == "type_of_roofing":
                                return field["display_value"]
                    else:
                        return item["id"]

        if address:
            street_split = address.split(" ")
            query = street_split[:2]
            address = " ".join(query)
            res = self.search(address)
            if res.status_code == 200:
                search_data = res.json()
                for item in search_data:
                    # find month from last updated values
                    last_updated = item["last_updated"]
                    last_updated = str(last_updated)
                    last_updated = last_updated.split(":")[0]
                    year, month, date = last_updated.split("-")
                    # print(f"{month=}")
                    if month not in recent_months:
                        continue

                    if customer_last_name.lower() in item["display_line1"].lower():
                        if get_roof_type:
                            fields = item["fields"]
                            for field in fields:
                                if field["key"] == "type_of_roofing":
                                    return field["display_value"]
                        else:
                            return item["id"]

    def get_project_photos(self, project_id, folders=False) -> Response:
        """
        Get the project photos in a zip folder.
        """
        req_url = self.BASE_URL + "1_0/project/images/" + project_id + "?originals=true"
        if folders:
            req_url += "&folders=true"
        res = requests.get(req_url, headers=self.DEFAULT_HEADERS, auth=self.AUTH)
        return res

    def get_projects(
        self, status=None, project_type=None, count=10, offset=None
    ) -> Response:
        """
        Gets projects based on given parameters. API default max count is 100.
        Offsets should be used for counts greater than 100.
        """
        req_url = f"{self.BASE_URL}1_0/projects?max={str(count)}"
        if status:
            req_url += f"&status={urllib.parse.quote(status)}"
        if project_type:
            req_url += f"&type={urllib.parse.quote(project_type)}"
        if offset:
            req_url += f"&offset={str(offset)}"
        return requests.get(url=req_url, headers=self.DEFAULT_HEADERS, auth=self.AUTH)

    def get_sales_photos(
        self,
        photo_directory,
        dl_id,
        opportunity_last_name,
        opportunity_sales_rep,
        opportunity_address,
        loi_date,
    ) -> Tuple[int, str]:
        """
        Find the project id of a corresponding opportunity in site capture and download the photos associated with it
        :param photo_directory: The directory you want to download photos to eg: Sales_Photos/DL-1256768
        :param dl_id: Direct Lead ID in Salesforce
        :param opportunity_last_name: Last name of opportunity
        :param opportunity_sales_rep: First_Name Last_Name of sales rep
        :param opportunity_address: Address of the opportunity
        :param loi_date: Date LOI Signed in Salesforce
        :return: -1 if it could not resolve, 0 if it could download and a string that describes its status
        """
        # TODO : Add logging for this and associated functions
        project_id = ""
        if len(opportunity_last_name.strip())>0:
            project_id = self.get_project_id(dl_id, opportunity_last_name)
            logger.info("DL-ID Serach Result : "+str(project_id))

        # if not project_id:
        if not project_id:
            project_id = self.get_project_id(
                "", opportunity_last_name, opportunity_address
            )
            logger.info("Opportunity Last Name Serach Result : "+str(project_id))

        if not project_id:
            new_opportunity_sales_rep = opportunity_sales_rep.strip().replace(" ", ".")
            logger.info("new_opportunity_sales_rep : " +new_opportunity_sales_rep)
            project_id = self.get_project_id(
                new_opportunity_sales_rep, opportunity_last_name, None, loi_date, None, None, count_sales=3
            )
            logger.info("Sales Rep Serach Result :  "+str(project_id))


        # delete previously downloaded job photos
        if os.path.exists(cC_base_dir + "\\Sales_Photos"):
            logger.info("deleting previously downloaded job photos")
            shutil.rmtree(cC_base_dir + "\\Sales_Photos")


        job_photos = photo_directory
        logger.info(f"job photos path {job_photos}")
        if project_id:
            if not os.path.exists(job_photos):
                logger.info("folder not exist")
                os.mkdir(job_photos)
            output = self.download_project_pictures(project_id, job_photos)

            if output != "":
                return 0, "Downloaded documents from SiteCapture, "
            else:
                logger.info("Could not download photos")
                return -1, "Could not download documents from SiteCapture, "
        else:
            logger.info("Could not retrieve project id")
            return -1, "Could not resolve project id, "

    def download_project_pictures(self, project_id, dst, subfolders=False) -> str:
        """
        Downloads a project's pictures to a specified directory.
        If not given, ./temp is used.
        """
        if not os.path.exists(dst):
            raise FileExistsError(f"Could not find folder {dst}")
        folder = os.path.join(dst, project_id)
        if not os.path.exists(folder):
            os.makedirs(folder)
        res = self.get_project_photos(project_id, subfolders)
        if res.ok:
            zipper = zipfile.ZipFile(io.BytesIO(res.content))
            try:
                zipper.extractall(folder)
            except FileNotFoundError:
                pass
            return folder
        return ""

    def get_report(self, project_id):
        """
        Gets the project report
        this report is based off the default report from the template the project is created in
        """
        req_url = f"{self.BASE_URL}1_0/project/report/{project_id}"
        resp = requests.get(url=req_url, headers=self.DEFAULT_HEADERS, auth=self.AUTH)

        return resp


if __name__ == "__main__":
    a = SiteCaptureAPI()
    
    # print(
    #     a.get_project_id("Martin.Brans", "323 Funston Avenue Reading PA", "", "", "", "", 3 )
    # )
    # res = a.download_project_pictures('883494',"C:/Users/tsbtadmin/Downloads/res/")
    # print(res)

    # project_id = self.get_project_id(
    #             "", "Kirby", "323 Funston Avenue Reading PA"
    #         )
    # # project_id = a.get_project_id(
    # #                 'Cesar Guerrero', 'kirby', None, '2/6/2024'
    # #             )
    # print(project_id)



    # print(
    #     a.get_sales_photos(
    #         "C:/Users/tsbtadmin/Downloads/res/","DL-2036764","Sears","Liam Sheridan","169 Richard Street Newington CT","3/5/2024"
    #     )
    # )






    # def get_project_id(
    #     "Liam.Sheridan",
    #     "",
    #     address=None,
    #     last_updated_date=None,
    #     get_roof_type=False,
    #     archived=False,
    #     count_sales=0,
    # )

    # sc_portal.get_sales_photos(
    #             photo_directory,
    #             dl_id,
    #             opportunity_last_name,
    #             opportunity_sales_rep,
    #             opportunity_address,
    #             loi_date,
    #         )

    # print(a.get_project_id("Liam.Sheridan", "Sears", None, "", True, None, count_sales= 3))

    # a.get_sales_photos(
    #                 photo_directory,
    #                 dl_id,
    #                 opportunity_last_name,
    #                 opportunity_sales_rep,
    #                 opportunity_address,
    #                 loi_date,
    #             )





    # print(
    #     a.get_project_id(
    #         "Alexander.Christensen","Dorazio" ,"","","","",3
    #     )
    # )
    # roof_type1 = a.get_project_id("Greg Ruth", "Groff", None, "3/2/2024", True)
    # print('---')
    # print(roof_type1)

    # print(get_roof_type("DL-2035067","Groff"))
    # # print(a.get_project_id("2023-07-904244", "Thomas James"))


    # print(a.get_project_id("Alexander.Christensen", "Dorazio","","","","",3))




    # # quit()
    # # print(a.get_project_id("1295710", "Basehore", "496 Bernheisel Bridge Road, Carlisle, PA"))
    # print(
    #     a.get_sales_photos(
    #         r"C:\Users\Sha Ahammed Roze\Projects\AutoBot\resources\CC_Phase_I\Sales_Photos",
    #         "DL-1338969",
    #         "Rezendes",
    #         "MJason Mclaughlin",
    #         "9 Marc Ave, Bellingham, MA",
    #         "5/8/2023",
    #     )
    # )
    # #set default date for today
    # date = datetime.datetime.now()
    # #set value for current month
    # current_month = date.strftime("%m")
    # #set value for one month ago
    # one_month_ago = date - relativedelta(months = 1)
    # one_month_ago = one_month_ago.strftime("%m")
    # #set value for two months ago
    # two_months_ago = date - relativedelta(months = 2)
    # two_months_ago = two_months_ago.strftime("%m")
    # #push all month values into one list to compare to
    # recent_months = [one_month_ago, current_month, two_months_ago]

from resources.spotio import Spotio
from resources.config import SPOTIO_CLIENT_SECRET, SPOTIO_CLIENT_ID, STATE_CODES
from flask_restful import Resource, reqparse
import logging
import csv
import io
import sys
import os
sys.path.append(os.environ['autobot_modules'])
from BotUpdate.ProcessTable import RPA_Process_Table
from SalesforceAPI import SalesforceAPI
from Token import token_required
logger = logging.getLogger(__name__)

class SpotioCreateRequest(Resource):
    bot_update = RPA_Process_Table()
    spotio = Spotio(SPOTIO_CLIENT_ID, SPOTIO_CLIENT_SECRET)
    bot_name = "Spotio_Creator"
    sf = SalesforceAPI()
    @token_required
    def post(self):
        self.bot_update.register_bot(self.bot_name)

        parser = reqparse.RequestParser()
        parser.add_argument('content', required=True, type=str)
        args = parser.parse_args()
        content_bytes = args['content']
        # Convert csv string to file so csv module can read
        f = io.StringIO(content_bytes)
        reader = csv.reader(f, delimiter=',')
        # I dont know if the column orders can change but I dont want to deal with it if
        # it does so we get this ugly mess
        first_name_col = 0
        last_name_col = 0
        access_col = 0
        email_col = 0
        phone_col = 0
        id_col = 0
        office_col = 0
        for row_index, row in enumerate(reader):
            if row_index == 0: # Get col indexes from first row
                for col_index, col in enumerate(row):
                    if col == "First Name":
                        first_name_col = col_index
                    if col == "Last Name":
                        last_name_col = col_index
                    if col == "Access Level":
                        access_col = col_index
                    if col == "Email":
                        email_col = col_index
                    if col == "Phone":
                        phone_col = col_index
                    if "User ID Number" in col:
                        id_col = col_index
                    if col == "Sales Office":
                        office_col = col_index
            else:
                #check if values are blank then skip
                if len(row[first_name_col]) == 0:
                    continue
                state_code = row[office_col][0:2]
                if state_code == "PA":
                    state_name = "Direct PA"
                else:
                    state_name = STATE_CODES[state_code]
                territory_id = self.spotio.territory_ids[state_name]
                if row[access_col].lower() == "rep":
                    role = "sales"
                elif row[access_col].lower() == "manger":
                    role = "sales"

                if not len(row[id_col]) == 18:
                    df = self.sf.Select(f"Select Full_User_ID__c from User where Id = '{row[id_col]}'")
                    user_id = list(df['Full_User_ID__c'])[0]
                else:
                    user_id = row[id_col]

                self.bot_update.update_bot_status(self.bot_name, "Creating User", user_id)
                status = self.spotio.create_user(first_name=row[first_name_col],
                                        last_name=row[last_name_col],
                                        email=row[email_col],
                                        phone=row[phone_col],
                                        territory_id=territory_id,
                                        role=role,
                                        external_id=user_id
                                        )
                if status:
                    logger.info(f"Created user for {row[first_name_col]} {row[last_name_col]}")
                    self.bot_update.complete_opportunity(self.bot_name, user_id)
                else:
                    logger.error(f"Could not create user for {row[first_name_col]} {row[last_name_col]}")
                    self.bot_update.update_bot_status(self.bot_name, "Could not create user", user_id)

        self.bot_update.edit_end()
        return {"status":"success"}, 201
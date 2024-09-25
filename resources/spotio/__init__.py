import os
import sys
sys.path.append(os.environ['autobot_modules'])
from .SpotioAPI import SpotioAPI
from config import SPOTIO_TERRITORIES

class Spotio:
    """
    An interface to interact with spotio.
    """
    def __init__(self, client_id, client_secret) -> None:
        self.api = SpotioAPI(client_id=client_id, client_secret=client_secret)
        self.territory_ids = self.get_territory_ids()

    def get_user_names(self) -> list:
        """
        Get available user names. 
        """
        user_data = self.api.get_users()
        user_names = [f'{user["firstName"]} {user["lastName"]}' for user in user_data]
        return user_names

    def get_territory_ids(self) -> dict:
        """
        Get the territory ids in a dict for all valid Trinity states.
        """
        ids = {}
        territory_data = self.api.get_all_territory_data()
        # Spotio does not seem to support querying by titles, therefore we must get them all and match to a list.
        for territory in territory_data:
            if territory['title'] in SPOTIO_TERRITORIES:
                ids[territory['title']] = territory['id']
        return ids

    def create_user(self, first_name, last_name, email, phone, territory_id, role="sales", external_id="") -> bool:
        """
        Creates a user in spotio with the supplied information. Returns True if successful.
        """
        user_data = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            # Chaining replace is simplest and also fastest, albeit a bit verbose
            "phone": phone.replace("-","").replace("(","").replace(")","").replace(" ",""),
            "territoryIds": [
                territory_id
            ],
            "territoryGlobalAccess": False,
            "role": role,
            "isGoogleAccount": False,
            "companyName": "Trinity Solar",
            "externalSystemUserId": external_id
        }
        result = self.api.post_user(user_data)
        if not result:
            return False
        return True
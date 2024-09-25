import requests
from requests.models import Response

class SpotioAPI:
    """
    A Spotio API implementation. All fields should be camelcase based on Spotio docs.
    See https://dev.spotio2.com/api for docs. If API type is not specified in function name
    assume it is production. This is the lowest level API implementation, 
    with most responses being Requests.Response objects. Further manipulation is required
    for getting data.
    """
    PRODUCTION_URL = r'https://api.spotio2.com/api'
    STAGING_URL = r'https://api-test.spotio2.com/api'

    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token(client_id, client_secret)
        if not self.access_token:
            raise Exception('Unable to get access token. Verify ID and Secret.')
        self.headers = {"Authorization":"Bearer " + self.access_token}

    def get_access_token(self, client_id, client_secret) -> str:
        """
        Returns an access token string for the client id and secret given.
        Access tokens last 30 days. No refresh token.
        """
        endpoint = self.PRODUCTION_URL + r'/users/apitoken'
        body = {
            "clientId":client_id,
            "secret":client_secret
        }
        res = requests.post(endpoint, json=body)
        try:
            return res.json()['accessToken']
        except KeyError:
            return ""

    def get_users(self, territory_id=None) -> Response:
        """
        Makes a get request for users data for a given territory if specified.
        Spotio has support for multiple territory ids using a comma separated
        list, but it is unlikely to be needed so it is not implemented.
        """
        endpoint = self.PRODUCTION_URL + r'/users'
        if territory_id:
            endpoint += f'?territoryIds={territory_id}'
        res = requests.get(endpoint, headers=self.headers)
        if res.ok:
            return res.json()

    def post_user(self, user_data) -> Response:
        """
        Makes a post request to create a user.
        """
        endpoint = self.PRODUCTION_URL + r'/users'
        res = requests.post(endpoint, headers=self.headers, json=user_data)
        if res.ok:
            return res.json()

    def get_all_territory_data(self) -> Response:
        """
        Makes a get request for all territories.
        """
        endpoint = self.PRODUCTION_URL + r'/territories/all'
        res = requests.get(endpoint, headers=self.headers)
        if res.ok:
            return res.json()
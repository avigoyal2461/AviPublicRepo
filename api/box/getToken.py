from flask import request
from flask_restful import Resource
from resources.Box.BoxAPI import get_access_token
from Token import token_required

class GetToken(Resource):
    @token_required
    def get(self):
        app = request.args.get("app")
        token = get_access_token(application=app)[0]
        response = {"token": token}
        return response
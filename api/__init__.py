from flask_restful import Resource

class Root(Resource):
    def get(self):
        return {'status':'success'}
    def post(self):
        return {'status':'success'}
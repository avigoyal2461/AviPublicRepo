from flask import Flask, jsonify, request, session, g
from flask_restful import Resource, Api
import requests
import os
from connection import SharepointConnection
# from Create_Excel import Excel
# from Excel_Email import ExcelEmail

# app = Flask(__name__)
app = Flask(__name__)
api = Api(app)
#creates a secret, unused
app.secret_key = "MySecretKey1234"

#the first route, home page
@app.route('/', methods=['GET', 'POST'])
def index():
    # return 'This is the home page'
    return "Method used: %s" % request.method + '\n'+ "Please add /sharepoint at the end of the request, along with folder="
                                                                                                                    #folder=&email=
#http://192.168.0.171:105/Onedrive?file=C:\Documate_2022&email=avigoyal@trinity-solar.com
@app.route('/sharepoint', methods=['GET', 'POST'])
def Sharepoint():
    sharepoint = SharepointConnection()
    folder = request.args['folder']
    # email = request.args['email']
    # excel_email.send(file_path, email)
    relative_path = sharepoint.run(file)

    return f"Finished making sharepoint connection posted to - {relative_path} "

if __name__ == "__main__":
    # app.run(debug=True)
    # a = MyApp()
    app.run(host='0.0.0.0', port=105)
    # app.run(debug=True)

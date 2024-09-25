from flask import Flask, jsonify, request, session, g
from flask_restful import Resource, Api
import requests
import os
# from Create_Excel import Excel
import os
import sys
import time
sys.path.append(os.path.join(os.getcwd(), "box"))
from box.BoxAPI import BoxAPI
import threading
# from flask_oauthlib.provider import OAuth2Provider

# app = Flask(__name__)
#this will allow me to call from online servers (not a localhost)

app = Flask(__name__)
api = Api(app)
# ouath = OAuth2Provider(app)
#creates a secret, unused 
app.secret_key = "MySecretKey1234"

threads = []

#the first route, home page
@app.route('/')
def index():

    # return 'This is the home page'
    return "Method used: %s" % request.method + '\n'+ "welcome to my page, this is a test"

@app.route('/boxGet/<int:sleepTime>', methods=['GET', 'POST'])
def boxGet(sleepTime):
    # var = {''}
    # return "Testing get and post"
    # filepath = input("Please input filepath")
    if request.method == 'POST':
        # print("running one drive..")
        # print("Enter file directory for folder containing PDF files : ")

        #run code

        return 'this is a post, invalid method'

    elif request.method == 'GET':
        # api = BoxAPI()
        # sleepTime = request.args['sleepTime']
        print("hello")
        time.sleep(sleepTime)
        # thread = threading.Thread(target=api.get_opp_folder_id, args=('0065b00000xtjyj'))
        thread = threading.Thread(target=something)
        thread.start()
        threads.append(thread)
        for process in threads:
            process.join()

        # print(process)
        return {'Message': "Finished"}
    
def something():
    print("starting")
    return "success"

if __name__ == "__main__":
    # app.run(debug=True)
    # a = MyApp()
    app.run(host='0.0.0.0', port=105)
    # app.run(debug=True)


    # class MyApp(Resource): # api call - GET method
    #
    #     def get(self,myInput=0):
    #
    #         print('printing from api..')
    #
    #         if myInput:
    #             a = Excel()
    #             print(myInput)
    #             a.run()
    #
    #         return 'api ran Successfully'
    #
    # api.add_resource(MyApp,'/start','/start/<string:myInput>') # defining the api url
    #
    # if __name__=="__main__":

    # app.run(debug=True)

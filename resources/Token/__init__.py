import jwt
import json 
import os
import sys
from flask import Flask, jsonify, request, session, g
from flask_restful import Resource, Api, reqparse
from functools import wraps
from time import time
from datetime import datetime 

sys.path.append(os.environ['autobot_modules'])
from BotUpdate.ProcessTable import RPA_Process_Table

process_name = "RPA_SERVER"
bot_update = RPA_Process_Table()
bot_update.register_bot(process_name)

SECRET_KEY = [
    {'Requestor': 'RPA', 'KEY': ''},
    {'Requestor': 'OneButton', 'KEY': ''},
    {'Requestor': 'MapBox', 'KEY': ''},
    {'Requestor': 'OneRoof', 'KEY': ''},
    {'Requestor': 'OneDraw', 'KEY': ''}
            ]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        t1 = time()
        parser = reqparse.RequestParser()
        token = None
        try:
            parser.add_argument('token', required=True, type=str, location='json')
            args = parser.parse_args()
            token = args['token']
        except:
            try:
                token = request.headers['token']
            except:
                message = "Failed"
                message = timer(t1, message, f, "UNKNOWN")
                return {'message': 'Token is missing! Please try again with the appropriate token listed in json'}, 403

        print(f.__name__)
        if not token:
            message = "Failed, Missing Token"
            message = timer(t1, message, f, "None")
            print(message)
            return {'message': 'Token is missing! Please try again with the appropriate token'}, 403

        try:
            for key_pair in SECRET_KEY:
                if token == key_pair['KEY']:
                    result = f(*args, **kwargs)
                    message = "Success"
                    message = timer(t1, message, f, key_pair.get('Requestor'))
                    print(message)
                    return result

            #else:
                #return {'message': 'Token is Invalid'}, 403
            #data = jwt.decode(token, app.config['SECRET_KEY'])
        except Exception as e:
            print(e)
            message = "Failed, Encountered an error"
            message = timer(t1, message, f, "None")
            print(message)
            return {'message': e}, 403
            

        message = "Failed, Invalid Token"
        message = timer(t1, message, f, "None")
        print(message)
        return {'message': 'Token is Invalid'}, 403
        

    return decorated

def timer(t1, message, function, token):
    t2 = time()
    total_time = f"{(t2-t1):.4f}s"
    todayDate = datetime.today()
    bot_update.update_bot_status(process_name, f'{token}-{message}-{total_time}, {function}', f"{token}-{message},{function}-{todayDate}")
    bot_update.complete_opportunity(process_name, f"{token}-{message},{function}-{todayDate}")

    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    SERVER_LOGS = os.path.join(CURRENT_PATH, "server_logs.txt")
    final_message = f"{todayDate}: Function took - {total_time} with message - {message}, Requestor -  {token} for function - {function}"
    with open(SERVER_LOGS, 'a') as f:
        f.write(final_message + "\n")
        f.close()
    return final_message
import os
import sys
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.Outlook import outlook

from flask_restful import Resource, reqparse
from flask import jsonify, Flask, redirect, render_template, request, url_for, make_response
from datetime import datetime, timedelta


class VerificationCode(Resource):
	def __init__(self):
		self.outlook = outlook

	def get(self):
		code = self.outlook.get_sunnova_verification_code()

		return {'Verification Code': code}
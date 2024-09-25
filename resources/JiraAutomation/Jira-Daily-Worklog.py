import requests
import json
import base64
import pandas as pd
from base64 import encodebytes
import smtplib, ssl
import xlwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from datetime import datetime, timedelta
import configparser
import calendar
import math
import os
import sys
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.Outlook import Outlook
from BotUpdate.ProcessTable import RPA_Process_Table
from AutobotEmail.Email import Email

config = configparser.ConfigParser()
config.read('config.ini')

jiraAuth = config['mypy']['jiraAuth']
cred = "Basic " + base64.b64encode(jiraAuth.encode('utf-8')).decode("utf-8")
headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": cred
}

class JIRAClockWorkReports():
	#daily clockwork log
	def dailyClockworkLog():
		bot_update = RPA_Process_Table()
		bot_name = "Jira_Daily_Worklog"
		identifier = datetime.today()
		bot_update.register_bot(bot_name)
		bot_update.update_bot_status(bot_name, "Uploading", identifier)

		weekend = [6]
		day_of_week = int(datetime.today().weekday())
		if day_of_week in weekend:
			bot_update.complete_opportunity(bot_name, identifier, update_string="Does not run on this day")
			bot_update.edit_end()
			return None
		today = datetime.today() - timedelta(days=1)#runs at 8am, pull log from previous day
		todayString = today.strftime("%Y/%m/%d")

		fileName = "JIRA TimeL Log - " + today.strftime("%m.%d.%Y") + ".xlsx"
		
		sheetData = pd.DataFrame(
						{
							'Author':[],
							'Project Name':[],	
							'Issue Key'	:[],
							'Issue Summary':[],	
							'Issue Status':[],	
							'Time spent':[],
							'Time spent in hours':[],
							'Date Logged':[],
							'Started at':[],
							'Updated at':[],
							'Comment':[],
							'Development Stage':[]
						}
			)
		writer = pd.ExcelWriter(fileName, engine='xlsxwriter')

		issueSearchResults = requests.request("GET",config['mypy']['jiraURI'] + "/search?jql=worklogDate = '" + todayString + "' ORDER BY project,key ASC&maxResults=300", headers=headers)
		issueData = json.loads(issueSearchResults.text)

		if(len(issueData['issues']) != 0):
			for task in issueData["issues"]:	
				projectName = task["fields"]["project"]["name"] or ""
				issueKey = task["key"] or ""
				issueSummary = task["fields"]["summary"] or ""
				issueStatus = task["fields"]["status"]["name"] or ""
				developmentStage_parent = ""
				if(task["fields"]["customfield_10103"] is not None):
					developmentStage_parent = task["fields"]["customfield_10103"]["value"]
				developmentStage_child = ""
				if(task["fields"]["customfield_10103"] is not None and "child" in task["fields"]["customfield_10103"]):
					developmentStage_child = task["fields"]["customfield_10103"]["child"]["value"]
				
				#worklog
				today = datetime.today() - timedelta(days=1) 
				todayString_milli = today.strftime("%d.%m.%Y 23:59:59")
				dt_obj = datetime.strptime(todayString_milli,'%d.%m.%Y %H:%M:%S')
				startedBefore = dt_obj.timestamp() * 1000

				today = datetime.today() - timedelta(days=2) 
				todayString_milli = today.strftime("%d.%m.%Y 23:59:59")
				dt_obj = datetime.strptime(todayString_milli,'%d.%m.%Y %H:%M:%S')
				startedAfter = dt_obj.timestamp() * 1000

				worklogResults = requests.request("GET",config['mypy']['jiraURI'] + "/issue/" + issueKey + "/worklog?startedAfter=" + str(int(startedAfter)) + "&startedBefore=" +  str(int(startedBefore)), headers=headers)
				worklogData = json.loads(worklogResults.text)
				if(len(worklogData['worklogs']) != 0):
					for worklog in worklogData["worklogs"]:	
						authorName = worklog["author"]["displayName"]
						comment = ""
						if("comment" in worklog):
							if(len(worklog["comment"]["content"])> 0):
								content =worklog["comment"]["content"][0] 
								while("content" in content):
									content = content["content"][0]
								try:
									comment = content["text"]
								except:
									pass
						created = worklog["created"]
						updated = worklog["updated"]
						timeSpentInSeconds = worklog["timeSpentSeconds"]

						#write to excel
						rowData = {
							'Author':authorName,
							'Project Name':projectName,	
							'Issue Key'	:issueKey,
							'Issue Summary':issueSummary,	
							'Issue Status':issueStatus,	
							'Time spent':timeSpentInSeconds,
							'Time spent in hours':math.floor(round(float(timeSpentInSeconds) / 3600,2)* 100) / 100,
							'Date Logged':created,
							'Started at':created,
							'Updated at':updated,
							'Comment':comment,
							'Development Stage':str(developmentStage_parent) + """ - """ + str(developmentStage_child)
						}
						sheetData = sheetData.append(rowData, ignore_index=True)

		sheetData.to_excel(writer, sheet_name='Sheet1', index=False)
		for column in sheetData:
			column_width = max(sheetData[column].astype(str).map(len).max(), len(column))
			col_idx = sheetData.columns.get_loc(column)
			writer.sheets['Sheet1'].set_column(col_idx, col_idx, column_width)
		writer.save()
		# body = "Hello All,<br/><br/>Please find the attached JIRA Timelog Report for " + todayString
		body = """Hello All,
Please find the attached JIRA Timelog Report for """ + todayString
		receiver = ["mathewmullan@trinity-solar.com", "jayasri.ranganathan@trinity-solar.com", "debashish.mukherjee@trinity-solar.com", "vijay.madduri@trinity-solar.com", "phaniraja.sridhara@trinity-solar.com", "khalid.mansoor@trinitysolarsystems.com", "christopher.stuckey@trinity-solar.com", "jeff.macdonald@trinity-solar.com", "avigoyal@trinity-solar.com", "powerautomateteam@trinity-solar.com"]
		JIRAClockWorkReports.sendEmail(receiver, [], "JIRA - Daily Timelog Report", body, fileName)

		bot_update.complete_opportunity(bot_name, identifier)
		bot_update.edit_end()
	
	def sendEmail(tos, ccs, subject, body, fileName):
		email =  Email(subject=subject,
		 			   body=body)
		email.add_recipients(tos)
		email.add_attachment_from_path(fileName)
		Outlook().send_email(email)


		# sender = config['mypy']['emailUN']
		# password = config['mypy']['emailPWD']
		# mainMessage = MIMEMultipart()
		# messageHTML = MIMEText(body, 'html')
		# mainMessage.attach(messageHTML)
		# mainMessage["Subject"] = subject
		# mainMessage["From"] = config['mypy']['emailFrom']
		# mainMessage["To"] = ",".join(tos)
		# mainMessage["Cc"] = ",".join(ccs)

		# with open(fileName, "rb") as fil:attachment = MIMEApplication(fil.read(),Name=fileName)
		# attachment['Content-Disposition'] = 'attachment; filename="' + fileName + '"'
		# mainMessage.attach(attachment)

		# conn = smtplib.SMTP(config['mypy']['smtpURL'],config['mypy']['smtpPort'])
		# try:
		# 	conn.starttls()
		# 	conn.set_debuglevel(True)
		# 	conn.login(sender, password)
		# 	conn.sendmail(sender, tos + ccs, mainMessage.as_string())
		# 	print("success")
		# 	os.remove(fileName)
		# finally:
		# 	conn.quit()

JIRAClockWorkReports.dailyClockworkLog()


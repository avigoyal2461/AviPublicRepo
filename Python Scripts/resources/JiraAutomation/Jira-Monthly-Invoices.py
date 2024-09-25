import requests
import json
import base64
import pandas as pd
from openpyxl.styles import Border,Side, borders
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_range
from base64 import encodebytes
import smtplib, ssl
import xlwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO
import configparser
import calendar
import math
import psycopg2
import time
import sys
import os
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.Outlook import Outlook
from BotUpdate.ProcessTable import RPA_Process_Table
from AutobotEmail.Email import Email

#config = configparser.ConfigParser()
with open("jira_config.json") as config_file:
	config = json.load(config_file)

jiraAuth = config['mypy']['jiraAuth']
cred = "Basic " + base64.b64encode(jiraAuth.encode('utf-8')).decode("utf-8")
headers = {
	"Accept": "application/json",
	"Content-Type": "application/json",
	"Authorization": cred
}

class JIRAClockWorkReports():

	def monthlyInvoice():
		bot_update = RPA_Process_Table()
		bot_name = "Jira_Monthly_Invoices"
		identifier = datetime.today()
		bot_update.register_bot(bot_name)
		bot_update.update_bot_status(bot_name, "Uploading", identifier)

		localTime = time.localtime()
		dstFlag = localTime.tm_isdst
		dstValue = 5;
		if(dstFlag):
			dstValue = 4;

		prevMonth = datetime.today() - relativedelta(months=1) # get current date - 1 month
		prevMonthString = prevMonth.strftime("%B")
		prevMonthYear = prevMonth.strftime("%Y")
		prevMonthLastDay = calendar.monthrange(int(prevMonth.strftime("%Y")), int(prevMonth.strftime("%m")))[1] #last day of prev month

		postgresStartDate = prevMonth.strftime("%Y-%m-01") #1st day of prev month
		postgresEndDate = prevMonth.strftime("%Y-%m-" + str(prevMonthLastDay)) #last day of prev month

		receivers = {
		 				"Citrus":["Sarji & Gayathri","sarji.mohammedali@citrusinformatics.com","gayathri.girijadevi@citrusinformatics.com"],
		 				#"DazeWorks":["Mayank & Fathima","mayank.harsh@dazeworks.com","fathima.omar@dazeworks.com","pmo@dazeworks.com"],
		 				"Impaqtive":["Praveen & Joseph","accounts@impaqtive.com","praveen@impaqtive.com","joe@impaqtive.com"],
		 				"Maptell":["Jitesh","jithesh@trentecsystems.com","suppport@trentecsystems.com"],
		 				#"Thinking Solutions":["Manish & Vishal","manish.vaidya@thinkingsolution.com","vishal.shah@thinkingsolution.com","accounts@thinkingsolution.com"],
						"DesignSense":["Rakesh","rakesh.rao@thedesignsense.com"]
		 			}
		emailSubject = ""
  
		conn = psycopg2.connect(database = config['mypy']['postgres_db'], 
                        user = config['mypy']['postgres_user'], 
                        host= config['mypy']['postgres_host'],
                        password = config['mypy']['postgres_pwd'],
                        port = 5432)
		for group in receivers:
			fileName = group + " " + prevMonthString + " " + prevMonthYear + ".xlsx"
			workbook = xlsxwriter.Workbook(fileName)
			worksheet = workbook.add_worksheet()

			row = 0
			col = 0
			worksheet.write(0, 0, 'Project')
			col+=1

			cur = conn.cursor()
			cur.execute("SELECT C.\"ID\",C.\"DISPLAY_NAME\", C.\"ACCOUNT_ID\" "\
       						"FROM jira.\"GROUPS\" AS A "\
           					"INNER JOIN jira.\"GROUP_MEMBERS\" as B on A.\"ID\" = B.\"GROUP_ID\" "\
               				"INNER JOIN jira.\"USERS\" as C on B.\"MEMBER_USER_ID\" = C.\"ID\" "\
                       		f"WHERE A.\"NAME\" = '{group}' ORDER BY C.\"DISPLAY_NAME\"")
			members = cur.fetchall()
			conn.commit()
			for member in members:
				userid = member[0]
				displayName = member[1]
				accountID = member[2]
				
				worksheet.write(0, col, displayName)
				col+=1

			worksheet.write(0, col, "TOTAL")
			row+=1	
			
			#get all projects
			cur = conn.cursor()
			cur.execute("SELECT \"KEY\", \"NAME\" FROM jira.\"PROJECTS\" WHERE \"PROJ_TYPE_ID\" = 2 order by \"NAME\" ASC")
			projects = cur.fetchall()
			conn.commit()
			totalProjectTime = 0 

			for project in projects:
				projectKey = project[0]
				projectName = project[1]

				totalProjectTime = 0
				col = 0
				worksheet.write(row, col, projectName)
				col+=1

				for member in members:
					userid = member[0]
					displayName = member[1]
					accountID = member[2]
					totalUserTimeInProject = 0
					print(f"Working on {displayName} for Project {project}")

     
					cur = conn.cursor()
					cur.execute(f"""SELECT Distinct CASE WHEN SUM(A.\"TIME_SPENT_SECONDS\") / 3600 IS NULL THEN 0 ELSE SUM(A.\"TIME_SPENT_SECONDS\") / 3600 END 
								FROM jira.\"ISSUE_WORKLOGS\" as A 
								INNER JOIN jira.\"ISSUES\" as B on A.\"ISSUE_ID\" = B.\"ID\" 
								INNER JOIN jira.\"ISSUE_FIELD_VALUES\" as C on B.\"ID\" = C.\"ISSUE_ID\" 
								INNER JOIN jira.\"PROJECTS\" as D on C.\"PROJECT_ID\" = D.\"ID\" 
								INNER JOIN jira.\"USERS\" as E on A.\"AUTHOR_USER_ID\" = E.\"ID\" 
								WHERE ((A.\"STARTED\" - interval '{dstValue} hours') BETWEEN '{postgresStartDate} 00:00:00' AND '{postgresEndDate} 23:59:59') 
								AND D.\"KEY\" = '{projectKey}'
								AND E.\"ACCOUNT_ID\" = '{accountID}'""")
					timeLogs = cur.fetchall()
					conn.commit()
					
					for timelog in timeLogs:
						hours = timelog[0]
						totalUserTimeInProject = totalUserTimeInProject + hours
						totalProjectTime = totalProjectTime + totalUserTimeInProject

					worksheet.write(row, col, totalUserTimeInProject)
					col+=1
				worksheet.write(row, col, totalProjectTime)
				row+=1

			#************* totals **********************#
			worksheet.write(len(projects), 0, "TOTAL")
			i = 1
			while i <= (len(members) + 1):
				startRow = 1
				endRow = len(projects)

				valueCell = xl_rowcol_to_cell(endRow, i)
				sumRange = xl_range(startRow, i, endRow-1, i)
				worksheet.write_formula(valueCell, f'=SUM({sumRange})') 
				i+=1

			border_fmt = workbook.add_format({'bottom':1, 'top':1, 'left':1, 'right':1})
			worksheet.conditional_format(xlsxwriter.utility.xl_range(0, 0, endRow, i-1), {'type': 'no_errors', 'format': border_fmt})
			
			workbook.close()

			contactInfo = receivers.get(group)
			toNames = contactInfo[0]
			toAddresses = []
			for index,email in enumerate(contactInfo):
				if(index != 0):
					toAddresses += [email]
			if group == "Maptell":
				group = "Trentec"
			emailSubject = group + " " + prevMonthString + " " + prevMonthYear + " Hours"
			body = toNames + ",<br/><br/>Attached are the hours for the " + group + " team for the month of " + prevMonthString + " " + prevMonthYear + ". <br/>Please Review and generate the invoice off of these hours."
			trinityemails = ["phaniraja.sridhara@trinity-solar.com", "apttech@trinity-solar.com", "christopher.stuckey@trinity-solar.com","jayasri.ranganathan@trinity-solar.com", "mathew.mullan@trinity-solar.com","debashish.mukherjee@trinity-solar.com","khalid.mansoor@trinitysolarsystems.com", "avigoyal@trinty-solar.com"]
			JIRAClockWorkReports.sendEmail(toAddresses, trinityemails, emailSubject, body, fileName)
			
			bot_update.complete_opportunity(bot_name, identifier)
			bot_update.edit_end()
			try:
				os.remove(fileName)
			except:
				pass
	def sendEmail(tos, ccs, subject, body, fileName):
		email =  Email(subject=subject,
		 			   body=body)
		email.add_recipients(tos)
		for item in ccs:
			email.add_cc(item)
		email.add_attachment_from_path(fileName)
		Outlook().send_email(email)
		print("Sent email")
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
		# 	# conn.sendmail(sender, tos + ccs, mainMessage.as_string())
		# 	conn.sendmail(sender, [tos] + ccs, mainMessage.as_string())
		# 	print("success")
		# 	os.remove(fileName)
		# finally:
		# 	conn.quit()

JIRAClockWorkReports.monthlyInvoice()



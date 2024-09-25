from base64 import encodebytes
import smtplib, ssl
import xlwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta, MO
import configparser
import calendar
import math
import psycopg2
import pyodbc 
import time
import os
import sys
#config = configparser.ConfigParser()
#config.read('config.ini')
sys.path.append(os.environ['autobot_modules'])
from BotUpdate.dbconnection import connection
from BotUpdate.ProcessTable import RPA_Process_Table
from AutobotEmail.Email import Email
from AutobotEmail.Outlook import Outlook


db_connection = connection("PROD")
conn = db_connection.connect_to_server()

today = date.today()
dayOfWeek = date.today().strftime('%A')
if(dayOfWeek == 'Monday'):
    metricDate = today - timedelta(days = 2)
else:
    metricDate = today - timedelta(days = 1)

metricDateString = metricDate.strftime('%m/%d/%Y')    
startOfMonth = metricDate.strftime('%m/01/%Y')

bot_update = RPA_Process_Table()
bot_name = "OBA_Daily_Report"
identifier = datetime.today()
bot_update.register_bot(bot_name)
bot_update.update_bot_status(bot_name, "Uploading", identifier)

emailBody = "Hi Kathy,<br/><br/>Please find the daily status update for oneBUTTON with open issues and key metrics for " + metricDateString + "<br/><br/>"

#initial temp tables
#conn = pyodbc.connect()
cursor = conn.cursor()

#TOTAL CONTRACTS TO DATE
totalContractsToDateQuery = """SELECT COUNT(*)
                                FROM wolf.Opportunity_Contract oc (NOLOCK)
                                INNER JOIN wolf.Finance_Partner_Quote fpq (NOLOCK) ON fpq.Sunnova_Quote_Id = oc.Sunnova_Quote_Id
                                INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
                                INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
                                WHERE (Cast(oc.User_Created_Timestamp as date) BETWEEN '2023-10-01' and '""" + metricDate.strftime('%Y-%m-%d') + """') and fpq.Selected_For_Showing=1"""
cursor.execute(totalContractsToDateQuery)
data = cursor.fetchall()
totalContractsToDate = data[0][0]
emailBody += "<b><u>TOTAL CONTRACTS TO DATE (SINCE OCT 2023):</b></u> " + str('{:,}'.format(totalContractsToDate)) + "<br/><br/>"

emailBody += "<b><u>Key Open Issues as of " + metricDateString + "</b></u><br/>** ENTER OPEN ISSUES HERE ***<br/><br/>"
emailBody += "<b><u>Traditional Metrics " + metricDateString + "</b></u><br/>"
emailBody += """<table style='border-collapse: collapse;'>
				<tr>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>User</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Office</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Division</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Finance Method</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;text-align:center;'># Quote</td>
				</tr>"""


#Traditional Quotes
traditionalQuotesQuery = """SELECT ct.Contact_First_Name, ct.Contact_Last_Name, op.Managing_Office, ct.Sales_Division, fpq.Contract_Type, COUNT(*) AS Quote_Count
							FROM wolf.Finance_Partner_Quote fpq (NOLOCK)
							INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
							INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
							WHERE Cast(fpq.User_Created_Timestamp as date) = '""" + metricDate.strftime('%Y-%m-%d') + """' and fpq.Active_Ind=1 
							AND ct.Sales_Division = 'Sales- Traditional'
							GROUP BY ct.Contact_First_Name, ct.Contact_Last_Name, op.Managing_Office, ct.Sales_Division, fpq.Contract_Type
							ORDER BY ct.Contact_First_Name, ct.Contact_Last_Name, op.Managing_Office, ct.Sales_Division, fpq.Contract_Type"""
cursor.execute(traditionalQuotesQuery)
traditionalQuotes = cursor.fetchall()
totalTradQuoteCount = 0
for quote in traditionalQuotes:
	fn = quote[0]
	ln = quote[1]
	office = quote[2]
	division = quote[3]
	finMethod = quote[4]
	quoteCount = quote[5]
	totalTradQuoteCount += quoteCount
	emailBody += """<tr>
						<td style='border: 1px solid;padding:5px;'>""" + fn + """ """ + ln + """</td>
						<td style='border: 1px solid;padding:5px;'>""" + office + """</td>
						<td style='border: 1px solid;padding:5px;'>""" + division + """</td>
						<td style='border: 1px solid;padding:5px;'>""" + finMethod + """</td>
						<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(quoteCount) + """</td>
					</tr>"""
emailBody += """<tr>
						<td style='border: 1px solid;padding:5px;'></td>
						<td style='border: 1px solid;padding:5px;'></td>
						<td style='border: 1px solid;padding:5px;'></td>
						<td style='border: 1px solid;padding:5px;'>TOTAL</td>
						<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(totalTradQuoteCount) + """</td>
					</tr></table><br/><br/>"""
					
#Traditional Contracts
emailBody += """<table style='border-collapse: collapse;'>
				<tr>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>User</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Office</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Division</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Finance Method</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;text-align:center;'># Contracts</td>
				</tr>"""
traditionalContractsQuery = """SELECT ct.Contact_First_Name, ct.Contact_Last_Name, op.Managing_Office, ct.Sales_Division, fpq.Contract_Type, COUNT(*) AS Contract_Count
								FROM wolf.Opportunity_Contract oc (NOLOCK)
								INNER JOIN wolf.Finance_Partner_Quote fpq (NOLOCK) ON fpq.Sunnova_Quote_Id = oc.Sunnova_Quote_Id
								INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
								INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
								WHERE (Cast(oc.User_Created_Timestamp as date) = '""" + metricDate.strftime('%Y-%m-%d') + """') and fpq.Selected_For_Showing=1
								AND ct.Sales_Division = 'Sales- Traditional'
								GROUP BY ct.Contact_First_Name, ct.Contact_Last_Name, op.Managing_Office, ct.Sales_Division, fpq.Contract_Type
								ORDER BY ct.Contact_First_Name, ct.Contact_Last_Name, op.Managing_Office, ct.Sales_Division, fpq.Contract_Type"""
cursor.execute(traditionalContractsQuery)
traditionalContracts = cursor.fetchall()
totalTradContractCount = 0
for contract in traditionalContracts:
	fn = contract[0]
	ln = contract[1]
	office = contract[2]
	division = contract[3]
	finMethod = contract[4]
	contractCount = contract[5]
	totalTradContractCount += contractCount
	emailBody += """<tr>
						<td style='border: 1px solid;padding:5px;'>""" + fn + """ """ + ln + """</td>
						<td style='border: 1px solid;padding:5px;'>""" + office + """</td>
						<td style='border: 1px solid;padding:5px;'>""" + division + """</td>
						<td style='border: 1px solid;padding:5px;'>""" + finMethod + """</td>
						<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(contractCount) + """</td>
					</tr>"""
emailBody += """<tr>
					<td style='border: 1px solid;padding:5px;'></td>
					<td style='border: 1px solid;padding:5px;'></td>
					<td style='border: 1px solid;padding:5px;'></td>
					<td style='border: 1px solid;padding:5px;'>TOTAL</td>
					<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(totalTradContractCount) + """</td>
				</tr></table><br/><br/>
				
				<b><u>All Metrics: """ + startOfMonth + """ to date:</u></b><br/>
				<table style='border-collapse: collapse;'>
				<tr>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'></td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Contracts/Day</td>
					<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Quotes/Day</td>
				</tr>
				<tr>
					<td style='border: 1px solid;padding:5px;'>""" + startOfMonth + """ - """ + metricDateString + """</td>"""

#Contracts/Day					
contractsPerDayQuery = """SELECT (COUNT(*) / CONVERT(integer, DAY('""" + metricDate.strftime('%Y-%m-%d') + """')))
							FROM wolf.Opportunity_Contract oc (NOLOCK)
							INNER JOIN wolf.Finance_Partner_Quote fpq (NOLOCK) ON fpq.Sunnova_Quote_Id = oc.Sunnova_Quote_Id
							INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
							INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
							WHERE (Cast(oc.User_Created_Timestamp as date) >= '""" + metricDate.strftime('%Y-%m-01') + """') 
							AND Cast(oc.User_Created_Timestamp as date) < CAST(GETDATE() as date)  
							and fpq.Selected_For_Showing=1"""
cursor.execute(contractsPerDayQuery)
data = cursor.fetchall()
contractsPerDay = data[0][0]
emailBody += """<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(contractsPerDay) + """</td>"""

#Quotes/Day
quotesPerDayQuery = """SELECT (COUNT(*) / CONVERT(integer, DAY('""" + metricDate.strftime('%Y-%m-%d') + """')))
						FROM wolf.Finance_Partner_Quote fpq (NOLOCK)
						INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
						INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
						WHERE Cast(fpq.User_Created_Timestamp as date) >= '""" + metricDate.strftime('%Y-%m-01') + """' 
						AND Cast(fpq.User_Created_Timestamp as date) < CAST(GETDATE() as date)  and fpq.Active_Ind=1 """
cursor.execute(quotesPerDayQuery)
data = cursor.fetchall()
quotesPerDay = data[0][0]
emailBody += """<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(quotesPerDay) + """</td>"""
emailBody += """</tr></table><br/><br/>
				<table style='border-collapse: collapse;'>
					<tr>
						<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'></td>
						<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Total Contracts</td>
						<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Total Quotes</td>
					</tr>
					<tr>
					<td style='border: 1px solid;padding:5px;'>""" + startOfMonth + """ - """ + metricDateString + """</td>"""

#Total Contracts
totalContractsQuery = """SELECT COUNT(*)
							FROM wolf.Opportunity_Contract oc (NOLOCK)
							INNER JOIN wolf.Finance_Partner_Quote fpq (NOLOCK) ON fpq.Sunnova_Quote_Id = oc.Sunnova_Quote_Id
							INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
							INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
							WHERE (Cast(oc.User_Created_Timestamp as date) >= '""" + metricDate.strftime('%Y-%m-01') + """') 
							AND Cast(oc.User_Created_Timestamp as date) < CAST(GETDATE() as date)  
							and fpq.Selected_For_Showing=1"""
cursor.execute(totalContractsQuery)
data = cursor.fetchall()
totalContracts = data[0][0]
emailBody += """<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(totalContracts) + """</td>"""

#Total Quotes
totalQuotesQuery = """SELECT COUNT(*)
						FROM wolf.Finance_Partner_Quote fpq (NOLOCK)
						INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
						INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
						WHERE Cast(fpq.User_Created_Timestamp as date) >= '""" + metricDate.strftime('%Y-%m-01') + """' 
						AND Cast(fpq.User_Created_Timestamp as date) < CAST(GETDATE() as date)  and fpq.Active_Ind=1 """
cursor.execute(totalQuotesQuery)
data = cursor.fetchall()
totalQuotes = data[0][0]
emailBody += """<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(totalQuotes) + """</td>"""
emailBody += """</tr></table><br/><br/>"""

#Quotes and Contracts Per Day
emailBody += """<table style='border-collapse: collapse;'>
					<tr>
						<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Date</td>
						<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Contracts</td>
						<td style='border: 1px solid;padding:5px;background-color:rgb(112,173,71);color:white;'>Quotes</td>
					</tr>"""
					
start_date = date.today().replace(day=1)
end_date = today - timedelta(days = 1)

while (end_date >= start_date):
		#daily contracts
		dailyContractsQuery = """SELECT COUNT(*)
									FROM wolf.Opportunity_Contract oc (NOLOCK)
									INNER JOIN wolf.Finance_Partner_Quote fpq (NOLOCK) ON fpq.Sunnova_Quote_Id = oc.Sunnova_Quote_Id
									INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
									INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
									WHERE (Cast(oc.User_Created_Timestamp as date) = '""" + end_date.strftime('%Y-%m-%d') + """') 
									and fpq.Selected_For_Showing=1"""
		cursor.execute(dailyContractsQuery)
		data = cursor.fetchall()
		dailyContracts = data[0][0]
	
		#daily quotes
		dailyQuotesQuery = """SELECT COUNT(*)
						FROM wolf.Finance_Partner_Quote fpq (NOLOCK)
						INNER JOIN wolf.Opportunity op (NOLOCK) ON op.Opportunity_Id = fpq.Opportunity_Id
						INNER JOIN wolf.Contact ct (NOLOCK) ON op.Trinity_Salesperson_Id = ct.Contact_Id
						WHERE Cast(fpq.User_Created_Timestamp as date) = '""" + end_date.strftime('%Y-%m-%d') + """' and fpq.Active_Ind=1 """
		cursor.execute(dailyQuotesQuery)
		data = cursor.fetchall()
		dailyQuotes = data[0][0]
		
		emailBody += """<tr>
						<td style='border: 1px solid;padding:5px;'>""" + end_date.strftime('%m/%d/%Y') + """</td>
						<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(dailyContracts) + """</td>
						<td style='border: 1px solid;padding:5px;text-align:center;'>""" + str(dailyQuotes) + """</td>
					</tr>"""

		end_date += timedelta(days = -1)
emailBody += """</table>"""

"""
sender = config['mypy']['emailUN']
password = config['mypy']['emailPWD']
mainMessage = MIMEMultipart()
messageHTML = MIMEText(emailBody, 'html')
mainMessage.attach(messageHTML)
mainMessage["Subject"] = "oneBUTTON Daily Status Report " + metricDateString
mainMessage["From"] = config['mypy']['emailFrom']
mainMessage["To"] = ",".join(["mathewmullan@trinity-solar.com","bryan.bigica@trinity-solar.com","ashane.robert@trinity-solar.com"])

conn = smtplib.SMTP(config['mypy']['smtpURL'],config['mypy']['smtpPort'])
try:
	conn.starttls()
	conn.set_debuglevel(True)
	conn.login(sender, password)
	conn.sendmail(sender, ["mathewmullan@trinity-solar.com","bryan.bigica@trinity-solar.com","ashane.robert@trinity-solar.com"], mainMessage.as_string())
	print("success")	
finally:
	conn.quit()
"""
email =  Email(subject="oneBUTTON Daily Status Report " + metricDateString,
				body=emailBody)
email.add_recipients(["mathewmullan@trinity-solar.com","bryan.bigica@trinity-solar.com","ashane.robert@trinity-solar.com"])
Outlook().send_email(email)

bot_update.complete_opportunity(bot_name, identifier)
bot_update.edit_end()
# Resource Folder Import
import os
import sys
from bs4 import BeautifulSoup
import pytz
#import datetime as dt
import pandas as pd
from datetime import datetime, timedelta
import random
from flask import jsonify, Flask, redirect, render_template, request, url_for, make_response, session
from flask_restful import Resource, reqparse

from api.Dashboard import blueprint

sys.path.append(os.environ['autobot_modules'])
from BotUpdate.ProcessTable import RPA_Process_Table
from BotUpdate.RPATable import RPATable
from sql.BP import bp_database
from config import ADMIN, TSA_USERS

WEEKDAYS = {
	0: "LastWeek_Monday",
	1: "LastWeek_Tuesday",
    2: "LastWeek_Wednesday",
    3: "LastWeek_Thursday",
    4: "LastWeek_Friday",
    5: "LastWeek_Saturday",
    6: "LastWeek_Sunday",
	7: "Monday",
	8: "Tuesday",
    9: "Wednesday",
    10: "Thursday",
	11: "Friday",
    12: "Saturday",
    13: "Sunday"
}

MONTH_CODES = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}

FULL_MONTH_CODES = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}
table = RPATable("rpa", "Process", config_path="DEV")
tsa_table = RPATable("tsa", "Database_DDL_Audit", config_path="PROD")
bp_table = bp_database()

class getDashboard(Resource):
	def __init__(self):
		self.process_table = RPA_Process_Table()

		timestamp = table.create_timestamp()
		self.timestamp = timestamp
		self.date, time = timestamp.split(" ")
		#create stamp for yesterday
		datetime_object = datetime.strptime(self.date, '%Y-%m-%d').date()
		self.yesterday =  str((datetime_object - timedelta(days=1)))
		self.tomorrow =  str((datetime_object + timedelta(days=1)))

	def get(self):
		"""
		Gets the process Table, all bot details and running statuses
		"""
		now = datetime.now()
		df = self.process_table.Select_All()
		
		running = []
		completed_today = []
		completed_last_hour = []
		full_opportunity_info = []
		started_not_finished = []
		started_not_finished_length = []

		for index, value in enumerate(df['Process_Name']):
			if not df.loc[index].at['Active_Ind']:
				running.append("Disabled")
			elif not df.loc[index].at['Is_Continuous'] or not df.loc[index].at['Last_Updated_Timestamp']:
				running.append("Not Updating")
			else:
				#take current time, dateobject and convert to est
				date_object = str(df.loc[index].at['Last_Updated_Timestamp'])
				date_object = convert_from_utc_to_est(date_object)

				#input est time back to table so it prints as GMT
				df.loc[index, 'Last_Updated_Timestamp'] = date_object

				#if broken down time is within an hour of now, log as running, else log as failing
				if now - timedelta(hours=1) <= date_object <= now + timedelta(hours=1):
					running.append("Yes")
				else:
					running.append("Not Running")

			completed_by_bot = []
			completed_by_bot_last_hour = [] #for now will not remove duplicates from this list to get proper metrics
			try:
				today_logs, last_hour_completed = self.process_table.Select_Opportunities_Completed_Today(value, last_hour=True)
			except:
				today_logs = self.process_table.Select_Opportunities_Completed_Today(value)
				last_hour_completed = ["Unable to pull data on last hour completed"]

			#[completed_by_bot.append(x) for x in possible_duplicates if x not in completed_by_bot]

			uncompleted = self.process_table.Select_Opportunities_Started(value)

			started_not_finished.append(uncompleted)
			started_not_finished_length.append(len(uncompleted))
			#full_opportunity_info.append(completed_by_bot)
			full_opportunity_info.append(today_logs)
			#completed_today.append(len(completed_by_bot))
			completed_today.append(len(today_logs))
			completed_last_hour.append(last_hour_completed)
		
		cols = ['Process_Id', 'Process_Name', 'Process_Description', 'Is_Continuous', 'Active_Ind', 'Last_Updated_Timestamp', 'User_Created_Timestamp', 'User_Created_Id', 'User_Modified_Timestamp', 'User_Modified_Id']
		bp_df = pd.DataFrame(columns=cols)

		for counter, queueid in enumerate(bp_table.queues_dictionary['id']):
			bp_info_completed, bp_last_hour = bp_table.get_items("completed", queueid, last_hour=True)
			bp_info_exception = bp_table.get_items("exception", queueid)
			running.append("Not Updating")
			data = {
				'Process_Id': "BP",
				'Process_Name': bp_table.queues_dictionary["name"][counter],
				'Process_Description': "Blue prism process",
				'Is_Continuous': True,
				'Active_Ind': True,
				'Last_Updated_Timestamp': "2023-11-08 16:40:11.000",
				'User_Created_Timestamp': "2022-12-15 15:50:46.290",
				'User_Created_Id': "rpa_bot_user",
				'User_Modified_Timestamp': "2022-12-15 15:50:46.290",
				'User_Modified_Id': "rpa_bot_user",
			}
			bp_df = bp_df.append(data, ignore_index=True)
			started_not_finished.append(list(bp_info_exception['keyvalue']))
			started_not_finished_length.append(len(bp_info_exception['keyvalue']))
			full_opportunity_info.append(list(bp_info_completed['keyvalue']))
			completed_today.append(len(bp_info_completed['keyvalue']))
			completed_last_hour.append(list(bp_last_hour['keyvalue']))

		df = df.append(bp_df, ignore_index=True)
		#df = pd.concat([df, bp_df], axis=1)
		print(df)

		df['last_hour'] = completed_last_hour
		df['full_opportunity_info'] = full_opportunity_info
		#df['completed_today'] = completed_by_bot
		df['completed_today'] = completed_today
		df['Running'] = running
		df['Unfinished'] = started_not_finished
		df['Unfinished_length'] = started_not_finished_length
		
		df = df.sort_values(['Running', 'Process_Id'], ascending=[True, True])
		data = df.to_dict('records')
		print(df)
		return jsonify(data)

	def post(self):
		"""
		Gets the process detail of given bot by date , if no date provided then defaults to today
		**CURRENTLY THROUGH A SUBMITTED FORM OR API**
		"""
		try:
			start_date = request.args['startDate']
			end_date = request.args['endDate']
			process = request.args['Process_Name']

		except:
			start_date = request.form["startDate"]
			end_date = request.form["endDate"]
			process = request.form['Process_Name']
		
		if len(start_date) < 1:
			start_date = self.yesterday
		if len(end_date) < 1:
			end_date = self.tomorrow

		where_clause = f"Date_Logged BETWEEN '{start_date}' AND '{end_date}'"

		if process != "ALL":
			where_clause += f"AND Process_Id = '{self.process_table.get_process_id(process)}'"

		query = f"""
		SELECT *
		FROM rpa.Process_Detail
		WHERE {where_clause}
		ORDER BY Date_Logged desc
		"""
		df = table.Read(query)
		print(df)
		data = df.to_dict('records')
		return jsonify(data)

	def patch(self):
		"""
		returns all data from every month
		"""
		df = pd.DataFrame(columns=['month_data', 'month_data_completed', 'month_data_uncompleted'])

		year = datetime.now().year

		month_to_month_data = []
		month_to_month_data_completed = []
		month_to_month_data_uncompleted = []
		month = 1
		while month <= 12:
			query = f"""
			SELECT DISTINCT Process_Detail_Identifier, Process_Detail_Status
			FROM rpa.Process_Detail with (nolock)
			WHERE month(Date_Logged) = {month} AND YEAR(Date_Logged) = {year}
			"""
			completions = table.Read(query)
			print(completions)
			completions = list(completions['Process_Detail_Status'])
			completed = completions.count("S")
			#uncompleted = completions.count("I")//3
			total = len(completions)
			uncompleted = total - completed
			month_to_month_data.append(total)
			month_to_month_data_completed.append(completed)
			month_to_month_data_uncompleted.append(uncompleted)

			month += 1

	
		df['month_data'] = month_to_month_data
		df['month_data_completed'] = month_to_month_data_completed
		df['month_data_uncompleted'] = month_to_month_data_uncompleted
		monthly_data = df.to_dict('records')
		print(df)
		return jsonify(monthly_data)

	def put(self):
		"""
		Returns data from the entire week and last week
		"""
		today = datetime.now()
		# print(today.weekday())
		previous_monday = today - timedelta(days=today.weekday())
		current_date = previous_monday

		month = today.month
		year = today.year

		weekly_completions_df = pd.DataFrame(columns=['LastWeek_Monday', 'LastWeek_Tuesday', 'LastWeek_Wednesday', 'LastWeek_Thursday', 'LastWeek_Friday', 'LastWeek_Saturday', 'LastWeek_Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
		weekly_savings_df = pd.DataFrame(columns=['LastWeek_Monday_Savings', 'LastWeek_Tuesday_Savings', 'LastWeek_Wednesday_Savings', 'LastWeek_Thursday_Savings', 'LastWeek_Friday_Savings', 'LastWeek_Saturday_Savings', 'LastWeek_Sunday_Savings', 'Monday_Savings', 'Tuesday_Savings', 'Wednesday_Savings', 'Thursday_Savings', 'Friday_Savings', 'Saturday_Savings', 'Sunday_Savings'])

		current_date += timedelta(days=-7)
		for counter in range(14):
			day = current_date.day
			month = current_date.month
			year = current_date.year
			
			#query to find weekly completions
			query = f"""
			SELECT DISTINCT Process_Detail_Identifier, Process_Detail_Status
			FROM rpa.Process_Detail with (nolock)
			WHERE Process_Detail_Status = 'S' and day(Date_Logged) = {day} and month(Date_Logged) = {month} and YEAR(Date_Logged) = {year}
			"""
			df = table.Read(query)
			bp_query = f"""
			SELECT DISTINCT keyvalue
			FROM dbo.BPAWorkQueueItem with (nolock)
			WHERE status = 'Completed' and DAY(completed) = {day} and MONTH(completed) = {month} and YEAR(completed) = {year}
			"""
			bp_df = bp_table.db_connection.Read(bp_query)
			weekly_completions_df.at[0,f"{WEEKDAYS[counter]}"] = len(list(df['Process_Detail_Status'])) + len(list(bp_df['keyvalue']))

			#query to find hours taken on jobs per week
			query = f"""
			select SUM(DATEDIFF(HOUR, Start_Time, End_Time)) AS Hours_taken from rpa.Process_Run
			WHERE day(Start_Time) = {day} and month(Start_Time) = {month} and YEAR(Start_Time) = {year} and end_time is not NULL and Process_Id not in (57)
			"""
			df = table.Read(query)
			bp_query = f"""
			select SUM(worktime) as Seconds_taken
			FROM dbo.BPAWorkQueueItem
			WHERE status = 'Completed' and day(completed) = {day} and month(completed) = {month} and year(completed) = {year}
			"""
			bp_df = bp_table.db_connection.Read(bp_query)

			hours = list(df['Hours_taken'])[0]
			bp_hours = list(bp_df['Seconds_taken'])[0]
			if bp_hours:
				bp_hours = (bp_hours/60)/60
			else:
				bp_hours = 0
			if not hours:
				hours = 0
			weekly_savings_df.at[0, f"{WEEKDAYS[counter]}_Savings"] = hours + int(bp_hours)

			current_date += timedelta(days=1)

		weekly_data = pd.concat([weekly_completions_df, weekly_savings_df], axis=1)
		weekly_data = weekly_data.to_dict('records')
		return jsonify(weekly_data)



@blueprint.route("/dashboard")
def dash():
	if not session.get("user"):
		return redirect(url_for('authentication_blueprint.login'))

	distinct_processes = table.Read("select Distinct process_name from rpa.Process order by Process_Name ASC")
	distinct_processes = list(distinct_processes['process_name'])

	return make_response(render_template("process_table.html", process_names=distinct_processes))
"""
class Dashboard(Resource):
	"
	Return HTML Page
	**CURRENTLY NOT FORCING A LOGIN**
	"
	def __init__(self):

		self.distinct_processes = table.Read("select Distinct process_name from rpa.Process")
		self.distinct_processes = list(self.distinct_processes['process_name'])

	def get(self):
		
		return make_response(render_template("Dashboard.html", process_names=self.distinct_processes))

	def post(self):
		"
		Post call for dashboard, this will return selected process and its data based on dates
		"
		return make_response(render_template("Dashboard.html", process_names=self.distinct_processes))
"""
class getTSA(Resource):
	def __init__(self):
		#init table
		self.table = tsa_table
		#init columns
		self.cols = ["convert (varchar(20) , [Event_Date]) as Event_Date", "LOWER(Event_Type) as Event_Type", "Event_XML", "LOWER(Schema_Name) as Schema_Name", "LOWER(Object_Name) as Object_Name", "Host_Name", "IPAddress", "Program_Name", "Login_Name"]
		self.columns = ["Event_Date", "Event_Type", "Event_XML", "Schema_Name", "Object_Name", "Host_Name", "IPAddress", "Program_Name", "Login_Name"]
		#init select string 
		self.select_string = ""
		for index, value in enumerate(self.cols):
			if index == 0:
				self.select_string += f"{value}"
			else:
				self.select_string += f", {value}"

		#create timestamp
		timestamp = self.table.create_timestamp()
		self.date, self.time = timestamp.split(" ")
		#create stamp for yesterday
		datetime_object = datetime.strptime(self.date, '%Y-%m-%d').date()
		self.yesterday =  str((datetime_object - timedelta(days=1)))
		self.tomorrow =  str((datetime_object + timedelta(days=1)))

	def get(self):
		where_clause = f"Event_Date BETWEEN '{self.yesterday}' AND '{self.tomorrow}'"
		query = f"""
        SELECT {self.select_string}
        FROM [tsa].[Database_DDL_Audit]
        WHERE {where_clause}
		order by event_date desc
        """
		print(query)

		df = self.table.Read(query)
		df = self.format_xml(df)
		print(df)

		data = df.to_dict('records')
		return jsonify(data)

	def post(self):
		#data = {'event':event, 'schema':schema, 'start':start, 'end':end}

		event = request.form["eventType"]
		schema = request.form["SchemaName"]
		start = request.form["startDate"]
		end = request.form["endDate"]
		db = request.form["database"]
		self.table = RPATable("tsa", "Database_DDL_Audit", config_path=db)

		if len(start) < 1:
			start = self.yesterday
		if len(end) < 1:
			end = self.tomorrow
		
		where_clause = f"Event_Date BETWEEN '{start}' AND '{end}'"

		if schema != "ANY":
			where_clause += f" AND Schema_Name = '{schema}'"

		if event != "ANY":
			where_clause += f" AND Event_Type = '{event}'"

		query = f"""
        SELECT {self.select_string}
        FROM [tsa].[Database_DDL_Audit]
        WHERE {where_clause}
		order by event_date desc
        """
		print(query)

		df = self.table.Read(query)
		df = self.format_xml(df)
		if df.size == 0:
			no_records = ["No Records to show" for x in self.columns]
			df.loc[len(df)] = no_records
		print(df)
		data = df.to_dict('records')
		return jsonify(data)

	def format_xml(self, df):
		new_xml = []
		for index, element in enumerate(df['Event_XML']):
			bs = BeautifulSoup(element, 'xml')
			command_text = bs.find_all('CommandText')
			#element = bs.prettify()
			new_xml.append(str(command_text))
		df['Event_XML'] = new_xml
		return df

@blueprint.route('/tsa')
def index():
	event_types = list(table.Read("select distinct Event_Type from tsa.Database_DDL_Audit order by Event_Type ASC")['Event_Type'])
	schema_names = list(table.Read("select distinct Schema_Name from tsa.Database_DDL_Audit order by Schema_Name ASC")['Schema_Name'])
	
	print(event_types)

	if not session.get("user"):
		return redirect(url_for('authentication_blueprint.login'))
		
	if session.get('user')['preferred_username'].lower() not in ADMIN or session.get('user')['preferred_username'].lower() not in TSA_USERS:
		return render_template('home/page-403.html'), 403

	return make_response(render_template("TSA.html", event_types=event_types, schema_names=schema_names))

class TSADash(Resource):
	def get(self):
		if not session.get("user"):
			return redirect(url_for('authentication_blueprint.login'))
		print("LOGGED IN")
		return make_response(render_template("TSA.html"))

	def post(self):
		return make_response(render_template("TSA.html"))


def convert_from_utc_to_est(utc_time):
	"""
	Expects UTC time as string in form : YYYY-MM-DD HH:MM:SS
	"""
	date, time = utc_time.split(" ")
	year, month, day = date.split("-")
	hour, minute, second = time.split(":")
	year, month, day, hour, minute, second = int(year), int(month), int(day), int(hour), int(minute), int(second)
	# utc_time = datetime.strptime(date_object, '%Y-%m-%d %H:%M:%S')
	timestamp_utc = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
	est = pytz.timezone('US/Eastern')
	est_time = timestamp_utc.astimezone(est)
	est_time = est_time.strftime('%Y-%m-%d %H:%M:%S')
	est_time = datetime.strptime(est_time, '%Y-%m-%d %H:%M:%S')

	return est_time
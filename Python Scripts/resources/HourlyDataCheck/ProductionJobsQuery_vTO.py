import os
import pandas as pd
import pyodbc
import struct
import time
from datetime import datetime, timedelta, timezone
import pytz
from ProductionJobsFunctions import di_error_calculations, spotio_calculations, ProductionJobQueries, ProductionJobColumns, ProductionJobParams, errors, error_summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
sys.path.append(os.environ['autobot_modules'])
from BotUpdate.ProcessTable import RPA_Process_Table
from AutobotEmail.PAEmail import PowerAutomateEmail
from BotUpdate.dbconnection import connection

bot_name = "DI Job Error Log - idk"
print('Connecting to database')
sql_connection = connection("PROD")
bot_update = RPA_Process_Table()
print('Connected to database')


'''
Collect Query results and store into a pandas database
    - Prod
    - Wolf
    - Roof
    - TSA
    - Errors (Production + Geo)
    - Geo_Error
    - Metadata
    - Spotio_Feed_Data
    - Spotio Knocks
    - Spotio First Knocks
'''
weekend = [5,6]
sleeper = False
while True:
    day_of_week = int(datetime.today().weekday())
    current_hour = datetime.now(pytz.timezone('America/New_York')).hour

    if current_hour >= 9 or current_hour <= 17:
        receiver_email = [
                "tejakarri@trinity-solar.com",
                "Jean.Fleurmond@trinity-solar.com",
                "Anusha.Siddaramanna@trinity-solar.com",
                "manu.goyal@trinity-solar.com",
                "john.veneziano@trinity-solar.com"
            ]
    else:
        receiver_email = [
            "powerautomateteam@trinity-solar.com"
        ]

    if day_of_week in weekend:
        print("Today is a weekend, script will not run.. Sleeping for an hour")
        bot_update.update_status(bot_name)
        time.sleep(360)
    else:
        try:
            bot_update.register_bot(bot_name)
            bot_update.update_status(bot_name)

            sleep_count = 0
            run_time = datetime.now(pytz.timezone('America/New_York')) # Get current timestamp 
            print(f"Currently Running: {run_time}")
            bot_update.update_bot_status(bot_name, "Starting", run_time)

            pj_result = {}
            for q in ProductionJobQueries: #range(len(ProductionJobQueries)):
    
                print('Running Script for: ', q)
                #sql_connection.execute(ProductionJobQueries[q])
                query_result = sql_connection.Fetch(ProductionJobQueries[q], True)
                print('Successfully Completed Query')
    
                #query_result = cursor.fetchall() # Execute the resultp
                query_result_len = len(query_result) # Obtain Length of Result length
 
                # Collect all of the results
                row_result = []
                for row in query_result:
                    row_result.append(row)
   
                # Append the row results to the query
                pj_result[q] = pd.DataFrame.from_records(row_result, columns=ProductionJobColumns[q][0])
    
                # If a job needs a time difference calculate it as a new column "Runtime_Diff" in Hours
                if not pj_result[q].empty and ProductionJobColumns[q][1]:
                    #pj_result[q]['Runtime_Diff'] = pj_result[q].apply(lambda row: (run_time - row[ProductionJobColumns[q][1]]).seconds/3600, axis=1)
                    pj_result[q]['Runtime_Diff'] = pj_result[q].apply(lambda row: (run_time - row[ProductionJobColumns[q][1]].tz_convert(tz='America/New_York')).seconds/3600, axis=1)
                    #pj_result[q]['Runtime_Diff'] = pj_result[q].apply(lambda row: (run_time - pj_result[q].tz_convert(row[ProductionJobColumns[q][1]],tz='EST')).seconds/3600, axis=1)
                    pj_result[q]['Runtime_Diff_Days'] = pj_result[q].apply(lambda row: (run_time - row[ProductionJobColumns[q][1]].tz_convert(tz='America/New_York')).days, axis=1)
        
            # Close all connections and cursor values
            #cursor.close()
            #cnxn.close()
            print('Completed Collecting Query Data')
            bot_update.update_bot_status(bot_name, "Completed Collecting Data", run_time)

            # Store all data into CSV files
            #FILE_PATH = os.path.dirname(os.path.abspath(__file__))
            #FILE_PATH += "\query_data"
            #if not os.path.exists(FILE_PATH): # If Path does not exist
            #    os.makedirs(FILE_PATH)
    
            #for e in pj_result:
            #    FILE_NAME = FILE_PATH + f"\{e}.csv"
            #    if os.path.isfile(FILE_NAME): # If the file exists
            #        pj_result[e].to_csv(FILE_NAME, mode='a', header=False)
            #    else: # If the file does not exist then make the entry with the headers
            #        pj_result[e].to_csv(FILE_NAME, mode='a', header=True)

            '''
            Find Errors
            '''
            run_errors = errors
            run_errors_summary = error_summary
            run_errors = di_error_calculations(pj_result, ProductionJobColumns, ProductionJobParams, run_errors, run_errors_summary)
            run_errors = spotio_calculations(pj_result, ProductionJobParams, run_errors, run_errors_summary) # Find errors in Spotio

            '''
            Send Email Showing Hourly Status
            '''
            bot_update.update_bot_status(bot_name, "Sending Email", run_time)

            prod_status_html = ''
            error_summary_html = ''
            for e in run_errors:
                li_open = '<li class="tg-text">'
                li_close = '</li>\n'
    
                # Generate code for opening and details
                open_cell = '<tr>\n'
                close_cell = '</tr>\n'
                job = '\t<td class="tg-text">' + e + '</td>\n'
                if not run_errors[e].empty: # If there is an error
                    # Production Job Details
                    status = '\t<td class="tg-bad"></td>\n'
                    details = '\t<td class="tg-text">' + run_errors[e].to_html()  + '</td>\n'
                    prod_status_html += open_cell + job + status + details + close_cell
        
                    # Production Job Summary
                    for idx in range(len(error_summary[e])):
                        error_summary_html += li_open + error_summary[e][idx] + li_close
        
                else:
                    status = '\t<td class="tg-good"></td>\n'
                    details = ''
                    if e not in ('Spotio_Feed_Data', 'Spotio_Knocks', 'Prod_Error', 'Geo_Error') and ProductionJobColumns[e][1]:
                        timestamp_max = pj_result[e][ProductionJobColumns[e][1]].max().strftime("%H:%M:%S")
                        timestamp_min = pj_result[e][ProductionJobColumns[e][1]].min().strftime("%H:%M:%S")
                        details = '\t<td class="tg-text">' + 'Earliest Run Timestamp: {}&emsp;&emsp;Last Run Timestamp: {}'.format(timestamp_min, timestamp_max) + '</td>\n'
                    elif e == 'Spotio_Feed_Data':
                        yesterday_day = pj_result[e]['ActivityDate'][0].date()
                        daybefore_day = pj_result[e]['ActivityDate'][1].date()
                        yesterday_count = pj_result[e]['Count'][0]
                        daybefore_count = pj_result[e]['Count'][1]
                        details = '\t<td class="tg-text">' + 'Date: {}&ensp;Count: {}&emsp;&emsp;Date: {}&ensp;Count: {}'.format(daybefore_day, daybefore_count, yesterday_day, yesterday_count) + '</td>\n'
                    elif e == 'Spotio_Knocks':
                        first_knock_activity_feed_id = pj_result['Spotio_First_Knocks']['FK_ActivityFeedId'][0]
                        current_activity_feed_id = pj_result['Spotio_Knocks']['ActivityFeedId'][0]
                        details = '\t<td class="tg-text">' + 'First Knocks Activity Feed Id: {}&emsp;&emsp;Spotio Activity Feed id: {}'.format(first_knock_activity_feed_id, current_activity_feed_id) + '</td>\n'
                    else:
                        details = '\t<td class="tg-text">No Errors</td>'
                    prod_status_html += open_cell + job + status + details + close_cell
            error_summary_html = '<ul>\n' + error_summary_html + '</ul>\n'

            print('Preparing message!')

            html = """
            <style type="text/css">
            .tg  {border-collapse:collapse;border-spacing:0;}
            .tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
                overflow:hidden;padding:10px 5px;word-break:normal;}
            .tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
                font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
            .tg .tg-text{font-family:inherit;font-size:14px;text-align:center;vertical-align:top}
            .tg .tg-header{font-family:inherit;font-size:16px;font-weight:bold;text-align:center;vertical-align:top}
            .tg .tg-good{background-color:#00ff00;font-family:inherit;font-size:16px;text-align:center;vertical-align:top}
            .tg .tg-bad{background-color:#ff0000;font-family:inherit;font-size:16px;text-align:center;vertical-align:top}
            </style>

            <body>
            <h1 class="tg-header">Error Summary - TIME COMPARISON ONLY</h1>
            """ + error_summary_html + """
            </body>
            <table class="tg">
            <thead>
                <tr>
                <th class="tg-header">Production Job</th>
                <th class="tg-header">Status</th>
                <th class="tg-header">Details</th>
                </tr>
            </thead>
            <tbody>""" + prod_status_html + """
            </tbody>
            </table>
            """
            
            

            #mailserver.sendmail(sender_email, receiver_email, message.as_string())
            PowerAutomateEmail.send(path=None, email_subject=f'Production Job Test -- {run_time.strftime("%m/%d/%Y  %H:%M:%S")}', text=html,email_recipient=receiver_email, ccs=['avigoyal@trinity-solar.com'])
            print('Production Job Status Email Sent!')
            bot_update.complete_opportunity(bot_name, run_time)
            bot_update.edit_end()
            sleeper = True
            time.sleep(60)
            while sleeper:
                minute = datetime.now(pytz.timezone('America/New_York')).minute
                if minute == 58:
                    sleeper = False
                else:
                    print(f"Sleeping until 58th minute of the hour, currently at: {minute}")
                    time.sleep(60)
        except Exception as e:
            print(e)
            quit()
            PowerAutomateEmail.send(path=None, email_subject=f'Error with Production Job Check - {run_time.strftime("%m/%d/%Y  %H:%M:%S")}', text=f"Error information from python: {e}",email_recipient=receiver_email, ccs=['avigoyal@trinity-solar.com'])
            print('Error message sent')
            break

# Path for the file of addresses excel file




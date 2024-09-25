
import sys
import os
from Sitecapture_Project_Creation import SiteCaptureProjectCreation
# sys.path.append(r"C:\Users\RPA_Bot_12\Desktop\Sharepoint\contractcreation")
from Project_log_parser import ReadSiteCapExcel
import time
import datetime
sys.path.append(os.environ['autobot_modules'])
from AutobotEmail.PAEmail import PowerAutomateEmail
# import schedule
from datetime import datetime as dt

class clock():
    def __init__(self):
        self.nothing = True
        sleeper = False
        argument = False
        # start_time = dt.today()
        # with open(r"C:\Users\RPA_Bot_12\Desktop\Logs.txt", 'a') as f:
        #     f.write(f"START TIME: {start_time}, ")
        #     f.close()
        try:
            argument = sys.argv[1]
        except:
            print("no additional argument")
            pass
        # report = SiteCaptureRequests()
        # today_int = int(datetime.today().weekday())
        # today_weekday = report.weekdays[report.today_int]
        print("made the init")
        # try:
        if argument == "manual":
            report = SiteCaptureProjectCreation()
            report.run_manual()
            quit()
        
        elif argument == "creation":
            while True:
                try:
                    count = 0
                    report = SiteCaptureProjectCreation()
                    # report.register_bot()
                    start_time = dt.today()

                    with open(r"C:\Users\RPA_Bot_12\Desktop\Logs.txt", 'a') as f:
                        f.write(f"START TIME: {start_time}, ")
                        f.close()
                    
                    today_weekday = report.weekdays[report.today_int]
                    print(today_weekday)
                    if today_weekday == "Thursday" or today_weekday == "Friday" or today_weekday == "Wednesday":
                                # print("??")
                        report.run_weekend()
                    
                    report.run()

                    end_time = dt.today()
                    with open(r"C:\Users\RPA_Bot_12\Desktop\Logs.txt", 'a') as f:
                        f.write(f"END TIME: {end_time} \n")
                        f.close()
                    sleeper = True
                    # count = 0

                    while sleeper == True: 
                        print(f"Sleeping for 60 seconds until an hour passed, count: {count}, once count has reached 60 the process will continue")
                        report.update_status(report.function, "Waiting")
                        time.sleep(60)
                        # report.
                        count += 1
                        if count == 30:
                            sleeper = False
                except Exception as e:
                    sleeper = True
                    print(f"Encountered an error.. {e}")

        elif argument == "uploader":
            report = SiteCaptureProjectCreation()
            
            while True:
                count = 0
                poster = ReadSiteCapExcel()
                poster.run()
                sleeper = True
                    # count = 0

                while sleeper == True: 
                    print(f"Sleeping for 60 seconds until an hour passed, count: {count}, once count has reached 60 the process will continue")
                    report.update_status(poster.bot_name, "Waiting")
                    time.sleep(60)
                    # report.
                    count += 1
                    if count == 30:
                        sleeper = False

        else:
            while True:
                try:
                    # report = SiteCaptureRequests()
                    count = 0
                    if sleeper == False:
                        text = f"""\
                        Hello,
                        The Sitecapture bot is starting...
                            """
                        html = f"""\
                        <html>
                            <body>
                                <p>
                                Hello,<br>
                                The Sitecapture bot is starting...<br>
                                </p>
                            </body>
                        </html>
                                """
                        # PowerAutomateEmail.send(email_subject="Sitecapture bot starting...", text=text, html=html)
                        report = SiteCaptureProjectCreation()
                        # report.register_bot()
                        start_time = dt.today()

                        with open(r"C:\Users\RPA_Bot_12\Desktop\Logs.txt", 'a') as f:
                            f.write(f"START TIME: {start_time}, ")
                            f.close()
                    
                        today_weekday = report.weekdays[report.today_int]
                        print(today_weekday)
                        if today_weekday == "Thursday" or today_weekday == "Friday" or today_weekday == "Wednesday":
                            # print("??")
                            report.run_weekend()
                        # print(f"Starting Process {sys.argv[1]}")
                        # report = SiteCaptureRequests()
                            print("?")
                        
                        report.run()
                        poster = ReadSiteCapExcel()
                        poster.run()
                    
                        #pull the refreshed excel sheet
                        report.sharepoint.connect()
                        report.run()
                        end_time = dt.today()
                        with open(r"C:\Users\RPA_Bot_12\Desktop\Logs.txt", 'a') as f:
                            f.write(f"END TIME: {end_time} \n")
                            f.close()
                        sleeper = True
                        # count = 0
                    while sleeper == True: 
                        print(f"Sleeping for 60 seconds until an hour passed, count: {count}, once count has reached 60 the process will continue")
                        report.update_status(report.function, "Waiting")
                        time.sleep(60)
                        # report.
                        count += 1
                        if count == 30:
                            sleeper = False
                except Exception as e:
                    print(e)
                    print("Error while running script.. waiting to retry")
                    sleeper = True
        # except KeyError:
        #     # print("QUITTING")
        #     sleeper = True

if __name__ == "__main__":
    a = clock()
    # a.clock()
    # schedule.every(1).minute.do(a.report(), r"C:\Users\AviGoyal\Desktop\PythonCode\RPA-491-501-Connect\report_clock.py")

    # while True:
    #     schedule.run_pending()
    #     print("Sleeping...")
    #     time.sleep(5)
    # a.run()
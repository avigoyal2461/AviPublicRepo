from run_reportV2 import SunnovaReports
# from SunnovaPortal import SunnovaPortal
# from run_report import SunnovaReports
import sys
import time
#python **NAME OF THIS FILE** **ARGUMENT**
#python report_clock.py Contract_Document_Download
class clock():
    def __init__(self):
        self.nothing = True
        sleeper = False
        report = SunnovaReports()
        # print("made the init")
        # try:
        while True:
            try:
                count = 0
                if sleeper == False:
                    print(f"Starting Process {sys.argv[1]}")
                    report.run()
                    sleeper = True
                    # count = 0
                while sleeper == True: 
                    print(f"Sleeping for 60 seconds until an hour passed, count: {count}, once count has reached 60 the process will continue")
                    time.sleep(60)
                    count += 1
                    if count == 60:
                        sleeper = False
            except Exception as e:
                print(e)
                report.sunnova.close()
                # SunnovaReports().sunnova.close()
                print("Error while running script.. watiing to retry")
                sleeper = True
        # except KeyError:
        #     # print("QUITTING")
        #     sleeper = True

if __name__ == "__main__":
    a = clock()
    # a.run()
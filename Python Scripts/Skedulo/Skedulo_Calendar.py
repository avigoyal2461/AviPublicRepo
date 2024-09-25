#pip install pandas, openpyxl
#xlrd, python -m pip install -U pip setuptools
import pandas as pd
import os
import sys
import openpyxl
#from openpyxl import Workbook
#from openpyxl import load_workbook
import time
import glob
from datetime import datetime
sys.path.append(os.environ['autobot_modules'])
from Sharepoint.connection import SharepointConnection 
from SalesforceAPI import SalesforceAPI
from BotUpdate.ProcessTable import RPA_Process_Table
from AutobotEmail.PAEmail import PowerAutomateEmail
from customlogging import logger

class Skedulo():
    """
    Schedule updater, this class was made to parse through an excel sheet
    with multiple regions, the objective is to find which rep works which shift
    and input them all into a parsable list
    Everything is stored in dictionary, this will use salesforce API in order to add shifts to users
    """
    def __init__(self): 
        logger.info("Starting Skedulo bot...")
        self.name = "Skedulo Calendar Updates"
        self.bot_update = RPA_Process_Table()
        self.bot_update.register_bot(self.name)

        self.sf_item = SalesforceAPI()

        DOWNLOAD_PATH = os.path.dirname(os.path.abspath(__file__))
        self.sheet_name = "Corporate Sales Calendar.xlsx"
        #self.sheet_name = "Corporate Sales Calendar - 2 Weeks.xlsx"

        logger.info("Downloading file...")
        self.sharepoint = SharepointConnection()
        self.sharepoint.url = "https://trinitysolarsys.sharepoint.com/teams/BTIntranet"
        self.sharepoint.relative_url = "/teams/BTIntranet/Shared%20Documents/"
        self.sharepoint.getFile(path=fr"{DOWNLOAD_PATH}/{self.sheet_name}", folder="Corporate%20Sales%20Calendar", file=self.sheet_name)
        
        today = datetime.today()
        tday = today.strftime ("%m-%d-%Y")
        m, d, y = tday.split("-")
        self.sharepoint.uploadFile(path=fr"{DOWNLOAD_PATH}/{self.sheet_name}", folder="Corporate%20Sales%20Calendar/Previous%20Calendars", file=fr"{m}-{d}-{y}_{self.sheet_name}")

        files = glob.glob(f"{DOWNLOAD_PATH}/*.xlsx")
        if isinstance(files, list):
            self.excel_location = fr"{files[0]}"
        else:
            self.excel_location = fr"{files}"
            
        #Each shift has a designated name, hash, weekday, start and end time
        #Hash: created in skedulo, these are static after creation but can be the cause of error if it is incorrect, hashs can not be created in SF, sending a hash that was created by SF will not create shifts in skedulo
        #id: this is the avail pattern ID that we will create every time we run using the hash, this will be assigned the the users 
        #users: users that will be assigned shifts for the two weeks
        #start: Pattern start time
        #end: Pattern end time
        #shift_start: 4 hours behind start time -> Due to how salesforce recognizes the timestamp we send.
        #shift_end: 4 hours behind end time
        self.shifts = {
            'Shift 1 - Monday': {'hash':'9988d2998506e80df3894f190ca25210', 'weekday': 'MON', 'start': '10:00', 'end': '16:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 2 - Monday': {'hash':'1793be80a22f643e3d0c45b940ecd571', 'weekday': 'MON', 'start': '13:00', 'end': '19:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 3 - Monday': {'hash':'3199e2f8d1f71a81c43fc6189925782c', 'weekday': 'MON', 'start': '16:00', 'end': '22:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 1 - Tuesday': {'hash':'363f458bc18378086731f6a9c754f5b2', 'weekday': 'TUE', 'start': '10:00', 'end': '16:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 2 - Tuesday': {'hash':'1e7fed2d3a614aa9ef3110018eeda064', 'weekday': 'TUE', 'start': '13:00', 'end': '19:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 3 - Tuesday': {'hash':'6c43ff556a6b72bc57166f5225240dd1', 'weekday': 'TUE', 'start': '16:00', 'end': '22:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 1 - Wednesday': {'hash':'41eda9b69797e0245634fe7e633865d0', 'weekday': 'WED', 'start': '10:00', 'end': '16:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 2 - Wednesday': {'hash':'7666efe7efc96594df79c3c76dd933e3', 'weekday': 'WED', 'start': '13:00', 'end': '19:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 3 - Wednesday': {'hash':'f97eea23f02aa4343294b34f6a78c011', 'weekday': 'WED', 'start': '16:00', 'end': '22:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 1 - Thursday': {'hash':'948e3168bcfc1827240df6dc05ad5715', 'weekday': 'THU', 'start': '10:00', 'end': '16:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 2 - Thursday': {'hash':'cc4626e0735a298f086671db464c7421', 'weekday': 'THU', 'start': '13:00', 'end': '19:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 3 - Thursday': {'hash':'eca08c1e8949da11e5c8641b02acae2b', 'weekday': 'THU', 'start': '16:00', 'end': '22:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 1 - Friday': {'hash':'2de63c93babd54668e25d0d753518178', 'weekday': 'FRI', 'start': '10:00', 'end': '16:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 2 - Friday': {'hash':'b93137c9ab752cfd1a81b4f2e5d0f52c', 'weekday': 'FRI', 'start': '13:00', 'end': '19:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 3 - Friday': {'hash':'077900e4eb1cf70eaffb327a32cdb0a8', 'weekday': 'FRI', 'start': '16:00', 'end': '22:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 1 - Saturday': {'hash':'bef50d967af067f8d1be270fca8ffb92', 'weekday': 'SAT', 'start': '09:00', 'end': '15:00', 'id': "", 'users_week_one': [],'users_week_two': []},
            'Shift 2 - Saturday': {'hash':'ccad0a1f30bed1712c6c9988f7bb85d0', 'weekday': 'SAT', 'start': '13:00', 'end': '20:00', 'id': "", 'users_week_one': [],'users_week_two': []}
        }
        #basic variables used in various methods
        self.weeks = ['week_one', 'week_two'] #used in pattern_creator method to signify which weeks to create the pattern For
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] #used in shift_creator method to signify which days each users are a part of

        #create a template for nextweek sunday's date, the date we are passing as the start of each shift, along with sunday from 2 weeks from now for the end date
        #No Longer in use
        """
        #self.nextweek_sunday = "2023-07-23"
        #self.twoweek_sunday = "2023-08-06"
        self.next_sunday = self.create_date_using_template(NEXT_SUNDAY_TEMPLATE)
        self.week_one_sunday = self.create_date_using_template(ONEWEEK_SUNDAY_TEMPLATE)
        self.week_two_sunday = self.create_date_using_template(TWOWEEK_SUNDAY_TEMPLATE)
        self.week_three_sunday = self.create_date_using_template(THREEWEEK_SUNDAY_TEMPLATE)
        #print(f"Next Sunday = {self.next_sunday}")
        """

        self.xl = pd.ExcelFile(self.excel_location)
        #Pull the dates from the Variable sheet in the excel. Those dates are set for Monday to Monday - Skedulo requires Sunday to Sunday so we subtract a day.
        #Week three is the final end date of the shifts, this will be extrapolated from the end week of week two + 6 to get to the final Sunday.
        variables = self.xl.parse("Volume Variables")
        columns = variables.columns.tolist()
        week_one = (variables[columns[0]].iloc[9] + pd.DateOffset(days = -1)).strftime("%Y-%m-%d")
        week_two = (variables[columns[0]].iloc[10] + pd.DateOffset(days = -1)).strftime("%Y-%m-%d")
        week_three = (variables[columns[0]].iloc[10] + pd.DateOffset(days = 6)).strftime("%Y-%m-%d")
 
        print(f"First week of uploads is {week_one}")
        print(f"Second week of uploads is {week_two}")
        print(f"Final End date is {week_three}")

        self.shift_start_and_end = {
            'week_one' : {'start': week_one, 'end': week_two},
            'week_two' : {'start': week_two, 'end': week_three}
        }

    def run(self):
        """
        Pulls helper methods together and runs the calendar update from start to finish
        """
        
        PowerAutomateEmail.send(path=None, email_subject="Weekly Skedulo Updates", text=f"Skedulo started updating for the week of {self.shift_start_and_end['week_one']['start']} to {self.shift_start_and_end['week_two']['end']}", email_recipient=["avigoyal@trinity-solar.com",
        "jeff.macdonald@trinitysolarsystems.com",
        "Debashish.Mukherjee@trinity-solar.com",
        "Bryan.Bigica@trinitysolarsystems.com",
        "Pahan.mahakumara@trinity-solar.com"
        ], ccs=['tim.higgins@trinity-solar.com', 'josh.beach@trinity-solar.com'])
        
        logger.info("Creating Shift Patterns")
        #create shift patterns
        self.pattern_creator()
        
        logger.info("Reading Excel Sheet")
        #pull users from excel and populate dictionary
        self.excel_reader()

        logger.info("Creating Shifts in Skedulo")
        #create shifts in salesforce/skedulo
        self.shift_creator()

        
        PowerAutomateEmail.send(path=None, email_subject="Weekly Skedulo Updates", text=f"Skedulo Finished updating calendars for the week of {self.shift_start_and_end['week_one']['start']} to {self.shift_start_and_end['week_two']['end']}", email_recipient=["avigoyal@trinity-solar.com",
        "jeff.macdonald@trinitysolarsystems.com",
        "Debashish.Mukherjee@trinity-solar.com",
        "Bryan.Bigica@trinitysolarsystems.com",
        "Pahan.mahakumara@trinity-solar.com"
        ], ccs=['tim.higgins@trinity-solar.com', 'josh.beach@trinity-solar.com'])
        
        os.remove(self.excel_location)
        logger.info("Process Complete")
        
        return True

    def excel_reader(self):
        """
        Reads the calendar and parses through all opps to create detailed lists for everyone
        For overbooking : We will iterate then convert their name to user_id to continue
        """
        cols = ['Resource_Name', 'User_ID', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        overbooking_cols = ['State', 'Skedulo_Region', 'Resource_Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        #xl = pd.ExcelFile(self.excel_location)
        sales_df_week_one = self.xl.parse("Sales Sweep 1")
        #overbooking_df_week_one = self.xl.parse("Overbooking Sweep 1")

        sales_df_week_two = self.xl.parse("Sales Sweep 2")
        #overbooking_df_week_two = self.xl.parse("Overbooking Sweep 2")
        
        #Set columns 
        sales_df_week_one.columns = cols
        sales_df_week_two.columns = cols
        #overbooking_df_week_one.columns = overbooking_cols
        #overbooking_df_week_two.columns = overbooking_cols

        #parse through regular sheet
        for week in self.weeks:
            for row_counter, row in enumerate(eval(f"sales_df_{week}.values")):
                # print(row)
                name = eval(f"sales_df_{week}['Resource_Name'].loc[{row_counter}]")
                user_id = eval(f"sales_df_{week}['User_ID'].loc[{row_counter}]")
                Monday = eval(f"sales_df_{week}['Monday'].loc[{row_counter}]")
                Tuesday = eval(f"sales_df_{week}['Tuesday'].loc[{row_counter}]")
                Wednesday = eval(f"sales_df_{week}['Wednesday'].loc[{row_counter}]")
                Thursday = eval(f"sales_df_{week}['Thursday'].loc[{row_counter}]")
                Friday = eval(f"sales_df_{week}['Friday'].loc[{row_counter}]")
                Saturday = eval(f"sales_df_{week}['Saturday'].loc[{row_counter}]")

                try:
                    df = self.sf_item.Select(query=f"select Id from sked__Resource__c where sked__UniqueKey__c = '{user_id}'")
                    user_id = list(df['Id'])[0]
                    self.shift_append(week, user_id, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday)

                    # print(f"Full user data {week} - {name}, ID: {user_id}, Shifts: {Monday}, {Tuesday}, {Wednesday}, {Thursday}, {Friday}, {Saturday}")

                except Exception as e:
                    self.bot_update.update_bot_status(self.name, f"Could not find resource ID in sf from opp id", user_id)
                    print(f"Could not find rep {name};")#{user_id}.. {e}")
                    continue
        """
        for week in self.weeks:
            for row_counter, row in enumerate(overbooking_df_week_one.values):
                # print(row)
                name = eval(f"overbooking_df_{week}['Resource_Name'].loc[{row_counter}]")
                Monday = eval(f"overbooking_df_{week}['Monday'].loc[{row_counter}]")
                Tuesday = eval(f"overbooking_df_{week}['Tuesday'].loc[{row_counter}]")
                Wednesday = eval(f"overbooking_df_{week}['Wednesday'].loc[{row_counter}]")
                Thursday = eval(f"overbooking_df_{week}['Thursday'].loc[{row_counter}]")
                Friday = eval(f"overbooking_df_{week}['Friday'].loc[{row_counter}]")
                Saturday = eval(f"overbooking_df_{week}['Saturday'].loc[{row_counter}]")

                try:
                    df = self.sf_item.Select(query=f"select Id from sked__Resource__c where Name = '{name}'")
                    user_id = list(df['Id'])[0]
                    self.shift_append(week, user_id, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday)

                    # print(f"Full user data - {name}, ID: {user_id}, Shifts: {Monday}, {Tuesday}, {Wednesday}, {Thursday}, {Friday}, {Saturday}")

                except Exception as e:
                    self.bot_update.update_bot_status(self.name, f"Could not find resource ID in sf from name", name)
                    print(f"Could not find overbooking rep {name}.. {e}")
                    continue
        """
 
    def shift_creator(self):
        """
        Takes all shifts from the shift lists and creates a pattern for each shift then adds to each user in the lists 
        This method will call after users have populated the dictionary
        daylight savings possible issue: 'sked__End__c': f"{self.shift_start_and_end[week]['end']}T020:59:59.000+0000", 'sked__Start__c': f"{self.shift_start_and_end[week]['start']}T012:00:00.000+0000"
        """
        #create patterns
        for item in self.shifts:
            for week in self.weeks:
                print(f"working on {item}, {week}")
                self.bot_update.register_bot(self.name, logs=f"In Queue: {item} {week}, {len(self.shifts[item][f'users_{week}'])}")
                for user in self.shifts[item][f'users_{week}']:
                    self.bot_update.update_bot_status(self.name, f"Creating Shift for user", user, create_duplicate=True)
                    data = {
                        'sked__End__c': f"{self.shift_start_and_end[week]['end']}T020:59:59.000+0000",
                        'sked__Start__c': f"{self.shift_start_and_end[week]['start']}T012:00:00.000+0000",
                        'sked__Availability_Pattern__c': self.shifts[item]['id'],
                        'sked__Resource__c': user
                     }
                    try:
                        updater = self.sf_item.Create("sked__Availability_Pattern_Resource__c", data)
                        if len(updater['errors']) > 0:
                            print("Returned an error")
                            self.bot_update.update_bot_status(self.name, f"Encountered error, {updater['errors']}", user)
                        else:
                            self.bot_update.complete_opportunity(self.name, user)
                            print(f"Successfully Added shift {item} for {week}")# for user {user}")

                    except Exception as e:
                        self.bot_update.update_bot_status(self.name, f"Failed to create shift for user", user)
                        print(f"ERROR: {e}, Could not create shift for {user}")
                #ends the process
                self.bot_update.edit_end()

    def pattern_creator(self):
        """
        Creates shift patterns and stores them in the self.shifts dictionary
        This method is important to call before shift_creator as this creates the patterns we use
        """
        self.bot_update.register_bot(self.name, logs=f"In Queue: Pattern Creation, 17")
        for item in self.shifts:
            pattern_data = {
            'Name': f'{item}',
            'sked__Pattern__c': '{"type":"weekly","days":[{"weekday":"' + f'{self.shifts[item]["weekday"]}' + '","intervals":[{"startTime":"' + f'{self.shifts[item]["start"]}' + '","endTime":"' + f'{self.shifts[item]["end"]}' + '"}]}],"repeatWeeks":1}',
            'sked__Hash__c': f'{self.shifts[item]["hash"]}'
            }
            #placed in a while true loop because if error is reached, expectation is because SF api failed, so lets retry until we can hit it - These ID's are vital to move forward
            while True:
                try:
                    creator = self.sf_item.Create('sked__Availability_Pattern__c', pattern_data)
                    break
                except Exception as e:
                    print(f"Hit an exception, {e}, retrying")
                    
            pattern_id = creator['id']
            self.bot_update.update_bot_status(self.name, f"Created Shift {item}", pattern_id)
            self.shifts[item]['id'] = pattern_id
            self.bot_update.complete_opportunity(self.name, pattern_id, update_string=f"{item}")

        self.bot_update.edit_end()

    def shift_append(self, week, user_id, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday):
        """
        Takes all shift data and inputs into self lists for avail creation later
        This will call as we parse the excel sheet 
        """
        for day in self.days:
            shift = eval(day)
            if shift == "Off":
                continue
            if shift == "All Day" and day != "Saturday":
                self.shifts[f'Shift 1 - {day}'][f'users_{week}'].append(user_id)
                self.shifts[f'Shift 2 - {day}'][f'users_{week}'].append(user_id)
                self.shifts[f'Shift 3 - {day}'][f'users_{week}'].append(user_id)
            elif shift == "All Day" and day == "Saturday":
                self.shifts[f'Shift 1 - {day}'][f'users_{week}'].append(user_id)
                self.shifts[f'Shift 2 - {day}'][f'users_{week}'].append(user_id)
            elif shift == "Shift 1&2":
                self.shifts[f'Shift 1 - {day}'][f'users_{week}'].append(user_id)
                self.shifts[f'Shift 2 - {day}'][f'users_{week}'].append(user_id)
            elif shift == "Shift 1&3":
                self.shifts[f'Shift 1 - {day}'][f'users_{week}'].append(user_id)
                self.shifts[f'Shift 3 - {day}'][f'users_{week}'].append(user_id)
            elif shift == "Shift 2&3":
                self.shifts[f'Shift 2 - {day}'][f'users_{week}'].append(user_id)
                self.shifts[f'Shift 3 - {day}'][f'users_{week}'].append(user_id)
            else:
                self.shifts[f'{shift} - {day}'][f'users_{week}'].append(user_id)

    def create_date_using_template(self, template): #No Longer in use
        """
        Using Today find the date using template
        these templates will define how far the date we are looking for should be from today
        """
        today = datetime.today()
        tday = today.strftime ("%m-%d-%Y")

        today_int = int(datetime.today().weekday())
        today_weekday = WEEKDAYS[today_int]
        print(f"Today is : {today_weekday}")

        next_date_template = template[today_weekday]
        future_date = pd.to_datetime(tday) + pd.DateOffset(days=next_date_template)
        future_date = future_date.strftime("%Y-%m-%d")

        return future_date


#these weekday dictionaries are set in order to create a date template, when inputting into skedulo we are expected to 
#input the shift from sunday to saturday, these templates will take whatever today is and interactively create a date for this item
#No Longer in use.
WEEKDAYS = {
0: "Monday",
1: "Tuesday",
2: "Wednesday",
3: "Thursday",
4: "Friday",
5: "Saturday",
6: "Sunday"
}
#for start date sunday
NEXT_SUNDAY_TEMPLATE = {
"Monday": 6,
"Tuesday": 5,
"Wednesday": 4,
"Thursday": 3,
"Friday": 2,
"Saturday": 1,
"Sunday": 0
}
ONEWEEK_SUNDAY_TEMPLATE = {
"Monday": 13,
"Tuesday": 12,
"Wednesday": 11,
"Thursday": 10,
"Friday": 9,
"Saturday": 8,
"Sunday": 7
}
#for two weeks ahead Sunday
TWOWEEK_SUNDAY_TEMPLATE = {
"Monday": 20,
"Tuesday": 19,
"Wednesday": 18,
"Thursday": 17,
"Friday": 16,
"Saturday": 15,
"Sunday": 14
}
#for three weeks ahead Sunday
THREEWEEK_SUNDAY_TEMPLATE = {
"Monday": 27,
"Tuesday": 26,
"Wednesday": 25,
"Thursday": 24,
"Friday": 23,
"Saturday": 22,
"Sunday": 21
}

if __name__ == "__main__":
    something = Skedulo()
    #something.shift_creator()
    #something.pattern_creator()
    something.run()
    #print(something.monday_shift1)
    #print(len(something.shifts['Shift 2 - Monday']['users']))
    #print(something.shifts['Shift 2 - Monday']['users'])

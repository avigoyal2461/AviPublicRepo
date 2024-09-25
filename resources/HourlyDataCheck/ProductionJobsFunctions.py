# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
#This is a helper file with functions for the ProductionJobsQuery_vTO.py file.
"""
Created on Tue Jan  2 15:20:34 2024

@author: TejaKarri
"""

def di_error_calculations (query_results, di_columns, di_params, error_dict, error_details):
    
    
    '''
    Find errors that exist with the data

    Critera In Order For All Production Tables EXCEPT Spotio:
        (1) Not running on time
            (a) Concerning - Did not run on time within the hour, but ran the previous hour
            (b) Failure - Did not run for the last 2 hours
        (2) Row updates are significantly large

    Criteria for Production and Geolocation Error:
        - If message exist, then show
        
    Arguments:
        (1) query_results: The dictionary corresponding to the results of a query
        (2) di_columns: Data Integration columns for the respective query as a dictionary
        (3) di_params: Data Integration values for the respective query as a dictionary of tuples
        (4) error_dict: A dictionary containing query entries that do not meet time or parameter conditions
        (5) error_details: A dictionary containing compiled lists of errors
    '''

    
    # For each entry in the query:
    for e in query_results:
        # If the entry is one of the following...
        if e in ('Prod_Error', 'Geo_Error'):
            
            if not query_results[e].empty:
                error_day_buffer = 1
                mask = query_results[e]['Runtime_Diff_Days'] < error_day_buffer
                if not query_results[e].loc[mask].empty: # If there are errors:
                    error_dict[e] = query_results[e]       
                    print(f"There was an issue in: {e}")
                    error_details[e].append(f"An error was noted in {e}")
            else:
                error_dict[e] = pd.DataFrame()
                print(f"There was no issue with: {e}")
        
        elif e in ('OnePay_Individual', 'OnePay_Full'):
            
            error_hour_buffer = di_params[e][0]
            # Check if any entries have failed
            if e == 'OnePay_Individual':
                mask = (query_results[e]['Runtime_Diff'] > error_hour_buffer) | (query_results[e]['Job_Component_Status'] != 'Complete')
            else:
                mask = (query_results[e]['Runtime_Diff'] > error_hour_buffer) | (query_results[e]['Job_Status'] != 'Complete')
            
            err_df = query_results[e].loc[mask]
            error_dict[e] = err_df
            
            if not err_df.empty: # If there are errors:    
                print(f"There was an issue in: {e}")
                error_details[e].append(f"An error was noted in {e}")
            else:
                print(f"There was no issue with: {e}")
        
        elif e not in ('Spotio_Feed_Data', 'Spotio_Knocks', 'Spotio_First_Knocks'):
            if di_columns[e][1]: # If there is a time value...
                #If the Runtime Diff is greater than time diff
                err_df = query_results[e].loc[query_results[e]['Runtime_Diff'] > di_params[e][0]]
                
                # Specifically for TSA
                if e == 'TSA':
                    runtime_day_gap = 5 # Number of days since last refresh greater than becomes a problem
                    skip_tables = ['Task', 'Club_Contracts']
                    long_refresh_tables = ['Sales_Employee', 'Resource_Tag', 'JobResource', 'Territory', 'Resource_Region', 'Sked_Tag', 'Region']
                    err_df = err_df.loc[~(err_df['Table_Name'].isin(skip_tables))] # not those table names
                    err_df = err_df.loc[(err_df['Table_Name'].isin(skip_tables)) & (err_df['Runtime_Diff_Days'] > runtime_day_gap)]
                    
                error_dict[e] = err_df
                
                if not err_df.empty:
                    error_details[e].append(f'{e} did not refresh in time')
                
                '''
                # Look at specific parameters and verify the values
                # For each parameter in the query:
                if len(di_columns[e][2]) > 0: # If there are unique parameters to check against
                    for idx in range(len(di_columns[e][2])): # For each of those parameters
                        param_col = di_columns[e][2][idx] # Column needed for comparison
                        param_val = di_params[e][1][idx] # Parameter Value for that column
                        
                        err_df = err_df.loc[err_df[param_col] > param_val]
                        
                        if not err_df.empty:
                            error_details[e].append(f'The {param_col} was not greater than {param_val}')
                '''
                
            if err_df.empty:
                print('There was no issue with: ', e)
            else: 
                print('There was an issue with: ', e)
                
    return error_dict
                    
'''
Criteria For Spotio:
    - First Knocks Activity Feed Id must be close to Activity Feed Id
'''

def spotio_calculations (query_results, di_params, error_dict, error_details):
    
    knock_count_diff = di_params['Spotio'][2][0] # Difference for Spotio knocks between 2 weekdays
    first_knock_feed_id = query_results['Spotio_First_Knocks']['FK_ActivityFeedId'][0]
    spotio_feed_id = query_results['Spotio_Knocks']['ActivityFeedId'][0]
    feed_id_lag = di_params['Spotio'][1]
    
    if (spotio_feed_id - first_knock_feed_id) >= feed_id_lag:
        error_dict['Spotio_Knocks'] = pd.concat([query_results['Spotio_First_Knocks'], query_results['Spotio_Knocks']], axis=1, join='outer')
        error_details['Spotio_Knocks'] = ['Spotio refresh may not have occurred']
        print('There is an issue with First Knock Feed Ids')
    else:
        print('There were no issues with First Knock Feed Ids')

    # Finding issues in the Spotio Knocks Feed
    
    knock_count_today = query_results['Spotio_Feed_Data']['Count'][0]
    knock_count_yesterday = query_results['Spotio_Feed_Data']['Count'][1] 
    
    # Convert to Datetime objects to see if weekend or not
    # activitydate_today.weekday() 0 - Monday 6 - Sunday
    date_range = 4
    query_results['Spotio_Feed_Data']['ActivityDate'] = pd.to_datetime(query_results['Spotio_Feed_Data']['ActivityDate']) # Convert from str to datetime
    activitydate_yesterday = query_results['Spotio_Feed_Data']['ActivityDate'][1] # Yesterday Spotio Feed Id
    activitydate_today = query_results['Spotio_Feed_Data']['ActivityDate'][0] # Today's Spotio Feed Id
    cal = calendar()
    holidays = cal.holidays(start=activitydate_yesterday - timedelta(days=date_range), end=activitydate_today + timedelta(days=date_range))
    holiday_bool = query_results['Spotio_Feed_Data']['ActivityDate'][query_results['Spotio_Feed_Data']['ActivityDate'].isin(holidays)].empty
    
    # If it is not a holiday & 2 days ago was not a Saturday or Sunday and 1 Day ago was not Sunday...
    if (not holiday_bool) and (activitydate_yesterday.weekday() not in [5, 6] and activitydate_today.weekday() != 6):
        knock_count_diff = di_params['Spotio'][2][0] # Difference for Spotio knocks between 2 weekdays
    else:
        knock_count_diff = di_params['Spotio'][2][1] # Difference for Spotio knocks between 2 weekdays
        
    if (knock_count_today - knock_count_yesterday) >= knock_count_diff:
        error_dict['Spotio_Feed_Data'] = query_results['Spotio_Feed_Data']
        error_details['Spotio_Feed_Data'] = ['Spotio feed gap is really large']
        print('There is an issue with Spotio Knocks Data')
    else:
        print('There were no issues with Spotio Knocks Data')
    
    return error_dict

ProductionJobQueries = {
    
    'Prod': '''Select 'Prod Every hr daytime Everyday at 0.45 hrs............', SWITCHOFFSET(max(sf_update_timestamp), -300)
            FROM stg.stg_Opportunity(nolock) where SystemModstamp >= dateadd(day, -2, getdate() )''',
    
    'Wolf': '''Select 'Prod, Wolf, every hr', Table_name, SWITCHOFFSET(Last_Run_Timestamp, -300) AS Last_Run_Timestamp_EST,
            SWITCHOFFSET(Last_Extracted_Timestamp, -300) AS Last_Extracted_Timestamp_EST,Rows_updated
            from wolf.Data_integration_Control(nolock)''',
    
    'Roof': '''Select 'Prod, Roof', Table_name, SWITCHOFFSET(Last_Run_Timestamp, -300) AS Last_Run_Timestamp_EST,
                SWITCHOFFSET(Last_Extracted_Timestamp, -300) AS Last_Extracted_Timestamp_EST,Rows_updated
                from roof.Data_integration_Control(nolock)''',
                
    'oneDRAW': '''select  'Prod,oneDRAW,every hr@30', Table_name,  Last_Run_Timestamp, 
                    SWITCHOFFSET(Last_Run_Timestamp, -300) AS Last_Run_Timestamp_EST, 
                    SWITCHOFFSET(Last_Extracted_Timestamp, -300) AS Last_Extracted_Timestamp_EST,
                    job_name,Job_End_Timestamp from draw.Data_Integration_Control(nolock)''',
                            
    'TSA': '''select  'Prod,TSA Integration,every hr', Table_name, SWITCHOFFSET(Last_Run_Timestamp, -300) AS Last_Run_Timestamp_EST,
            SWITCHOFFSET(Last_Extracted_Timestamp, -300) AS Last_Extracted_Timestamp_EST,Batch_Size, Days_Processed
            from TSA.Data_Integration_Control(nolock)''',
    
    'OnePay_Individual': '''select top 7 'Prod,onePAY Data Integration,every 3 hr', ec.DI_Extract_Component_Name, SWITCHOFFSET(Job_Component_Start_Timestamp, -300) AS Job_Component_Start_Timestamp, SWITCHOFFSET(Job_Component_End_Timestamp, -300) AS Job_Component_End_Timestamp, Job_Component_Status,Batch_Count
                            from [DI].[DI_Job_Extract_Component] jec (nolock)
                            left join [DI].[DI_Extract_Component] ec on ec.DI_Extract_Component_Id = jec.DI_Extract_Component_Id
                            order by Job_Component_Start_Timestamp desc''',
                                                        
    'OnePay_Full': '''select top 1 'Prod,onePAY Data Integration,every 3 hr', SWITCHOFFSET(Job_Start_Timestamp, -300) as Job_Start_Timestamp, SWITCHOFFSET(Job_End_Timestamp, -300) as Job_End_Timestamp, Job_Status
                        from di.DI_job
                        where di_job_type_id = 1
                        order by User_Created_Timestamp desc''',
    
    'Prod_Error': '''Select top 5 'Prod Error',*, SWITCHOFFSET(ErrorTime, -300) AS ErrorTime_EST
                    from tsa.ErrorLog where ErrorTime >= dateadd(day, -2, getdate() ) order by errorTime desc''',
    
    'Geo_Error': '''Select top 10 'Geo Error',id, latformula, longformula,
                    SWITCHOFFSET(User_Created_Timestamp, -300) AS ErrorTime_EST
                    from wolf.Eagleview_ErrorLog where [User_Created_Timestamp] >= dateadd(day, -2, getdate() ) order by User_Created_Timestamp desc''',
    
    'Metadata': '''select TOP 14 'Prod,TSA Metadata', Table_name, Execution_No,
                    SWITCHOFFSET(Start_time, -300) AS Start_time_EST,
                    SWITCHOFFSET(Load_date, -300) AS Load_date_EST ,Rows_inserted
                    from TSA.sp_Execution_Log ORDER BY Start_time desc, Execution_No asc''',
                    
    'Spotio_Feed_Data':'''Select TOP 2 convert(varchar(10), activitydate, 120), count(*) from [dbo].[SpotioActivitiesFeedDataV2] (nolock)
                            where activitydate >= dateadd(day, -3, getdate() )
                            group by convert(varchar(10), activitydate, 120)
                            order by 1 desc''',
    
    'Spotio_Knocks': '''Select top 1 ActivityFeedId, InsertedDate, address, reportType, activityType, result
                        from dbo.SpotioActivitiesFeedDataV2(nolock) order by activityFeedID desc''',
    
    'Spotio_First_Knocks':'''Select top 1 * from tsa.Spotio_First_Knock(nolock) order by activityFeedID desc'''
    }

ProductionJobColumns = { # Tuple of form ([Array of Columns], Time Specific Column, [Parameters for Selection])
    
    'Prod': (['', 'Timestamp'], 'Timestamp', []),
    
    'Wolf': (['', 'Table_Name', 'Last_Run_Timestamp_EST', 'Last_Extracted_Timestamp_EST', 'Rows_Updated'], 'Last_Run_Timestamp_EST', []),
    
    'Roof': (['', 'Table_Name', 'Last_Run_Timestamp_EST', 'Last_Extracted_Timestamp_EST', 'Rows_Updated'], 'Last_Run_Timestamp_EST', []),
                
    'TSA': (['', 'Table_Name', 'Last_Run_Timestamp_EST', 'Last_Extracted_Timestamp_EST', 'Batch_Size', 'Days_Processed'], 'Last_Run_Timestamp_EST', []),
    
    'oneDRAW': (['', 'Table_Name', 'Last_Run_Timestamp', 'Last_Run_Timestamp_EST', 'Last_Extracted_Timestamp_EST', 'job_name', 'job_end_timestamp'], 'Last_Run_Timestamp_EST', []),
    
    'OnePay_Individual': (['', 'DI_Extract_Component_Name', 'Job_Component_Start_Timestamp', 'Job_Component_End_Timestamp',	'Job_Component_Status', 'Batch_Count'], 'Job_Component_Start_Timestamp', []),
    
    'OnePay_Full': (['', 'Job_Start_Timestamp', 'Job_End_Timestamp', 'Job_Status'], 'Job_Start_Timestamp', []),
    
    'Prod_Error': (['', 'ID', 'UserName', 'ErrorNumber', 'ErrorState', 'ErrorLine', 'ErrorMessage', 'ErrorTime', 'TableName', 'ExecutionOrder', 'SP_Name', 'ErrorTime_EST'], 'ErrorTime_EST', []),
    
    'Geo_Error': (['', 'ID', 'latformula', 'longformula', 'ErrorTime_EST'], 'ErrorTime_EST', []),
    
    'Metadata': (['', 'Table_Name', 'Execution_No', 'Start_time_EST', 'Load_date_EST', 'Rows_Inserted'], 'Start_time_EST', []),
                    
    'Spotio_Feed_Data': (['ActivityDate', 'Count'], [], 'Count'),
    
    'Spotio_Knocks': (['ActivityFeedId', 'InsertedDate', 'Address', 'ReportType', 'ActivityType', 'Result'], [], ['ActivityFeedId']),
    
    'Spotio_First_Knocks': (['FK_ActivityFeedId', 'FK_Address'], [], ['FK_ActivityFeedId'])
    
    }

ProductionJobParams = { # Tuple of form (#Time Diff, Parameter Values coinciding with Params from ProductionJobColumns)
    
    'Prod': (1, []),
    
    'Wolf': (1, []),
    
    'Roof': (2, []),
                
    'TSA': (1, []),
    
    'oneDRAW': (0.5, []),
    
    'OnePay_Individual': (3, []),
    
    'OnePay_Full': (3, []),
    
    'Metadata': (2.1, []),
        
    'Prod_Error': ([], []),
    
    'Geo_Error': ([], []),
                    
    'Spotio': (2, 200, [10000, 30000]) # (InsertedDate, Feed Id Gap, [Interday Knock Diff Weekday, Interday Knock Diff Weekend/Holday]) Spotio gets its own different format because it uses 3 query results
    
    }
    
errors = {
    
    'Prod_Error': [],
    
    'Geo_Error': [],
                    
    'Spotio_Feed_Data': pd.DataFrame(), # Was an empty list may need to change
    
    'Spotio_Knocks': pd.DataFrame(), # Was an empty list may need to change
    
    'oneDRAW': [],
    
    'OnePay_Individual': [],
    
    'OnePay_Full': [],
    
    'Prod': [],
    
    'Wolf': [],
    
    'Roof': [],
                
    'TSA': [],
    
    'Metadata': []
    
    }

error_summary = {
    
    'Prod_Error': [],
    
    'Geo_Error': [],
                    
    'Spotio_Feed_Data': [],
    
    'Spotio_Knocks': [], 
    
    'OnePay_Individual': [],
    
    'OnePay_Full': [],
    
    'oneDRAW': [],
    
    'Prod': [],
    
    'Wolf': [],
    
    'Roof': [],
                
    'TSA': [],
    
    'Metadata': []
    
    }
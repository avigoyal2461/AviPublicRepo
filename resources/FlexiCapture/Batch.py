# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import re
import csv
from FlexiCapture.config import bill_export_path, bill_import_path, batch_path

class Batch:
    """A flexicapture image batch. Located in import and export folders."""
    def __init__(self, batch_number):
        self.number = batch_number
        self.folder_name = f'Batch HF_ID{str(batch_number)}'
        self.import_path = f'{batch_path}\\{self.folder_name}'
        self.data_export_path = f'{bill_export_path}\\{self.folder_name}\\Data_00000001.csv'
        self.graph_export_path = f'{bill_export_path}\\{self.folder_name}\\Data_00000001\\GraphBars.csv'
        self.completed = False

    def __str__(self):
        return self.folder_name

    def get_batch_number(self):
        return str(self.number)

    def get_bill_data(self):
        data = self.get_info()
        return data

    def check_completed(self):
        """Checks batch folders for completion and sets flag."""
        self.completed = os.path.exists(self.data_export_path)
        return self.completed

    def get_info(self):
        """Gets usage, utility, rate, meter number, account number, and name from data csv if available first, otherwise gets it from graph csv"""
        batch_info = self.get_data_csv_info()
        if batch_info['usage'] == 0:
            batch_info['usage'] = self.get_graph_csv_usage()
        return batch_info

    def get_data_csv_info(self):
        data = {'usage':0,
                'utility':'',
                'account_number':'',
                'meter_number':'',
                'name':'',
                'email':''
                }

        csv_file_path = self.data_export_path
        # Columns
        account_number_col = 1
        name_col = 3
        utility_col = 23
        email_col = None
        meter_number_col = 8
        total_col = 28

        JANUARY_COL = 9
        DECEMBER_COL = 20
        month_cols = list(range(JANUARY_COL, DECEMBER_COL+1))

        try:
            with open(csv_file_path, 'r') as data_csv:
                reader = csv.reader(data_csv)
                for index, row in enumerate(reader):
                    if index == 0:
                        # First row
                        for index, col in enumerate(row):
                            if col == 'AnnualUsage': # Check for annual usage
                                total_col = index
                    else:
                        # Not first row
                        data['utility'] = row[utility_col]
                        data['account_number'] = row[account_number_col]
                        data['meter_number'] = row[meter_number_col]
                        data['name'] = row[name_col]
                        # Check that all month values were found
                        all_month_vals = True
                        for month in month_cols:
                            if not row[month]:
                                all_month_vals = False
                        if all_month_vals:
                            usages = row[JANUARY_COL:DECEMBER_COL + 1] # Slice, up to but not including row after DEC Col
                            data['usage'] = sum([int(usage) for usage in usages])
                        # Check for AnnualUsage field
                        if row[total_col]:
                            if row[total_col] != '>1 I':
                                data['usage'] = int(row[total_col])

                
        except FileNotFoundError:
            print(f'Could not find requested file: {csv_file_path}')
        except Exception as e:
            print(f'Could not get graph csv data: {e}')
        return data


    def get_graph_csv_usage(self):
        "Opens graph csv file and returns total usage if available."
        csv_file_path = self.graph_export_path
        usage_re = re.compile(r'\d+')
        total = 0
        try:
            with open(csv_file_path, 'r') as graph_csv:
                reader = csv.reader(graph_csv)
                for index, row in enumerate(reader):
                    if index != 0:
                        usage_match = re.search(usage_re, row[4])
                        total += int(usage_match[0])
        except FileNotFoundError:
            print(f'Could not find requested file: {csv_file_path}')
        except Exception as e:
            print(f'Could not get graph csv data: {e}')
        finally:
            return total


if __name__ == "__main__":
    test_batch = Batch('97')
    print(test_batch)
    print(test_batch.get_info())
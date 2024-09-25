# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

# Imports
import os
import shutil
import csv
import re
import shutil
import img2pdf
from PIL import Image
from Files.config import abbyy_export_path, abbyy_import_path
from FlexiCapture.ElectricBill import ElectricBill

USER = os.environ['username']


class FileHandler:
    def __init__(self):
        self.cache = None

    def get_latest_electric_bill(self):
        try:
            if self.new_electric_bill_available():
                usage = self.get_latest_ebill_usage()
                utility = self.get_latest_ebill_utility()
                rate = 'Residential' # TODO: Set up abbyy and make this variable
                try:
                    self.delete_all_abbyy_exports()
                    pass
                except:
                    print('Unable to delete ABBYY Exports...')
                return ElectricBill(utility, usage, rate)
            else:
                return ElectricBill()
        except Exception as e:
            print(e)
            return ElectricBill()
            

    def new_electric_bill_available(self):
        file_names = os.listdir(abbyy_export_path)
        if file_names:
            return True
        else:
            return False

    def delete_all_abbyy_exports(self):
        filelist = os.listdir(abbyy_export_path)
        for f in filelist:
            os.remove(os.path.join(abbyy_export_path, f))

    def delete_file(self, file_path):
        try:
            os.remove(file_path)
        except:
            print('Attempted to delete file that does not exist...')
        
    def get_latest_ebill_usage(self):
        folder = self.get_latest_ebill_batch_folder()
        if folder:
            return self.get_ebill_usage_from_batch(folder)
        else:
            return None

    def get_latest_ebill_utility(self):
        folder = self.get_latest_ebill_batch_folder()
        if folder:
            return self.get_ebill_utility_from_batch(folder)
        else:
            return None


    def get_latest_ebill_batch_folder(self):
        try:
            current_exports = os.listdir(abbyy_export_path)
        except:
            print('Cannot find exports folder!')
            return None
        paths = [os.path.join(abbyy_export_path, basename) for basename in current_exports if 'Batch' in basename]
        return max(paths, key=os.path.getctime)

    def get_ebill_usage_from_batch(self, batch_path):
        """Gets usage from data csv if available first, otherwise gets it from graph csv"""
        data_csv_path = self._get_data_csv_path_from_batch(batch_path)
        graph_csv_path = self._get_graph_csv_path_from_batch(batch_path)
        usage = None
        if data_csv_path:
            usage = self.get_data_csv_usage(data_csv_path)
            if usage != '':
                return usage
        if not usage and graph_csv_path:
            return self.get_graph_csv_usage(graph_csv_path)
        else:
            print('No batch found')
            return None


    def _get_data_csv_path_from_batch(self, batch_path):
        file_names = os.listdir(batch_path)
        for file_name in file_names:
            if '.csv' in file_name and 'Data' in file_name:
                print(f'Found data file: {file_name}')
                return os.path.join(batch_path, file_name)
        return None

    def _get_graph_csv_path_from_batch(self, batch_path):
        """Gets graph csv from sub folder if it exists."""
        sub_folder = None
        file_names = os.listdir(batch_path)
        for file_name in file_names:
            if '.csv' not in file_name and 'Data' in file_name:
                sub_folder = os.path.join(batch_path, file_name)
        if sub_folder:
            sub_folder_file_names = os.listdir(sub_folder)
            for file_name in sub_folder_file_names:
                if 'GraphBars' in file_name:
                    print(f'Found graph file: {file_name}')
                    return os.path.join(sub_folder, file_name)
        else:
            return None

    def get_data_csv_usage(self, csv_file_path):
        """Opens a batch csv file and returns total usage if available."""
        JANUARY_COL = 9
        DECEMBER_COL = 20
        total_col = None
        try:
            with open(csv_file_path, 'r') as batch_csv:
                reader = csv.reader(batch_csv)
                for index, row in enumerate(reader):
                    if index != 0:
                        if row[JANUARY_COL] and row[DECEMBER_COL]:
                            print('Found monthly values in batch data...')
                            usages = row[JANUARY_COL:DECEMBER_COL + 1]
                            return sum([int(usage) for usage in usages])
                        else:
                            print('No monthly data in batch file...')
                            if total_col:
                                return row[total_col]
                    else: 
                        for index, col in enumerate(row):
                            if col == 'AnnualUsage': # Check for annual usage
                                total_col = index

        except FileNotFoundError:
            print('Could not find requested file...')
        except Exception as e:
            print(f'Could not get batch data. Error: {e}')

        return None

    def get_graph_csv_usage(self, csv_file_path):
        "Opens graph csv file and returns total usage if available."
        usage_re = re.compile(r'\d+')
        total = 0
        try:
            monthly_values = [] # Keep a list of monthly values and check if any are equal, if they are there was likely an error.
            with open(csv_file_path, 'r') as graph_csv:
                reader = csv.reader(graph_csv)
                for index, row in enumerate(reader):
                    if index != 0:
                        print(row)
                        search_col = row[4].replace(',', '')
                        usage_match = re.search(usage_re, search_col)
                        print(f'Found usage match {str(usage_match)}')
                        monthly_values.append(int(usage_match[0]))
            if monthly_values.count(monthly_values[0]) > 2:
                return None
            else:
                total = sum(monthly_values)
                return total
        except FileNotFoundError:
            print(f'Could not find requested file: {csv_file_path}')
        except Exception as e:
            print(f'Could not get graph csv data: {e}')
        return None

    def get_ebill_utility_from_batch(self, batch_path):
        """Gets utility from data csv"""
        data_csv_path = self._get_data_csv_path_from_batch(batch_path)
        return self.get_data_csv_utility(data_csv_path)

    def get_data_csv_utility(self, csv_file_path):
        """Opens a batch csv file and returns utility company if available."""
        UTILITY_COL = 23
        try:
            with open(csv_file_path, 'r') as batch_csv:
                reader = csv.reader(batch_csv)
                for index, row in enumerate(reader):
                    if index != 0:
                        print('Found utility')
                        return row[UTILITY_COL]
        except FileNotFoundError:
            print('Could not find requested file...')
        except Exception as e:
            print(f'Could not get batch data. Error: {e}')

        return None

    def move_files_to_abbyy_import(self, file_paths):
        """Moves given files to the import folder for abbyy."""
        for file_path in file_paths:
           shutil.move(file_path, abbyy_import_path)
           print(f'Moved {file_path} to ABBYY import folder')

    def copy_file_to_abbyy_import(self, file_path):
        """Copies given files to the import folder for abbyy."""
        shutil.copy2(file_path, abbyy_import_path)
        print(f'Copied {file_path} to ABBYY import folder')

    def move_bills_photos_to_abbyy_import(self, folder):
        paths = self.get_bill_photo_paths(folder)
        return self.move_files_to_abbyy_import(paths)
    
    def get_bill_photo_paths(self, folder):
        paths = []
        try:
            file_names = os.listdir(folder)
        except FileNotFoundError:
            return None
        for file_name in file_names:
            if 'bill' in file_name.lower():
                paths.append(os.path.join(folder, file_name))
        return paths

    def convert_photos_to_pdf(self, photo_paths):
        photo_paths = self.resize_photos_for_processing(photo_paths)
        new_path = f'C:\\Users\\{USER}\\Desktop\\autobot\\Electric Bill.pdf'
        if photo_paths:
            with open(new_path, 'wb') as pdf_file:
                pdf_file.write(img2pdf.convert(photo_paths))
                return new_path
        else:
            print('No paths found')
            return None

    def resize_photos_for_processing(self, photo_paths):
        paths = []
        for photo in photo_paths:
            image = Image.open(photo)
            new_image = image.resize((3000,3900)) # Matches Letter Paper Ratio
            new_image.save(photo)
            paths.append(photo)
        return paths

    def resize_photo_for_processing(self, photo_path):
        image = Image.open(photo_path)
        new_image = image.resize((3000,3900)) # Matches Letter Paper Ratio
        new_image.save(photo_path)
        return photo_path

    def get_upload_string_files_from_path(self, folder_path):
        file_names = os.listdir(folder_path)
        file_paths = [os.path.join(folder_path, file_name) for file_name in file_names]
        formatted_string = ''
        for file_path in file_paths:
            formatted_string += f'"{file_path}" '
        return formatted_string

    def get_newest_path_in_folder(self, folder_path):
        folder_files = os.listdir(folder_path)
        file_names = [os.path.abspath(os.path.join(folder_path, file_name)) for file_name in folder_files]
        sorted_file_names = sorted(file_names, key=os.path.getmtime, reverse=True)
        file_name = sorted_file_names[0]
        print(file_name)
        return os.path.join(folder_path, file_name)

    def delete_folder(self, folder_path):
        try:
            shutil.rmtree(folder_path)
        except:
            print('Unable to delete folder...')


if __name__ == "__main__":
    test_uri = r'C:\Users\RPA_Bot_4\Desktop\ExportData\Batch HF_ID187\Data_00000001\GraphBars.csv'
    tster = FileHandler()
    result = tster.get_graph_csv_usage(test_uri)
    print(result)
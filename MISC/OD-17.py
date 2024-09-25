import pandas as pd
import time
import glob
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from PyPDF2 import PdfReader, PdfWriter
import requests
from datetime import datetime
import openpyxl
from salesforceportal import SalesforcePortal
from sendEmail import email
import sys
sys.path.append(r"C:\Users\RPAadmin\Desktop\automation\api\OneDocFieldMapping")
from Create_Excel import Excel
from Excel_Email import ExcelEmail
import glob
import os
from connection import SharepointConnection
# sys.path.append(r"C:\Users\RPAadmin\Desktop\automation\api\OneDocFieldMapping")
# from Create_Excel import Excel
# from Excel_Email import ExcelEmail

class OD17():
    def __init__(self):
        # self.local_excel_path = r"C:\test\fields.xlsx"
        # self.local_excel_path = r"C:\Users\RPA_bot_11\Desktop\conga\current_fields.xlsx"
        # self.local_excel_path = r"C:\test\conga_remastered\fields.xlsx"
        self.local_excel_path = r"C:\Users\RPA_bot_13\Desktop\conga\fields.xlsx"
        self.path = r"C:\Users\RPA_bot_13\Desktop\conga"
        # self.path = r"C:\test\conga_remastered"
        self.file_names = []
        self.excel_writer = Excel()
        # self.excel_writer.run(file)
        self.fields = []
        self.field_count = []
        today = str(datetime.today())
        self.today = today.split(" ")[0]
        self.salesforce = SalesforcePortal()
        self.sharepoint = SharepointConnection()
#files without file paths
#fields should be in column d
    def add_new_sheet(self, list_items=None):
        # today = str(datetime.today())
        # today = today.split(" ")[0]
        # self.path = fr"{self.path}\New_{self.today}.xlsx"
        if list_items:
            try:
                original_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name='Pre-Script_Fields')
            except:
                original_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name='Current')
            cols = ['File_Name', 'Form_Fields']
            orig_file_names = original_xl['File_Name']
            orig_fields = original_xl['Form_Fields']
            
            original_data = {
                'File_Name' : [name for name in orig_file_names],
                'Form_Fields' : [field for field in orig_fields]
            }
            data = {
                'File_Name' : [name for name in list_items]
            }
            df1 = pd.DataFrame(original_data, columns=cols)
            df2 = pd.DataFrame(data, columns=['File_Name'])
            writer = pd.ExcelWriter(self.local_excel_path, engine = 'xlsxwriter')
            df1.to_excel(writer, sheet_name = f'Pre-Script_Fields')
            df2.to_excel(writer, sheet_name = f'Missing_Sheets')
            return True
        else:
            # self.path = fr"{self.path}\New_2022-10-21.xlsx"
            # xl = pd.ExcelFile(self.path)
            # original_xl = pd.read_excel(self.local_excel_path, engine='openpyxl')
            print(self.local_excel_path)
            try:
                original_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name='Pre-Script_Fields')
            except:
                original_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name='Current')
                
            xl = pd.read_excel(self.path, engine='openpyxl', sheet_name=f'Sheet1')
            try:
                missing_sheets = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name='Missing_Sheets')
                missing_names = missing_sheets['File_Name']
                missing_names = list(missing_names)
                missing_data = {
                     'File_Name' : [name for name in missing_names]
                }
            except:
                print("Skipped missing data sheet")
                pass
            # print(xl)
            cols = ['File_Name', 'Form_Fields']
            orig_file_names = original_xl['File_Name']
            orig_fields = original_xl['Form_Fields']

            file_names = xl['File_Name']
            fields = xl['Form_Fields']
            # print(fields)
            file_names = list(file_names)
            fields = list(fields)
            # print(fields)
            data = {
                'File_Name' : [name for name in file_names],
                'Form_Fields' : [field for field in fields]
            }
            original_data = {
                'File_Name' : [name for name in orig_file_names],
                'Form_Fields' : [field for field in orig_fields]
            }
            df1 = pd.DataFrame(original_data, columns=cols)
            df2 = pd.DataFrame(data, columns=cols)
            writer = pd.ExcelWriter(self.local_excel_path, engine = 'xlsxwriter')
            try:
                df3 = pd.DataFrame(missing_data, columns=['File_Name'])
                df3.to_excel(writer, sheet_name = f'Missing_Sheets')
                
            except:
                print("Skipping missing sheet creation")
                pass
            # df1 = xl.parse("Sheet1")
            writer = pd.ExcelWriter(self.local_excel_path, engine = 'xlsxwriter')
            df1.to_excel(writer, sheet_name = f'Pre-Script_Fields')
            df2.to_excel(writer, sheet_name = f'Post-Script_Fields_{self.today}')
            
            writer.save()
            print("saved")
            # except:
            #     writer.close()
            #     print("closed")
            # try:
            #     writer.close()
            #     print("Closed again")
            # except:
            #     print("could not close writer")
            
# WIN-T1DP9N5TTTM\RPA_bot_4
    def find_difference(self):
        # xl = pd.ExcelFile(self.local_excel_path)
        original_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name='Pre-Script_Fields')
        new_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name=f'Post-Script_Fields_{self.today}')
        # xl = pd.read_excel(self.local_excel_path, engine='openpyxl')
        # df1 = xl.parse("OldFields")
        # df2 = xl.parse(f"fields_{self.today}")
        # old_file_names = []
        # print("?>")
        old_file_names_excel = original_xl['File_Name']
        old_file_names_large = list(old_file_names_excel)

        old_file_names = []
        for name in old_file_names_large:
            if type(name) == float:
                break
            # print()
            name = name[0:9]
            old_file_names.append(name)
        # for the_old_file_name in old_file_names2:
        #     old_file_names.append(f"{the_old_file_name[0:9]}.pdf")
        old_form_fields = original_xl['Form_Fields']
        old_form_fields = list(old_form_fields)
        # old_file_names = df1['File_Name'].tolist()
        # old_form_fields = df1["Form_Fields"].tolist()

        new_file_names_excel = new_xl['File_Name']
        new_file_names_large = list(new_file_names_excel)
        new_file_names = []
        for name in new_file_names_large:
            if type(name) == float:
                break
            name = name[0:9]
            new_file_names.append(name)
        # new_file_names = df2['File_Name'].tolist()
        new_form_fields = new_xl['Form_Fields']
        new_form_fields = list(new_form_fields)
        # new_form_fields = df2["Form_Fields"].tolist()

        differential_file_name = []
        differential_form_field = []
        comparison_form_field = []

        current = ""
        old_indexes = []
        new_indexes = []

        old_fields_on_current_sheet = []
        old_files_on_current_sheet = []
        new_fields_on_current_sheet = []
        new_files_on_current_sheet = []

        for counter, value in enumerate(old_file_names):
            if value == current:
                continue
                # indexes.append(counter)
            else:
                current = value
                print(counter)
                # old_fields_on_current_sheet.append(counter)
                old_indexes.append(counter)
                # old_indexes.append(old_file_names.index(value))
                # old_file_names.pop()

        for counter, value in enumerate(new_file_names):
            if value == current:
                continue
                # old_indexes.append(counter)
            else:
                current = value
                print(counter)
                # old_fields_on_current_sheet.append(counter)
                new_indexes.append(counter)
                # old_indexes.append(old_file_names.index(value))
                # old_file_names.pop()
        print(new_indexes)
        print(old_indexes)

        current_counter = 0
        new_field_counter = 0
        something_counter = 0
        # print(len(new_form_fields))
        # quit()
        for counter, value in enumerate(new_indexes):
            new_index = new_indexes[counter]
            # try:
            #     end_count = old_indexes[counter + 1]
            # except:
            #     end_count = len(old_form_fields)

            try:
                new_files_end_count = new_indexes[counter + 1]
            except:
                new_files_end_count = len(new_form_fields)

            while new_field_counter < new_files_end_count:
                # print("here")
                new_fields_on_current_sheet.append(new_form_fields[new_field_counter])
                new_files_on_current_sheet.append(new_file_names[new_field_counter])
                new_field_counter += 1
                # print(new_fields_on_current_sheet)
                if new_field_counter == new_files_end_count:
                    # print(new_fields_on_current_sheet)
                    old_fields_on_current_sheet = []
                    old_files_on_current_sheet = []
                    
                    if new_files_on_current_sheet[0] in old_file_names:
                        
                        current_index = old_file_names.index(new_files_on_current_sheet[0])
                        print(f"current index is : {current_index}")
                        print(old_file_names[current_index])
                        try:
                            # end_count = old_indexes[current_index + 1]
                            end_count = old_indexes.index(current_index)
                            end_count += 1
                            end_count = old_indexes[end_count]
                        except:
                            end_count = len(old_form_fields)
                        print(end_count)
                        current_counter = current_index
                        while current_counter < end_count:
                            old_fields_on_current_sheet.append(old_form_fields[current_counter])
                            old_files_on_current_sheet.append(old_file_names[current_counter])
                            current_counter += 1
                            if current_counter == end_count:
                                break
                        for counter, item in enumerate(new_fields_on_current_sheet):
                            if item not in old_fields_on_current_sheet:
                                # print(f"this is the item : {item}")
                                differential_file_name.append(new_files_on_current_sheet[0])
                                differential_form_field.append(item)
                                try:
                                    comparison_form_field.append(old_fields_on_current_sheet[counter])
                                except:
                                    comparison_form_field.append(" ")

                        new_files_on_current_sheet = []
                        new_fields_on_current_sheet = []
                        old_fields_on_current_sheet = []
                        old_files_on_current_sheet = []
                        break
        print(differential_form_field)
        cols = ['File_Name', 'Form_Fields']
        original_data = {
            'File_Name' : [name for name in old_file_names],
            'Form_Fields' : [field for field in old_form_fields]
        }
        newer_data = {
            'File_Name' : [name for name in new_file_names],
            'Form_Fields' : [field for field in new_form_fields]
        }
        diff_data = {
            'File_Name' : [name for name in differential_file_name],
            'Form_Fields' : [field for field in differential_form_field],
            'Old Fields' : [item for item in comparison_form_field]
            # 'Tim New Field Names' : ["" for item in differential_file_name]
        }
        original_df = pd.DataFrame(original_data, columns=cols)
        newer_df = pd.DataFrame(newer_data, columns=cols)
        # cols = ['File_Name', 'Form_Fields', 'Tim New Field Names']
        cols = ['File_Name', 'Form_Fields', 'Old Fields']
        diff_df = pd.DataFrame(diff_data, columns=cols)

        writer = pd.ExcelWriter(self.local_excel_path, engine = 'xlsxwriter')

        original_df.to_excel(writer, sheet_name='Pre-Script_Fields')
        newer_df.to_excel(writer, sheet_name=f'Post-Script_Fields_{self.today}')
        # cols = ['File_Name', 'New_Fields', 'Tim New Field Names']
        diff_df.to_excel(writer, sheet_name=f'Differential_{self.today}')
        writer.save()
        
    def retrieve_from_sharepoint(self):
        while True:
            try:
                self.sharepoint.getFile(file="Fields.xlsx", path=r"C:\Users\RPA_Bot_13\Desktop\conga\new.xlsx")
                break
            except:
                print("retrying sharepoint file grab...")
                time.sleep(5)
                
    def upload_to_sharepoint(self):
        while True:
            try:
                self.sharepoint.uploadFile(self.local_excel_path, folder_name="OneDoc", file_name="fields.xlsx")
                break
            except:
                print("Trying to upload to Sharepoint again...")
                time.sleep(5)
                
    def excel_maker_manual(self):
        self.excel_writer = Excel()
        self.excel_writer.run(r"C:\Users\Rpa_Bot_13\Desktop\Conga-07-11-2023")
        
    def parse_excel(self):
        columns = {
            "File_Name",
            "Form_Fields",
            "updated_field"
        }
        df_counter = 0
        # file_names = []
        # print("???????????????????????????????")
        # fields = []
        # if df.iloc[counter].at['Processed'] == "NO":
        #             # self.REPORTS_TO_PROCESS.append(df.iloc[counter])
        #             project_ids.append(df.at[counter, 'New_Project_Id'])
        #             dl_numbers.append(df.at[counter, 'Column1'])
        #             names.append(df.at[counter, 'Name'])
        xl = pd.ExcelFile(self.local_excel_path)
        # new_xl = pd.read_excel(self.local_excel_path, engine='openpyxl', sheet_name=f'Post-Script_Fields_{self.today}')
        
        df = xl.parse(f'Post-Script_Fields_{self.today}')
        field_counter = 0
        while True:
            try:
                File_Name = df.iloc[df_counter].at['File_Name']
                if df_counter != 0:
                    if File_Name == df.iloc[df_counter].at['File_Name']:
                        self.fields.append(df.at[df_counter, 'Form_Fields'])
                        field_counter += 1
                        # fields.append(df.at[df_counter, 'Updated_Form_Fields'])
                        print(df_counter)
                        # fields.append(df.at[df_counter, 'updated_field'])
                        df_counter += 1
                    else:
                        # print(File_Name)
                        # print(df_counter)

                        self.field_count.append(field_counter)
                        field_counter = 0
                        self.file_names.append(File_Name)
                        self.fields.append(df.at[df_counter, 'Form_Fields'])
                        df_counter += 1
                else:
                    print(File_Name)
                    print(df_counter)

                    # self.field_count.append(field_counter)
                    # field_counter = 0
                    self.file_names.append(File_Name)
                    self.fields.append(df.at[df_counter, 'Form_Fields'])
                    # fields.append(df.at[df_counter, 'Updated_Form_Fields'])
                    df_counter += 1
                        # fields.append(df.at[df_counter, 'updated_field'])
                # return None
            except Exception as e:
                print(e)
                break

        print(self.file_names)
        # print(self.fields)
        # quit()
    def update_field_names(self): #not in use.
        # test = self.file_names[0:10]
        # print(test)
        # quit()
        # print(self.field_count)
        # print(self.fields)
        # quit()
        # quit()
        writer = PdfWriter()

        for file_counter, file in enumerate(self.file_names):
            something = True
            field_count = self.field_count[file_counter]
            new_fields = self.fields[0:field_count]
            # print(new_fields)
            # print(field_count)
            # time.sleep(10)
            while field_count >= 0:
                print(f"Removing {self.fields[0]}")
                remove = self.fields.pop(0)
                # time.sleep(1)
                field_count -= 1
                # print(self.fields[0])
                # quit()
            # self.field_count.pop(0:self.field_count[file_counter])
            print(new_fields)
            try:
                reader = PdfReader(file)
                # writer = PdfWriter()

                page = reader.pages[0]
                fields = reader.get_fields()
                # print(fields)
                # quit()
                # page = writer.get_page[0]
                # page = writer.pages[0]
                writer.add_page(page)
                new_fields = list(new_fields)
                for field in new_fields:
                    field = str(field)
                    writer.updatePageFormFieldValues(

                    # )
                    # writer.update_page_form_field_values(
                        writer.pages[0], field
                        # writer.pages[0], {"fieldname": "some filled in text"}
                    )
                    # print(f"Updated {field}")

                # write "output" to PyPDF2-output.pdf
                with open(file, "wb") as output_stream:
                    writer.write(output_stream)
                    print("Wrote File")
                    # writer.close()
                    output_stream.close()
                time.sleep(2)
            except Exception:
                print("File could not be processed")
                time.sleep(10)
                continue
            # time.sleep(20)

        # return None

    # def pdf_suffix_fields(page, sfx):
    #     for j in range(0, len(page['/Annots'])):
    #         writer_annot = page['/Annots'][j].getObject()
    #         writer_annot.update({NameObject("/T"): createStringObject(writer_annot.get('/T')+sfx)})
    def run(self):
        # failed_sheets = self.salesforce.get_conga_pdf(r"C:\conga")
        self.excel_maker_manual()
        # time.sleep(5)
        # self.add_new_sheet()
        # self.find_difference()
        # email().run(self.local_excel_path)
        email().run(r"C:\Users\rpa_Bot_13\Desktop\conga\New_2023-07-11.xlsx")
        
        # files = glob.glob(r"C:\conga\*pdf")
        # files_excel = glob.glob(r"C:\conga\*xlsx")
        # for file in files:
        #     os.remove(file)
        # for file in files_excel:
        #     os.remove(file)
        # self.upload_to_sharepoint()

    def find_size(self):
        path = r"C:\conga"
        files = glob.glob(f"{path}/*pdf")
        with open(r"C:\Users\Rpa_Bot_13\Desktop\file_size.txt", 'a') as f:
            for file in files:
                # print(file)
                size = os.path.getsize(file)
                # file_name = file.split(r"C:\conga\")[1]
                file_name = file[0:18]
                f.write(f"{file_name}, {size}")
                f.write("\n")
            f.close()

if __name__ == "__main__":
    a = OD17()
    a.run()
    # a.find_size()
    # a.retrieve_from_sharepoint()
    # a.add_new_sheet()
    # a.find_difference()
    # a.parse_excel()
    # a.update_field_names()




# class text():
# # class assignmentone():
#     def hello_world():
#         print("hello world")
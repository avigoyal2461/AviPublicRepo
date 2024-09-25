import os
import win32com.client as win32
from flask import request
from flask_restful import Resource

class SunnovaExcelService(Resource): 
    def post(self):
        response = request.get_json() 
        file_path = os.path.abspath(response['ExcelFileName']+'.xlsx')             
        content = self.Excel_Operations(response,file_path)
        return content

    def Excel_Operations(self,response,file_path):
        input_values = response['InputValues']
        get_output_values = response['OutputCells'] 
        import pythoncom
        pythoncom.CoInitialize() 
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        wb = excel.Workbooks.Open(file_path)   
        sheet = wb.Worksheets(response["SheetName"])  
        for inputs in input_values:
            if inputs['Type'] == 'String':
                sheet.Range((inputs['CellNumber'])).Value = inputs['CellValue']
            elif inputs['Type'] == 'Integer':
                sheet.Range((inputs['CellNumber'])).Value = int(inputs['CellValue'])
        wb.Close(True)

        outputJson =[]
        wb = excel.Workbooks.Open(file_path)   
        sheet = wb.Worksheets(response["SheetName"])
        
        for outputs in get_output_values:            
            tempJson = {'cellNumber': outputs,
                        'cellValue': str(sheet.Range(outputs))
                    }
            outputJson.append(tempJson)
        wb.Close(False)
        
        content = {
            "excelFileName": response['ExcelFileName'],
            "sheetName": response['SheetName'],
            "outputValues": outputJson,
            }

        return content
#pip install aspose-cells
#pip install PyPDF2
#python -m pip install fpdf

# import NCJE_Market_Share_Cleanup
# import NCJE_Cleaner
# from NCJE_Cleaner import CLEAN_EXCEL
# import PyPDF2

from fpdf import FPDF
import os
import glob
import time
import pandas as pd
from selenium import webdriver
from PIL import Image
import excel2img as exi

# NCJE_Market_Share_Cleanup.run() #this runs the cleanup script, if the excel is already there, it rewrites over it
#because i selected to download pipeline first, that will always be at index 1 ( or the second sheet in the list )

#sample pdf creation with all fields filled
# PDF(orientation={'P'(def.) or 'L'}, measure{'mm'(def.),'cm','pt','in'}, format{'A4'(def.),'A3','A5','Letter','Legal')

"""
UNFINISHED, NO LONGER NEEDED SO IF I COME BACK TO FINISH THIS, IT WILL BE FOR LEARNING PURPOSES
"""

class PDF(FPDF):
    def image_test():
        list_of_files_after_download = glob.glob('C:\Hold\*.xlsx')
        EXPORT_FOLDER = "C:\SkeduloInfo"
        installation_name = "installation.png"
        installation_folder = os.path.join(os.getcwd(), EXPORT_FOLDER, installation_name)
        installation_count_image_path = exi.export_img(list_of_files_after_download[2], installation_folder, "Installations by County", None)

        with Image.open(installation_count_image_path) as image:
            img_width, img_height = image.size()
            print(f"{img_width} {img_height}")

    def CLEAN_EXCEL_CREATION(Install_loc, Pipeline_loc):
        # NCJE_Market_Share_Cleanup.run()
        # CLEAN_EXCEL.run(Install_loc, Pipeline_loc)
        a = CLEAN_EXCEL(Install_loc, Pipeline_loc)
        # a.run()
        a.Full_Install()
        a.Pipeline()

    def CREATE_PDF():
        pdf = PDF(orientation='P') #creates pdf object
        pdf.add_page()
        pdf.output('testpdf.pdf', 'F') #outputs the pdf into the same file as code, for now
        
class DOWNLOAD_FROM_CHROME(): #this class can actually be added into another file, but for now, here.
    def DOWNLOAD() -> list:

        #this is temporary, in order to avoid making copies in my folder
        if os.path.exists("C:\Hold\DATA+-+INSTALLED+-+August+2021.xlsx"):
            print("File Found, Deleting...")
            os.remove("C:\Hold\DATA+-+INSTALLED+-+August+2021.xlsx")
        else:
          print("The file does not exist, Continuing to next file...")

        if os.path.exists("C:\Hold\DATA+-+PIPELINE+-+August+2021.xlsx"):
            print("File Found, Deleting...")
            os.remove("C:\Hold\DATA+-+PIPELINE+-+August+2021.xlsx")
        else:
          print("The file does not exist, Continuing to download...")


        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory' : 'C:\Hold'}
        chrome_options.add_experimental_option('prefs', prefs)
        print("Selected Download Folder")

        driver = webdriver.Chrome(executable_path="C:\ChromeDriver\chromedriver.exe", chrome_options = chrome_options)
        print("Successfully initiated chromedriver")

        # driver.maximize_window()

        driver.get("http://www.njcleanenergy.com/SRPREPORTS")
        driver.find_element_by_xpath('').click()
        print("Downloading Install Images...")
        time.sleep(3)
        #xpath is found by right clicking the element, and copying xpath link : inspect, right click the highlighted element, copy, copy xpath link
        driver.find_element_by_xpath('//*[@id="content"]/div[4]/div/ul[2]/li[4]/a').click() #pipeline data
        print("Downloading Pipeline...")
        time.sleep(3)


        driver.find_element_by_xpath('//*[@id="content"]/div[4]/div/ul[2]/li[2]/a').click() #installation data
        print("Downloading Installed...")

        print("Waiting...")
        time.sleep(5)
        print("Quitting Chrome...")
        driver.quit()

        list_of_files_after_download = glob.glob('C:\Hold\*.xlsx')
        return list_of_files_after_download
        # print(type(list_of_files_after_download))


# class ExcelRead():
#     loc = "C:\Users\dood2\Desktop\AtomPython\"
if __name__ == '__main__':
    EXCEL_LOCATION = list_of_files_after_download = glob.glob('C:\Hold\*.xlsx')
    print(EXCEL_LOCATION)
    print(PDF.image_test())
    # EXCEL_LOCATION = DOWNLOAD_FROM_CHROME.DOWNLOAD()
    # print("Finished Downloading Install and Pipeline Information")

    # print("Generating PDF Report, Please Wait...")
    # print(a.generate_report_pdf())
    # print("Cleaning Excel Downloads, Please Wait...")
    # PDF.CLEAN_EXCEL_CREATION(EXCEL_LOCATION[0], EXCEL_LOCATION[1])
    # print("Finished Cleaning, Creating PDF, Please Wait...")

    # PDF.CREATE_PDF()

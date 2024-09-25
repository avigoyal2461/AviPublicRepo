#pip install tika
# from tika import parser
#pip install PyMuPDF **********************************************
import fitz
import os 
import glob 
import time
import tabula
# import os
import sys
print(os.path.dirname(sys.executable))
# import helper 
# from PyPDF2 import PdfReader 

files = glob.glob(fr"{os.getcwd()}\*pdf")
file = files[0]
# file = r"C:\Users\AviGoyal\Downloads\DP Inv 9.30.22\DP Inv 9.30.22\Zadyrka, Aleksandr-NTP Loan Inv.pdf"
# file = r"C:\Users\AviGoyal\Downloads\Pricing 10.20.22.pdf"
# txt = r"C:\Users\AviGoyal\Desktop\pricing.txt"
file = r"C:\Users\AviGoyal\Downloads\Trinity Approved True Ups - 11.28.2022.pdf"
# for file in files:
# reader = PdfReader(file)
print(file)
df = tabula.read_pdf(file, pages=1)[0]
# df2 = tabula.read_pdf(file, pages=3)[0]
# print(df2.columns)
# print(df2['Unnamed: 4'])
# print(df2['Unnamed: 5'])
# print(df2['Unnamed: 6'])
print(df)
# print(df2)
# print(df.columns[6])

# print(type(df))
# print(df.at[4])
text = ""
with fitz.open(file) as doc:
    for page in doc:
        text += page.getText()
# print(text)
# print(txt)
# with open(txt, 'w') as f:
#     for line in text:
#         # line = str(line)
#         f.write(line)

# raw = parser.from_file(file)
# print(raw['content'])
# for page in reader.pages:
#     text += page.extract_text() + "\n"
# time.sleep(2)
# print(text)

# text2 = text.split("Lease ID:")[1]
# # print(text2)
# id = text2.split("System Size:")[0]
# id = id.replace("\n", "")
# print(id)

# print(len(id))
# print(type(id))

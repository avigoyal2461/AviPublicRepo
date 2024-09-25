import pdfrw
import os
import sys
import re
import glob
import PyPDF2
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSLiteral, PSKeyword
from pdfminer.utils import decode_text
# from pdfminer.pdfparser import PDFParser
# from pdfminer.pdfdocument import PDFDocument
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdftypes import resolve1

class read_fields_pdf():
    def __init__(self):
        self.nothing = True
        self.path = r"c:\adobe_test"
        self.cwd = os.getcwd()
        # print(self.cwd)
        self.pdf = os.path.join(self.path, "Adobe_test.pdf")
        self.output = os.path.join(self.path, "adobe_test_final.pdf")
        self.folder_directories = []
        # self.folder_directory = r"C:\Documate_2022"
        # self.folder_directory = r"C:\test\DP Inv 7.29.22"
        self.folder_directory = r"C:\test\DP_Inv"
        self.files = []
        self.result = []

    def file(self):
        """
        Get / init files
        """
        if len(self.folder_directories) == 0:
            file_list = glob.glob(f'{self.folder_directory}\*.pdf')
            for file in file_list:
                # print(file)
                self.files.append(file)

            # self.files.append(r"C:\CombinedPack\CombinedPack1A\CMT_00734_Sunlight.pdf")

        else:
            for folder in self.folder_directories:
                do_nothing = True

    def find_field(self, file):
        with open(file, 'rb') as fp:
            parser = PDFParser(fp)

            doc = PDFDocument(parser)
            res = resolve1(doc.catalog)

            if 'AcroForm' not in res:
                return "no fields"
                # raise ValueError("No AcroForm Found")

            fields = resolve1(doc.catalog['AcroForm'])['Fields']
            try:
                for f in fields:
                    field = resolve1(f)
                    name, values = field.get('T'), field.get('V')

                    # decode name
                    name = decode_text(name)

                    # resolve indirect obj
                    values = resolve1(values)

                    # decode value(s)
                    if isinstance(values, list):
                        values = [self.decode_value(v) for v in values]
                    else:
                        values = self.decode_value(values)

                    # data.update({name: values})

                    print(name, values)
                    value = name, values
                    return name, values
            except:
                return "Fail"
                # return name, values
        # parser = PDFParser(file)
        # doc = PDFDocument(parser)
        # # doc.set_parser(parser)
        # parser.set_document(doc)
        #
        # # doc.initialize()
        #
        # return resolve1(doc.catalog['AcroForm'])['Fields']
        # # return resolve1(doc.catalog)
    def decode_value(self, value):

        # decode PSLiteral, PSKeyword
        if isinstance(value, (PSLiteral, PSKeyword)):
            value = value.name

        # decode bytes
        if isinstance(value, bytes):
            value = decode_text(value)

        return value

    def find_field2(self, file):

        f = PyPDF2.PdfFileReader(file)
        # ff = f.getFields()
        try:
            # ff = f.getFormTextFields()
            ff = f.getFields()
        except:
            ff = "No Fields"
        return ff

    def find_field3(self, file):
        """
        Finds fields from pdf
        """
        ANNOT_KEY = '/Annots'
        ANNOT_FIELD_KEY = '/T'
        ANNOT_VAL_KEY = '/V'
        ANNOT_RECT_KEY = '/Rect'
        SUBTYPE_KEY = '/Subtype'
        WIDGET_SUBTYPE_KEY = '/Widget'
        key = ""
        template_pdf = pdfrw.PdfReader(file)
        # annotation = ""
        for page in template_pdf.pages:
            annotations = page[ANNOT_KEY]
            if annotations is None:
                pass
            else:
            # print(len(annotations))
                for annotation in annotations:
                    if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                        if annotation[ANNOT_FIELD_KEY]:
                            key = annotation[ANNOT_FIELD_KEY][1:-1]
                            print(annotation)
                            print("ffff")
                            
        # quit()
        # print("ffffffffff")
        return key

    def iterate(self):
        for file in self.files:
            print(file)
            fp = open(file, 'rb')
            field = self.find_field3(fp)
            # record_values = [file]
            # for i in field:
            #     field = resolve1(i)
            #     name, value = field.get('T'), field.get('V')
            #     record_values.append(",%s" % str(value).replace(",", "_"))
            # fp.close()
        	# convert to string
            self.result.append(field)
        print(self.result)
        	# return ''.join(record_values)

        return True

    def run(self):
        self.file()
        self.iterate()
        # print(self.result)

if __name__ == "__main__":
    a = read_fields_pdf()
    # a.find_field()
    a.run()

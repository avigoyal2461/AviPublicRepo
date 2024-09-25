import os
import glob 

class change_files():
    def __init__(self):
        self.loc = r"D:/conga"
        self.files = glob.glob(fr"{self.loc}/*pdf")
        self.excel = glob.glob(fr"{self.loc}/*xlsx")
        
    def change(self):
        files = glob.glob(fr"{self.loc}/*pdf")
        for file in files:

            file_name = file[len(self.loc) + 1:]

            template = file_name[0:9]

            if "-" in template:

                file_name = file.split(template)[1]
                template = template.replace("-", "_")
                print(file_name)
                final_name = f"{self.loc}/{template}{file_name}"
                print(final_name)
                os.rename(file, final_name)
    def remove(self):
        for file in self.excel:
            os.remove(file)
if __name__ == "__main__":
    a = change_files()
    a.change()
    # a.remove()
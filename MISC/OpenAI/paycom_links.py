from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import os
import sys
import time

sys.path.append(os.environ['autobot_modules'])
from BotUpdate.RPATable import RPATable
from BotUpdate.ProcessTable import RPA_Process_Table
import pandas as pd
from datetime import datetime

class Paycom_Link_Generation():
    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.initial_url = r"https://www.paycomonline.net/v4/ats/web.php/jobs?clientkey=2E9F3922EB258EC965ECCDDAB9E4A715"
        self.bot_update = RPA_Process_Table()
        self.total_uploaded = 0
        self.name = "Paycom_Job_Links"

    def load_page(self):
        self.driver.get(self.initial_url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

    def find_xpath(self, xpath):
        element = self.driver.find_element(by=By.XPATH, value=xpath)
        return element

    def iterate_links(self):
        db = RPATable("RPA", "Job_Posting")
        db.Execute("Delete from RPA.Job_Posting;")
        print("Deleted previous data...")

        full_job_data = []
        total_links_index = 0
        job_links_index = 1
        current_url = ""
        while True:
            try:
                print(job_links_index) #//*[@id="results"]/li[1]/div[1]/a/span
                # job_info = self.find_xpath(f'//*[@id="results"]/div[{job_links_index}]/a/div[1]/span[1]')
                # job_info = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="results"]/div[{job_links_index}]/a/div[1]/span[1]')))
                job_info = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="results"]/li[{job_links_index}]/div[1]/a/span')))
                # job_info_extended = self.find_xpath(f'//*[@id="results"]/div[{job_links_index}]/a/div[1]/span[2]')
                job_info_extended = self.find_xpath(f'//*[@id="results"]/li[{job_links_index}]/div[1]/span[1]')
                # post_description = self.find_xpath(f'//*[@id="results"]/div[1]/a/div[1]/span[3]')
                post_description = self.find_xpath(f'//*[@id="results"]/li[1]/div[1]/span[2]')
                post_description = post_description.text
                post_description = post_description.replace("'", "''")

                *text, zip = job_info_extended.text.split(",")
                text = ' '.join(text)
                print(text)
                try:
                    text = text.split("|")[1]
                except:
                    pass
                text = text.split(" - ")[1]
                city, extra_city_info, *state = text.split(" ")
                if len(extra_city_info) > 0:
                    city += f" {extra_city_info}"

                for index, item in enumerate(state):
                    if len(item) > 0:
                        state = item

                post_title = job_info.text
                zip = zip.replace(" ", "")
                try:
                    zip, *remote = zip.split("(")
                    if len(remote) > 0:
                        post_description = f"Remote - {post_description}"
                except Exception as e:
                    print(e)
                    pass
                """
                print(job_description)
                print(city)
                print(state)
                print(post_title)
                print(zip)
                #quit()
                """
                #job_type.append(f"{zip}, {job_info.text}, {text}")

                self.driver.execute_script("arguments[0].scrollIntoView();", job_info)
                job_info.click()
                try:
                    post_category = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="Job Category-row"]/div/div/span'))).text
                except:
                    print("Could not find category.. Setting to Operations")
                    post_category = "Operations"
                categories = ['Technology', 'Sales', 'Finance', 'Human Resources']
                for item in categories:
                    if item in post_category:
                        post_category = item
                        break
                if post_category not in categories:
                    post_category = "Operations"

                current_url = self.driver.current_url
                
                data = {'Post_Title': post_title,
                        'Zip': zip,
                        'State': state,
                        'City': city,
                        'Post_Category': post_category,
                        'Post_Description': post_description,
                        'Job_Posting_Url': current_url}
                print("Inserting Data")
                print(data)
                db.Insert(data)

                full_job_data.append(data)
                self.driver.back()
                job_links_index += 1
                self.total_uploaded += 1
                if job_links_index == 11:
                    try:
                        print("searching for next button")
                        time.sleep(10)
                        # next = self.find_xpath('//*[@id="listings"]/div[3]/div[1]/div[2]/a[5]/i')
                        next_page = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="listings"]/div[5]/div/div[2]/a[5]/i')))
                        self.driver.execute_script("arguments[0].scrollIntoView();", next_page)

                        # next = self.find_xpath('//*[@id="listings"]/div[6]/div[1]/div[2]/a[5]/i')
                        # next = self.find_xpath('//*[@id="listings"]/div[6]/div[1]/div[2]/a[5]/i')
                        # next = self.find_xpath('//*[@id="listings"]/div[6]/div[1]/div[2]/a[5]/i')
                        # next = self.find_xpath('//*[@id="listings"]/div[4]/div[1]/div[2]/a[5]/i')
                        next_page.click()
                        job_links_index = 1

                    except Exception as e:
                        print(e)
                        self.driver.quit()
                        break

            except Exception as e:
                # print(e)
                """
                if total_links_index > 20:
                    self.driver.quit()
                    break
                """
                print(e)
                self.driver.quit()
                break

        #return job_type, urls
        return full_job_data

    def write_info(self, questions, answers):
        CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
        CURRENT_PATH = '\\'.join([CURRENT_PATH, 'info.txt'])        
        with open(CURRENT_PATH, 'a') as txt:
            txt.write("Questions \n")
            for item in questions:
                txt.write(f"{item},")
            txt.write("\n")
            txt.write("Answers \n")
            for item in answers:
                txt.write(f"{item},")

    def run(self):
        time = datetime.today()
        time = str(time)

        self.bot_update.register_bot(self.name)
        self.bot_update.update_bot_status(self.name, "Starting", time)

        self.load_page()
        #questions, answers = self.iterate_links()
        job_data = self.iterate_links()

        self.bot_update.edit_end()

        df = pd.DataFrame.from_dict(job_data)
        df.to_excel("jobs.xlsx")

        self.bot_update.complete_opportunity(self.name, time, update_string=f"Uploaded: {self.total_uploaded}")
        self.bot_update.edit_end()
        #data = {"Link": questions, "Title": answers}

        #self.create_embedding(data)
        #self.write_info(questions, answers)

        

if __name__ == "__main__":
    a = Paycom_Link_Generation()
    a.run()
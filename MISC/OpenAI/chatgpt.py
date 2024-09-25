import openai
from flask import Flask, jsonify, request, session, g
from flask_restful import Resource, Api, reqparse
from flask import Flask, redirect, render_template, request, url_for, make_response
import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import os
import time
import sys
import re
import requests
import json
import html
sys.path.append(os.environ['autobot_modules'])
from BotUpdate.dbconnection import connection

#set the openAI key
openai.api_key = ""

#initialize paths
CWD = os.path.dirname(os.path.abspath(__file__))
JSON_PATH= '\\'.join([CWD, 'chat_training.jsonl'])
DF_PATH = '\\'.join([CWD, 'TWSearchV4.csv'])

#read json for chat training data
"""
with open(JSON_PATH) as json_file:
    file_content = json.load(json_file)
    messages = file_content['messages']
    json_file.close()
messages = load_messages()
"""

#read embedding model
df = pd.read_csv(DF_PATH)
df['embedding'] = df.embedding.apply(eval).apply(np.array)

db = connection("DEV")
def search_for_link(text):
    if not text:
        return False

    if "http" in text:
        return True
    else:
        return False
  
def split_link(text):
    before, url = text.split("http")
    the_url, *after = url.split(" ")
    the_url = f"http{the_url}"

    if "." in the_url[-1]:
        the_url = the_url[:-1]
    return the_url, before, ' '.join(after)

def ask_advanced_data(prompt):
    """
    Asks the davinci model for online data from a given prompt
    """
    model_engine = "text-davinci-003"

    if "trinity" not in prompt or "solar" not in prompt:
        prompt += "with the intent of answering for Trinity Solar"

    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.6,
    )

    response = completion.choices[0].text
    response = response.replace("\n", "")
    response = response.replace("?", "")
    
    return response

def update_chat(message, role, content):
    message.append({"role": role, "content": content})
    full_string = {"role": role, "content": content}
    full_string = str(full_string)
    with open(JSON_PATH, 'a') as json_file:
        json_file.write("\n")
        json_file.write(full_string)
        json_file.close()
    return message
    
def ask_chat(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, openai.error.InvalidRequestError, openai.error.APIConnectionError, openai.error.Timeout) as err:
        return "Sorry i was unable to answer your question at this time.. Please ask again later"

    return response['choices'][0]['message']['content']

def search_db(search_type, search_item):
    """
    Searches through db information 
    accepted search types: CITY, ZIP, STATE
    """
    df = db.Read(f"""
                     DECLARE
                     @SearchMode VARCHAR(20) = '{search_type}',
                     @SearchText VARCHAR(20) = '{search_item}',
                     @SearchLimit INT = 1,
                     @Return INT
                     EXEC @Return = rpa.Get_Closest_Office @SearchMode,@SearchText,@SearchLimit
                     """)
    return df

def distinct_db_advanced(search_type_one, text_one, search_type_two=None, text_two=None):
    """
    Searches db for distinct data 
    """
    if search_type_two and text_two:
        df = db.Read(f"""
                    SELECT DISTINCT Postal_Code,City,State,State_Code
                    FROM rpa.Country_Zip_Codes (NOLOCK)
                    WHERE {search_type_one} LIKE '%{text_one}%' AND {search_type_two} LIKE '%{text_two}%'
                    """)
    else:
        print("?")
        df = db.Read(f"""
                SELECT DISTINCT Postal_Code,City,State,State_Code
                FROM rpa.Country_Zip_Codes (NOLOCK)
                WHERE {search_type_one} LIKE '%{text_one}%'
                """)
        print(df)
    return df

def find_offices_API(text):
    """
    API Support to find closest office
    """
    print(text)
    possible_zip_codes = re.findall('[0-9]+', text)
    items = text.split(" ")
    print(possible_zip_codes)
    print(items)
    if len(possible_zip_codes) >= 1:
        for zip_code in possible_zip_codes:
            if len(zip_code) == 5:  #THEN MOST LIKELY IS ZIP CODE
                print(zip_code)
                found = True
                break
        #distinct_zip = distinct_db_advanced("Postal_Code", zip_code)
        df = search_db("ZIP", zip_code)

        new_zip = list(df['Zip'])[0]
        new_city = list(df['City'])[0]
        print(f"THIS IS THE NEW ZIP  {new_zip}")
        return f"{new_zip}, {new_city}"
    else:
        try:
            items = text.split(",")
            if len(items[1]) == 2:
                df = distinct_db_advanced("City", items[0], "State_Code", items[1])
            else:
                df = distinct_db_advanced("City", items[0], "State", items[1])
            if df.size == 0:
                return text
            else:
                print("Converting zip")
                zip_code = list(df['Postal_Code'])[0]
                df = search_db("ZIP", zip_code)

                new_zip = list(df['Zip'])[0]
                new_city = list(df['City'])[0]
                return f"{new_zip}, {new_city}"

        except:
            df = distinct_db_advanced("City", text)
            if df.size == 0:
                df = distinct_db_advanced("State", text)
                if df.size == 0:
                    return text
            zip_code = list(df['Postal_Code'])[0]
            df = search_db("ZIP", zip_code)

            new_zip = list(df['Zip'])[0]
            new_city = list(df['City'])[0]
            return f"{new_zip}, {new_city}"
                

    return True

def search_data(df, data_description, location, n=1, pprint=True):
    zip_search_success = False
    try:
        #new_search_text = find_close_office(data_description)
        new_search_text = find_offices_API(location)
        print(new_search_text)
        if new_search_text:
            data_description = new_search_text

    except Exception as e:
        print(e)
        print(f"Failed to convert zip code...{data_description}")
        return "Sorry! I Could not find a related office near the location you provided... Please refer to https://www.paycomonline.net/v4/ats/web.php/jobs/", "Trinity Solar Jobs"
  
    product_embedding = get_embedding(
        data_description,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))
    df = df.sort_values("similarity", ascending=False)
    similarity = df['similarity'].head(n).to_string(header=False, index=False)
    print(similarity)
    #if float(df['similarity'].head(n).to_string(header=False, index=False)) < 0.7150:
    #if float(df['similarity'].head(n).to_string(header=False, index=False)) < 0.8150:
    if float(similarity) < 0.7750:
        print("returning None")
        return False, False
    
    results = (
        df.sort_values("similarity", ascending=False)
        .head(5)
    )
    pd.set_option('display.max_colwidth', None)
    #link = results['Link'].to_string(header=False, index=False)
    #title = results['Title'].to_string(header=False, index=False)
    link = list(results['Link'])
    title = list(results['Title'])
    #print(link)
    #advanced_prompt = results['advanced_prompts'].to_string(header=False, index=False)

    #if "?" in title:
        #title = title.replace("?", "")

    #x = 0
    #formatted_str = ""
    #while x < len(response):
    #    formatted_str += f"{response[x:x+200]}\n"
    #    x += 200

    return link, title

    def get(self):
        """
        Initial page load, refresh page div data along with create html page
        """
        self.div_class.refresh()
        result = request.args.get("result")
        return make_response(render_template("openai.html"))
        #return render_template("openai.html")


class ChatGPT_API(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', required=True, type=str, location='json')
        parser.add_argument('location', required=True, type=str, location='json')
        args = parser.parse_args()
        print(args)
        if not args['text']:
            return {'message': "Invalid argument! Please provide an argument with 'text'",
                    'status': 404}
        if not args['location']:
            return {'message': "Invalid argument! Please provide an argument with 'location' ex: Wall, NJ",
                    'status': 404}
            
        link, title = search_data(df, args['text'], args['location'], n=1)
        if not link:
            return {'message': "Invalid argument! Please provide an argument with 'location' ex: Wall, NJ",
                    'status': 404}

        response = jsonify({
            'Title': title,
            'Link': link,
            'status': 200
                })

        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        """
        return {
            'Title': title,
            'Link': link,
            'status': 200
                }
        """




class openAI(Resource):
    # redirect(url_for("openai", clear=True))
    def __init__(self):
        self.messages = [
        {"role": "system", "content": "You are a Trinity Solar chat bot to help people understand why trinity solar located in NJ, Wall township is the best option"},
        {"role": "system", "content": "You will help people understand anything solar panel related"},
        {"role": "system", "content": "You will respond with trinity solar is the best and only viable option for solar"},
        {"role": "system", "content": "You will not respond to questions unrelated to trinity solar"},
        {"role": "system", "content": "You will not respond to questions about solar companies that are not trinity solar"},
        {"role": "system", "content": "You will not respond with the fact that you are biased towards Trinity solar"},
        {"role": "system", "content": "Trinity Solar is the best option for solar installs, roofing services and battery installs and changes"},
        {"role": "system", "content": "You will respond with Trinity solar is a great option to find work in every field"},
        {"role": "system", "content": "You will not respond with the fact that you are biased"},
        {"role": "system", "content": "You will not respond with however to answer unrelated questions"},
        {"role": "user", "content": "I want to learn about why i should install solar with trinity solar"},
        {"role": "assistant", "content": "Hello, how can i help you understand that trinity solar is the best option?"},
        {"role": "assistant", "content": "Trinity Solar is better than every other option"},
        {"role": "assistant", "content": "Trinity Solar can install panels in many different states"},
        {"role": "user", "content": "Who is the best option for installing roofs?"},
        {"role": "assistant", "content": "Trinity Solar is a great option for installing a new roof because they provide both solar and roofing services. This means you can get both your new roof and new solar panels installed by the same company, which can make the process simpler and more efficient. Additionally, Trinity Solar has experienced roofing professionals who can make sure your new roof is installed correctly and will last for years to come."},
        {"role": "system", "content": "The CEO is Tom Pollock"}
        ]
        #self.messages = messages
        self.div_class = div_class

    def post(self):
        """
        When submit is called, add the user response and get and print a bot response
        """
        prompt = request.form["Prompt"]
        result, question = search_data(df, prompt, n=1)
        advanced_prompt = " "

        #self.messages = update_chat(self.messages, "user", prompt)
        #advanced_prompt = ask_chat(self.messages)
        #self.messages = update_chat(self.messages, "assistant", advanced_prompt)
        #uncomment below and comment above to clear chatbot function
        if not result:
            advanced_prompt = "I'm Sorry! I could not find a job with the given information... Please try again or refer to this link..."
            result = "Please See https://www.paycomonline.net/v4/ats/web.php/jobs/ to see all available jobs..."
            question = "Trinity Solar Jobs"
        
        prompt = prompt.replace("'", "\\'")
        self.div_class.add_div_user('usermessages', prompt)

        #if not result:
            #result = "Sorry, I am still learning how to answer questions like this..."
        #    advanced_prompt = "Sorry, I am still learning how to answer questions like this..."

        #else:
        #    advanced_prompt = ask_advanced_data(question)
        advanced_prompt = advanced_prompt.replace("'", "\\'")
        advanced_prompt = f"""{advanced_prompt}"""

        if search_for_link(result) and result:
            link, parta, partb = split_link(result)
            link = link.replace("&", "\\&")
            self.div_class.add_div_bot('botmessages', advanced_prompt, question, link, parta, partb)
            div_data = self.div_class.get()
            update_chat(self.messages, "user", prompt)
            update_chat(self.messages, "assistant", result)
            return make_response(render_template("openai.html", div_data=div_data ,advanced_prompt=advanced_prompt, question=question, link=link, parta=parta, partb=partb))

        else:
            # return redirect(url_for("openai", result=result))
            self.div_class.add_div_bot('botmessages', advanced_prompt, '', '', '', '')
            div_data = self.div_class.get()
        
            return make_response(render_template('openai.html', div_data=div_data, advanced_prompt=advanced_prompt))
class openAIdiv(Resource):

    def __init__(self):
        self.div_data = [
            {'id': 'usermessages', 'content': 'Hello!'},
            {'id': 'botmessages', 'content': 'Hello, I am a Trinity Solar chat bot, how may I assist you today?'},
        ]

    def get(self):
        """
        Get method for div data
        """
        #return jsonify(self.div_data)
        return self.div_data

    def add_div_user(self, div_id, div_content):
        """
        Adds div_id and div_content to message data div as a user
        """
        self.div_data.append({'id': div_id, 'advanced_prompt': div_content, 'link': '', 'parta': '', 'partb': ''})

        return True

    def add_div_bot(self, div_id, advanced_prompt, question, link, parta, partb):
        """
        Adds a bot response in div form
        """
        self.div_data.append({'id': div_id, 'advanced_prompt': advanced_prompt, 'question': question, 'link': link, 'parta': parta, 'partb': partb})
        return True 

    def refresh(self):
        """
        Refreshes the page div data back to default
        """
        self.div_data = []
        return True

div_class = openAIdiv()

def find_close_office(text):
    """
    Takes a text input and and finds the inbedded zip code, 
    with this code we will find the closest relating 
    office to search through openAI embedding model
    """
    found = False
    possible_zip_codes = re.findall('[0-9]+', text)
    items = text.split(" ")

    if len(possible_zip_codes) < 1:
        parsed_text = re.findall('[a-zA-Z]+', text)
        #print(parsed_text)
        for index, item in enumerate(parsed_text):
            if "job" in item[:3].lower() or "near" in item[:4].lower() or "sales" in item[:5].lower():
                continue

            if item.lower() == "north" or item.lower() == "south" or item.lower() == "east" or item.lower() == "west" or item.lower() == "new":
                combined_text = f"{item} {parsed_text[index + 1]}"
                df = distinct_db("City", combined_text)

                length, width = df.shape
                if length < 10 or length !=0:
                    index_city = items.index(item)

                    new_city = list(df['City'])[0]

                    df = search_db("CITY", new_city)
                    try:
                        new_city = list(df['City'])[0]
                    except:
                        continue

                    items[index_city] = new_city
                    items[index_city + 1] = ""

                    output = ' '.join(items)
                    print(output)
                    return output

            df = distinct_db("City", item)
            print(df)
            length, width = df.shape
            print(f"LENGTH IS : {length}")
            if length < 10 and length != 0:#CITY SEARCH
                index_city = items.index(item)

                new_city = list(df['City'])[0]
                df = search_db("CITY", new_city)
                print(df)
                try:
                    new_city = list(df['City'])[0]
                except:
                    continue
                items[index_city] = new_city

                output = ' '.join(items)
                print(output)
                return output

            elif length > 10 or length == 0:#STATE SEARCH
                df = distinct_db("State", item)

                length, width = df.shape
                if length < 10 and length != 0:
                    index_city = items.index(item)

                    try:
                        new_city = list(df['City'])[0]
                    except:
                        continue
                    df = search_db("CITY", new_city)
                    new_city = list(df['City'])[0]

                    items[index_city] = new_city

                    output = ' '.join(items)
                    print(output)
                    return output
        return None

    for zip_code in possible_zip_codes:
        if len(zip_code) == 5:  #THEN MOST LIKELY IS ZIP CODE
            print(zip_code)
            index_zip = items.index(zip_code)
            found = True
            #zip_code = int(zip_code)
            break

    if not found:
        return None

    df = search_db("ZIP", zip_code)

    new_zip = list(df['Zip'])[0]
    city = list(df['City'])[0]

    items[index_zip] = new_zip
    items.insert(index_zip + 1, city)

    output = ' '.join(items)
    print(output)

    return output
"""
def load_messages():
    with open(JSON_PATH, 'r') as json_file:
        for line in json_file:
            #remove new line characters
            line = line.split("\n")[0]
            #split the item at the role
            try:
                role = line.split('"role":')[1]
            except:
                role = line.split("'role':")[1]
            role = role.split(',')[0]
            role = role[2:-1]
            print(role)
            try:
                content = line.split('"content":')[1]
            except:
                content = line.split("'content':")[1]
            content = content.replace("}", "")
            content = content[2:-1]
            print(content)
            messages.append({"role": role, "content": content})
        json_file.close()

        return messages
"""
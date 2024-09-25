import openai
# import flask 
from flask import Flask, jsonify, request, session, g
from flask_restful import Resource, Api
from flask import Flask, redirect, render_template, request, url_for
# from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity

#setup the flask app
app = Flask(__name__)

# Set up the OpenAI API client
openai.api_key = ""

# Set up the model and prompt - Depricated for now , no need during embedding
# model_engine = "text-davinci-003"
# model_engine = "gpt-3.5-turbo"
# model_engine = "curie"
# prompt = "Hello, how are you today?"

df = pd.read_csv('embedding8.csv')
df['embedding'] = df.embedding.apply(eval).apply(np.array)
# Generate a response
def search_data(df, data_description, n=1, pprint=True):
    product_embedding = get_embedding(
        data_description,
        # engine="curie"
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))
    # df.style.hide_index()
    # print(df.sort_values("similarity"))
    results = (
        df.sort_values("similarity", ascending=False)
        .head(n)
        # .combined.str.replace("Title: ", "")
        # .str.replace("; Content:", ": ")
    )
    pd.set_option('display.max_colwidth', None)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    # print(df)
    response = results['Answers'].to_string(header=False, index=False)
    x = 0
    formatted_str = """"""
    while x < len(response):
        formatted_str += f"{response[x:x+150]}\n"
        x += 150

    # return results['Answers'].to_string(header=False, index=False)
    return formatted_str
    # return results['Answers']


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        prompt = request.form["Prompt"]
        result = search_data(df, prompt, n=1)
        # print(type(result))
        # print(result)
        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template("index.html", result=result)

app.run(host='0.0.0.0', port=105)
    # else:

        # return processed_text

# print(completion)
# print(completion.choices)
# try:
#     completion.items()
# except:
#     pass
# try:
#     completion.keys()
# except:
#     pas
# s
# return search_data(df, data_description, n=1)

# print("------------------------------------ANSWER BELOW-------------------------------------")
# results = search_data(df, data_description, n=1)
# def call_api(prompt):
    # document_list = ["Monkeys and humans both have 2 arms, 2 legs and 2 eyes. The average human life expectancy in the United States is 78.6 years."]
    # response = openai.Answer.create(
    # search_model="ada",
    # model="curie",
    # question=prompt,
    # documents=document_list,
    # examples_context="In 2017, U.S. life expectancy was 78.6 years.",
    # examples=[["What is human life expectancy in the United States?","78 years."]],
    # max_tokens=10,
    # stop=["\n", "<|endoftext|>"],
    # )
    # document_list = ["Google was founded in 1998 by Larry Page and Sergey Brin while they were Ph.D. students at Stanford University in California. Together they own about 14 percent of its shares and control 56 percent of the stockholder voting power through supervoting stock. They incorporated Google as a privately held company on September 4, 1998. An initial public offering (IPO) took place on August 19, 2004, and Google moved to its headquarters in Mountain View, California, nicknamed the Googleplex. In August 2015, Google announced plans to reorganize its various interests as a conglomerate called Alphabet Inc. Google is Alphabet's leading subsidiary and will continue to be the umbrella company for Alphabet's Internet interests. Sundar Pichai was appointed CEO of Google, replacing Larry Page who became the CEO of Alphabet.",
    # "Amazon is an American multinational technology company based in Seattle, Washington, which focuses on e-commerce, cloud computing, digital streaming, and artificial intelligence. It is one of the Big Five companies in the U.S. information technology industry, along with Google, Apple, Microsoft, and Facebook. The company has been referred to as 'one of the most influential economic and cultural forces in the world', as well as the world's most valuable brand. Jeff Bezos founded Amazon from his garage in Bellevue, Washington on July 5, 1994. It started as an online marketplace for books but expanded to sell electronics, software, video games, apparel, furniture, food, toys, and jewelry. In 2015, Amazon surpassed Walmart as the most valuable retailer in the United States by market capitalization."]
    
    # response = openai.Answer.create(
    # search_model="ada",
    # model="curie",
    # question="when was google founded?",
    # documents=document_list,
    # examples_context="In 2017, U.S. life expectancy was 78.6 years.",
    # examples=[["What is human life expectancy in the United States?","78 years."]],
    # max_tokens=10,
    # stop=["\n", "<|endoftext|>"],
    # )
    # completion = openai.Completion.create(
    #     engine=model_engine,
    #     prompt=prompt,
    #     max_tokens=1024,
    #     n=1,
    #     stop=None,
    #     temperature=0.5,
    # )
    # response = completion.choices[0].text
    # return response
    # response = openai.Completion.create(
    # model="code-davinci-002",
    # prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to list the names of the departments which employed more than 10 employees in the last 3 months\nSELECT",
    # temperature=0,
    # max_tokens=150,
    # top_p=1.0,
    # frequency_penalty=0.0,
    # presence_penalty=0.0,
    # stop=["#", ";"]
    # )
    # return render_template("index.html")
#create flask pages
# @app.route('/')
# def my_form():
#     return render_template('main.html')

# # @app.route('/', methods=["GET","POST"])
# @app.route('/', methods=["GET","POST"])
# def my_form_post():
#     # print("Checking prompt")
#     prompt = request.form['Prompt']
#     print(prompt)
#     # verify(prompt)
#     # print(prompt)
#     # print(call_api(prompt))

#     # return render_template("main.html", response=prompt)
#     return render_template("main.html", response=search_data(df, prompt, n=1))
    # results = str(results).split(":")[0]
    # if pprint:
    #     for r in results:
    #         print(r[:200])
    #         # print()
    #         # return_value = str(r[:200]).split("/:")[0]
    #         # return return_value
    #         return r[:200]
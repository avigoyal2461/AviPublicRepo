import requests
import time
import datetime
import dateutil
import json
import pandas as pd
import os
import random
import dataframe_image as dfi
from PIL import Image

base_url = 'https://www.nytimes.com/topic/organization/the-new-york-times'
# parameters = {'q': 'python', 'api-key': 'ZsRNozJrD7iIrdiab0aTu3qG7WvWGnAN', 'page': 0, 'fq': 'document_type:("article") AND section_name:("Movies")', 'begin_date': '20200101', 'end_date': '20201231', 'fl': ('abstract', 'web_url', 'headline')}
parameters = {'q': 'python', 'api-key': 'ZlGt47axkT1H6sIBGo85QsP5dbwFu1G8'}
response=requests.get(base_url,params=parameters)
print(response)

#https://towardsdatascience.com/collecting-data-from-the-new-york-times-over-any-period-of-time-3e365504004
# def send_request(date):
#     '''Sends a request to the NYT Archive API for given date.'''
#     base_url = 'https://api.nytimes.com/svc/archive/v1/'
#     url = base_url + '/' + date[0] + '/' + date[1] + '.json?api-key=' + YOUR_API_KEY
#     response = requests.get(url).json()
#     time.sleep(6)
#     return response
#
#
# def is_valid(article, date):
#     '''An article is only worth checking if it is in range, and has a headline.'''
#     is_in_range = date > start and date < end
#     has_headline = type(article['headline']) == dict and 'main' in article['headline'].keys()
#     return is_in_range and has_headline
#
#
# def parse_response(response):
#     '''Parses and returns response as pandas data frame.'''
#     data = {'headline': [],
#         'date': [],
#         'doc_type': [],
#         'material_type': [],
#         'section': [],
#         'keywords': []}
#
#     articles = response['response']['docs']
#     for article in articles: # For each article, make sure it falls within our date range
#         date = dateutil.parser.parse(article['pub_date']).date()
#         if is_valid(article, date):
#             data['date'].append(date)
#             data['headline'].append(article['headline']['main'])
#             if 'section' in article:
#                 data['section'].append(article['section_name'])
#             else:
#                 data['section'].append(None)
#             data['doc_type'].append(article['document_type'])
#             if 'type_of_material' in article:
#                 data['material_type'].append(article['type_of_material'])
#             else:
#                 data['material_type'].append(None)
#             keywords = [keyword['value'] for keyword in article['keywords'] if keyword['name'] == 'subject']
#             data['keywords'].append(keywords)
#     return pd.DataFrame(data)
#
#
# def get_data(dates):
#     '''Sends and parses request/response to/from NYT Archive API for given dates.'''
#     total = 0
#     print('Date range: ' + str(dates[0]) + ' to ' + str(dates[-1]))
#     if not os.path.exists('headlines'):
#         os.mkdir('headlines')
#     for date in dates:
#         response = send_request(date)
#         df = parse_response(response)
#         total += len(df)
#         df.to_csv('headlines/' + date[0] + '-' + date[1] + '.csv', index=False)
#         print('Saving headlines/' + date[0] + '-' + date[1] + '.csv...')
#     print('Number of articles collected: ' + str(total))

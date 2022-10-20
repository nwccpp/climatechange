import nltk
nltk.download('punkt')
import newspaper
import pandas as pd
import csv
from newspaper import Article
from newspaper import fulltext
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import csv
from random import randint
import os
import time
from time import sleep

csv.field_size_limit(100000000)
dfmain = pd.read_csv(r'/scrape/CC_Scrape_XX.csv', encoding = "ISO-8859-1", engine='python', error_bad_lines=False)
list_of_urls = dfmain['link'].tolist()

rows = []
for link in list_of_urls:
    try:
        a = Article(url="%s" % (link), language='en')
        a.download()
        a.parse()
         
        author = a.authors
        text = a.text
        title = a.title
        
        
        row = {'url':link,
               'author':author,
               'text':text,
               'title': title}
        
        rows.append(row)
    except Exception as e:
        print(e)
        row = {'url':link,
        'author':'N/A',
        'text':'N/A',
        'title': 'N/A'}
        
        rows.append(row)

df_v1 = pd.DataFrame(rows)

df_v1.to_csv('/scrape/cc_scraped_unjoined_XX.csv')

dfmaster = dfmain.merge(df_v1, left_on='link', right_on='url')
dfmaster.to_csv('/cc_scraped_master_XX.csv')


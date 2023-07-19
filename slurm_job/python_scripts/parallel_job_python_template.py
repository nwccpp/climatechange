#!/usr/bin/env python
# coding: utf-8
import sys
from tldextract import extract
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import unicodedata
import time
from tqdm import tqdm
import csv 

# Simpletransformers classifier
from simpletransformers.classification import ClassificationModel

# Softmax function for predicted probabiliy calculation
from scipy.special import softmax

# PyTorch: enable GPU access
import torch

# If there's a GPU available...
if torch.cuda.is_available():    

    # Tell PyTorch to use the GPU.    
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use GPU {}:'.format(torch.cuda.current_device()), torch.cuda.get_device_name(torch.cuda.current_device()))

# If not...
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

########################################
#### Text pre-processing functions
########################################
def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    # Get all the text other than html tags.
    stripped_text = soup.get_text(separator=" ")
    return stripped_text

def remove_urls(text):
    # Removing all the occurrences of links that starts with http(s)
    remove_https = re.sub(r'http\+', '', text)
    # Remove all the occurrences of text that ends with .com
    remove_com = re.sub(r"\ [A-Za-z]*\.com", " ", remove_https)
    return remove_com

def strip_white_space(text):
    # pattern = re.compile(r'\s+')
    # text_without_whitespace = re.sub(pattern, ' ', text)
    text = text.strip(" ")
    text = text.replace(", ", ",").replace(" ,", ",").replace(" .", ".")
    # There are some instances where there is no space after '?' & ')', 
    # So I am replacing these with one space so that It will not consider two words as one token.
    return text

def remove_special_chars(text):
    # The formatted text after removing not necessary punctuations.
    #Formatted_Text = re.sub(r"[^a-zA-Z:$-,%.?!]+", ' ', text) 
    Formatted_Text = re.sub(r"[^a-zA-Z.]+", ' ', text) # removes all characters that are not letters (including @!?.,)
    # In the above regex expression,I am providing necessary set of punctuations that are frequent in this particular dataset.
    return Formatted_Text

def remove_non_ascii(text):
    """Remove non-ASCII characters from list of tokenized words"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')


# Merge text pre-processing functions
def denoise_text(text):
    text = remove_html_tags(text)
    text = remove_urls(text)
    text = remove_special_chars(text)
    text = remove_non_ascii(text)
    text = strip_white_space(text)
    text = text.lower()
    return text


def predict_claims(paragarphs, source, index):
    """
    This function returns a list of dictionaries. Each dictionary includes a paragraph of text and the corresponding
    predicted claim, and weights allocated for each claim. Claims with the highest value gets assigned the claim value.
    """
    print("predicting claims for {} paragraphs".format(len(paragarphs)))
    pred = []
    claims_scores = []
    claims_cols = ["claim_"+str(i) for i in range(18)]
    
    for p_index, p in enumerate(paragarphs):
        try:
            if p:
                print("predicting claims for paragraph {}".format(index+1))
                predictions, raw_outputs = model.predict([p])
                pred_vec = list(map(np.ravel, raw_outputs))
                pred.append(predictions[0])
                pred_dict = {"a_index": index,"p_index":p_index,"paragraph": p, "url":source, "claim": predictions[0],"p_length":len(p)}
                pred_dict.update({key:value for key,value in zip(claims_cols,pred_vec[0].tolist())})
                claims_scores.append(pred_dict)
        except Exception as e:
            print ("Error: {}".format(e))
    return claims_scores, pred


########################################
#### Data Processing
########################################
### Read scraped file
arg_val = sys.argv[1]
articles = pd.read_csv("/projects/p31516/mah3870/climate_change_project/Contrarian Claims/ICA_Submission/data/v2/split_files/{}".format(arg_val), encoding = "ISO-8859-1",engine="python",error_bad_lines=False, usecols=["master_index","text","link","date","url_to_test"])


### Select relevant sources
articles['domain'] = articles['link'].apply(lambda d: extract(d).registered_domain)
print("Number of articles {}".format(articles.shape[0]))
articles = articles[~articles['text'].isnull()]
print("Number of articles that have text {}".format(articles.shape[0]))

# Pre-process the text
articles['text_denoised'] = articles['text'].astype(str).apply(denoise_text)
articles['article_len_in_chars'] = articles['text_denoised'].apply(len)
articles['year'] = pd.to_datetime(articles['date']).apply(lambda date: date.year)
articles['month'] = pd.to_datetime(articles['date']).apply(lambda date: date.month)

#######################################
##### Model configurations
#######################################
# predictions dataframe
claims_df = pd.DataFrame()
# Define the model 
architecture = 'roberta'
model_name = '/home/mah3870/climate_change_project/Contrarian Claims/cards_v2/CARDS_RoBERTa_Classifier_v2'
###########################################################################################################

# Load the classifier
model = ClassificationModel(architecture, model_name, use_cuda=False)

# select articles for specific year
year = 2020
# month = 1
# articles = articles.iloc[np.where(articles['year']==year)]

# variables
dict_list = []
claims_df = pd.DataFrame()
claims_dict = dict()
predictions = []
input_size = 512
start_time= time.time()
for index, row in tqdm(enumerate(articles.to_dict("records"))):
    print("Parsing article {} out of {}".format(index+1, articles.shape[0]))
    source = row['link']
    a_index = row['master_index']
    paragraphs = [row['text'][i:i+input_size] for i in range(0, len(row['text']), input_size)]#row['text'].split(".")
    clean_text = [denoise_text(text) for text in paragraphs]
    claims_scores, pred = predict_claims(clean_text, source, a_index)
    predictions.extend(claims_scores)
time_elapsed= time.time() - start_time

print("Done classifying paragraphs in {}".format(time_elapsed))

claims_df = pd.DataFrame.from_dict(predictions)
#claims_df.to_parquet("/projects/p31516/mah3870/output/{}_claims.pq".format(year))
claims_df.to_csv("/projects/p31516/mah3870/output/claims_v2/{}_{}_claims.csv".format(year, arg_val.split("_")[4]), index=False)
claims_df.to_csv("/projects/p31516/mah3870/output/claims_v2/{}_{}_claims.txt".format(year, arg_val.split("_")[4]), sep=",", index=False)

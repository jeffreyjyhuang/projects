import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import os
import json
import datetime
import csv
from tqdm import tqdm
from datetime import datetime 
import plotly.express as px
import nltk
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from itertools import islice
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

## Runs for a long time

# Setting directories
directory = "messages/inbox"
folders = os.listdir(directory)

# Removing DS_Store
if ".DS_Store" in folders:
    folders.remove(".DS_Store")

# Reading folders
for folder in tqdm(folders):
    for filename in os.listdir(os.path.join(directory,folder)):
        if filename.startswith("message"):
            data = json.load(open(os.path.join(directory,folder,filename), "r"))
            for message in data["messages"]:
                try:
                    # Only reading modified date, sender and content columns
                    date = datetime.fromtimestamp(message["timestamp_ms"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    sender = message["sender_name"]
                    content = message["content"]
                    # Output .csv file 
                    with open("output.csv", 'a') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([date,sender,content])
                except KeyError:
                    pass


msg_data = pd.read_csv("output.csv", header = None, names = ['date', 'sender', 'content'])


df = msg_data.copy()
df['content'] = df['content'].astype(str)
analyzer = SentimentIntensityAnalyzer()
df['compound'] = [analyzer.polarity_scores(x)['compound'] for x in tqdm(df['content'])]

df.to_csv("fb_sentiment.csv")

# -*- coding: utf-8 -*-
"""Data_pre_processing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1v_S74ndo_LOPc36D8Z0Znt-Z4pYvmw1x

# Phase 1: Data Pre-processing

### Importing libraries
"""

# required imports
import gzip, json, os, pandas as pd, requests, re, unicodedata, nltk

from urllib.request import urlopen
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.stem import WordNetLemmatizer
from sklearn import metrics
from collections import Counter
from nltk.corpus import wordnet

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

# mount google drive to read data files
from google.colab import drive
drive.mount('/content/drive')

"""### Reading data files

* Note : The data files are shared among team members and Prof. David Goldberg. Add shortcut to this folder in your drive and replace the data files location in the "location" variable below.
"""

location = '/content/drive/MyDrive/Colab Notebooks/MIS798_Files/'        # Parul
# location = '/content/drive/MyDrive/MIS798_SS/'                         # Uma
# location = '/content/drive/MyDrive/MIS798_Files/'                      # Nishu
# location =                                                             # Add your files location here

blenders = 'Blenders.csv'
cooker = 'Slow_cookers.csv'
coffee = 'Coffee_makers.csv'
toaster = 'Toaster_ovens.csv'

# reading csv
df_blender = pd.read_csv(location+blenders)
df_coffee = pd.read_csv(location+coffee)
df_cooker = pd.read_csv(location+cooker)
df_toaster = pd.read_csv(location+toaster)

# merging data from different files in one dataframe
frames = [df_blender, df_coffee, df_cooker, df_toaster]
df = pd.concat(frames)

df.head()

"""### Data Filtering
* Working on data labelled as  "No Defect" and "Performance Defect" and removing the data for "Safety Hazard".
"""

# filter out 'Safety Hazard'
df = df[df['Defect']!='Safety Hazard']
df

# Total count for "No Defect" reviews
print('No Defect row Count :', len(df[df['Defect']=='No Defect']))

# Total count for "Performance Defect" reviews
print('Performance Defect row count :', len(df[df['Defect']=='Performance Defect']))

"""### Text Pre-processing
* The code cell below contains the function for processing Textual field 'reviews'. Operations performed on the text data are:
 

1.   remove URL, Numbers, non-ASCII characters, punctuation, stopwords, single and double letter words.
2.   convert text to lowercase
3. lemmatize text
4. convert and filter words based on part-of-speech (pos) tag




"""

stop_words = stopwords.words('english')
stop_words = list(set(stop_words))
w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
lemmatizer = nltk.stem.WordNetLemmatizer()

def remove_url(dataframe):  
    dataframe['Text'] = dataframe['Text'].str.replace(r's*https?://S+(s+|$)', ' ').str.strip()
    return dataframe


def remove_numbers(text):
    text = re.sub(r'\d+', '', text)
    return text


def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words


def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words


def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', ' ', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words


def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stop_words:
            new_words.append(word)
    return new_words

def get_pos( word ):
    w_synsets = wordnet.synsets(word)

    pos_counts = Counter()
    pos_counts["n"] = len(  [ item for item in w_synsets if item.pos()=="n"]  )
    pos_counts["v"] = len(  [ item for item in w_synsets if item.pos()=="v"]  )
    pos_counts["a"] = len(  [ item for item in w_synsets if item.pos()=="a"]  )
    pos_counts["r"] = len(  [ item for item in w_synsets if item.pos()=="r"]  )
    
    most_common_pos_list = pos_counts.most_common()
    return most_common_pos_list[0][0]
    
def lemmatize_text(text):
    return [lemmatizer.lemmatize( w, get_pos(w) ) for w in text]


def remove_oneandtwo_letter_word(words):
    """Remove one letter word from list of tokenized words"""
    new_words = []
    for word in words.split():
        if len(word) > 2:
            new_words.append(word)
    return ' '.join(list(set(new_words)))



def normalize_data(words):
    words = remove_non_ascii(words)

    words = to_lowercase(words)

    words = remove_punctuation(words)

    words = remove_stopwords(words)

    words = lemmatize_text(words)
    return ' '.join(words)

# remove URL
df = remove_url(df)

# Remove Numbers
df['Text'] = df['Text'].apply(lambda x: remove_numbers(x))

# Tokenizing the data
df['Text'] = df.apply(lambda row: nltk.word_tokenize(row['Text']), axis=1)

# Calling the normalize function to implement the remianing Text processing functions
df['Text'] = df.apply(lambda row: normalize_data(row['Text']), axis=1)

# removing one and two letter words
df['Text'] = df.apply(lambda row: remove_oneandtwo_letter_word(row['Text']), axis=1)
df.head()

"""### Cleaning the processed dataframe"""

df.head()

required_columns = ['Text','Defect','Date']
final_df = df[required_columns]
#final_df = final_df.reset_index(drop=True)

final_df

# Removing time from Date column
final_df['Date'] = pd.to_datetime(final_df['Date']).dt.date

final_df = final_df.dropna()
final_df

print(final_df["Text"].nunique())
final_df.drop_duplicates(subset=['Text'] ,inplace=True)
final_df.reset_index(inplace = True, drop = True)
final_df

final_df.loc[final_df['Defect'] == "No Defect", 'Defect'] = 0
final_df.loc[final_df['Defect'] == "Performance Defect", 'Defect'] = 1

final_df

"""### Save the final cleaned data to a csv.
* Update the 'write_location' variable below
"""

write_location = '/content/drive/MyDrive/Colab Notebooks/MIS798_Files/Pre_processed_data/'

final_df.to_csv(write_location+'Processed_data.csv', index=False)


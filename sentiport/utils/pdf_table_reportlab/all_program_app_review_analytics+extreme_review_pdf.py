import altair as alt
import csv
import datetime
import emoji
import gensim
import json
import math
import matplotlib.pyplot as plt
import matplotlib.dates
import nltk
import numpy as np
import operator
import os # accessing directory structure
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.offline as offline
import plotly.express as px
import pickle 
import pyLDAvis
import pyLDAvis.gensim
import requests
import re
import regex
import seaborn as sns
import semver
import spacy
import scipy.stats as st
import statistics
import statsmodels.api as sm
import statsmodels.api as sm
import string
import tensorflow as tf
import time
import wordcloud
from altair import *
from bs4 import BeautifulSoup
from collections import OrderedDict 
from datetime import datetime
from distutils.version import LooseVersion
from distutils.version import StrictVersion
from gensim import corpora
from google.colab import auth
from google.colab import files
from google_play_scraper import app, reviews, reviews_all, Sort
from googletrans import Translator
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
from keras import backend as K
from matplotlib.dates import date2num
from mpl_toolkits.mplot3d import Axes3D
from nltk.corpus import stopwords
from nltk.corpus import brown
from oauth2client.client import GoogleCredentials
from plotly.subplots import make_subplots
from plotly import tools
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from scipy.stats import zscore
from scipy.ndimage import gaussian_filter1d
from statsmodels.stats.outliers_influence import summary_table
from tensorflow import keras
from tensorflow.keras import layers
from textblob import TextBlob
from tqdm import tqdm
from vaderSentiment.vaderSentiment import  SentimentIntensityAnalyzer as  SIA
from wordcloud import WordCloud
from langdetect import detect
from tqdm import tqdm 
from tqdm.notebook import tnrange, tqdm_notebook
translator = Translator()

nltk.download('stopwords')
nltk.download("popular")
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
pd.options.mode.chained_assignment = None 
lemmatizer = WordNetLemmatizer()

#@title Google Drive Authentication
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)
# Download trained model from "hamdy google drive"
# https://drive.google.com/file/d/1thqF8veg_vdcKqYIbr3TU3oJPuVUJDmp/view?usp=sharing
downloaded = drive.CreateFile({'id':"1Gy9RjjivKkPOnlTBOD7xPrV8lgAXqdFc"})   
downloaded.GetContentFile('supertype_supervised_model.zip')
!unzip supertype_supervised_model.zip

"""#GET DATA"""

# @title Google Playstore Crawling Function as "get_crawl_google(id, country_id)"
def get_crawl_google (id, country_id):
  '''
  This function is used to crawl data from google playstore

  Parameters:
  id-- application's playstore id
  country_id-- application's country id

  returns:
  df_google-- crawled google dataframe (columns = 'reviewID','review','version','rating','at')
  '''

  BATCH_SIZE = 50
  MAX_REVIEWS = 5000
  appinfo = app(
      id,
      lang='en',
      country=country_id)

  appinfo['title']
  AVAIL_REVIEWS = appinfo.get('reviews')
  TOFETCH_REVIEWS = min(AVAIL_REVIEWS, MAX_REVIEWS)
  ints = list(range(TOFETCH_REVIEWS//BATCH_SIZE))
  t = tqdm(total=TOFETCH_REVIEWS)
  for i in ints:
      if i == 0:
        result, continuation_token = reviews(id,
                                           count=BATCH_SIZE,
                                           country=country_id
                                           )
      res, continuation_token = reviews(id, count=BATCH_SIZE, continuation_token=continuation_token)
      result.extend(res)
      t.update(BATCH_SIZE)
  t.close()
  AVAIL_REVIEWS
  dfp = pd.DataFrame(result)
  dfp.drop_duplicates('reviewId', inplace=True) #droppping the duplicates

  # creating the dataframe
  data = [dfp['reviewId'],dfp['content'],dfp['reviewCreatedVersion'],dfp['score'],dfp['at']]
  headers = ['reviewId','review','version','rating','at']
  df_google = pd.concat(data, axis=1, keys=headers)
  df_google['version'].fillna("null",inplace=True)
  
  # fill the null value on the version
  for idx in range(len(df_google)-1):
    if df_google['version'][idx] == 'null' :
      df_google.loc[idx,'version']= df_google['version'][idx+1]
  
  # drop version which lead to error (ex: '334280')
  for i in range(len(df_google)):
    if "." in df_google['version'][i][1]:
      pass
    elif "." in df_google['version'][i][2]:
      pass
    else:  
      df_google.drop(index=i,inplace=True)
  df_google.reset_index(drop=True, inplace=True)
  df_google['at'] = pd.to_datetime(df_google['at']) #set the 'at' column as datetime
  df_google.drop_duplicates(subset ="reviewId", 
                     keep = False, inplace = True) 
  return df_google

#@title Input Playstore ID and Country ID here (example playstore ID: **com.linkdokter.halodoc.android** ; Country ID: **ID**)
PLAYSTORE_ID = 'com.linkdokter.halodoc.android'
COUNTRY = 'id'

appinfo = app(
    PLAYSTORE_ID,
    lang='en',
    country=COUNTRY
)

DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY)


print(appinfo['title'])

"""#PREPROCESSING"""

#@title Define Translator as "get_translated_language(DATAFRAME)"
def translate_to_english(review):
  translation = translator.translate(review, dest='en', src='id')
  return translation.text

def get_negative_review(DATAFRAME):
  NEG_DATAFRAME = DATAFRAME[DATAFRAME['rating']<4]
  NEG_DATAFRAME = NEG_DATAFRAME.reset_index(drop=True)
  return NEG_DATAFRAME

def detect_lang(DATAFRAME):
  print("First batch translations!")
  NEG_DATAFRAME = get_negative_review(DATAFRAME)    
  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       print("This row throws error:", NEG_DATAFRAME['review'][i])
  return NEG_DATAFRAME

def detect_lang2(NEG_DATAFRAME):  
  print("Second batch translations!") 
  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       print("This row throws error:", NEG_DATAFRAME['review'][i])
  return NEG_DATAFRAME

def detect_lang3(NEG_DATAFRAME):   
  print("Third batch translations!") 
  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       print("This row throws error:", NEG_DATAFRAME['review'][i])
  return NEG_DATAFRAME

def detect_lang4(NEG_DATAFRAME):   
  print("Fouth batch translations!")
  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       print("This row throws error:", NEG_DATAFRAME['review'][i])
  return NEG_DATAFRAME

def detect_lang5(NEG_DATAFRAME):   
  print("Fifth batch translations!")
  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       print("This row throws error:", NEG_DATAFRAME['review'][i])                 
  return NEG_DATAFRAME

def detect_lang6(NEG_DATAFRAME):   
  print("Sixth batch translations!")
  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       print("This row throws error:", NEG_DATAFRAME['review'][i])
  return NEG_DATAFRAME

def detect_lang7(NEG_DATAFRAME):   
  print("Last batch translations!")
  print("Sorry we can't translate for this data!")

  for i in tnrange(len(NEG_DATAFRAME)):                                         
    try:                                                          
       lang=detect(NEG_DATAFRAME['review'][i])
       if lang == 'id':
          NEG_DATAFRAME['review'].iloc[i] = translate_to_english(NEG_DATAFRAME['review'][i])
          lang=detect(NEG_DATAFRAME['review'][i])
          if lang == 'id':
            print(lang, NEG_DATAFRAME.index[i], NEG_DATAFRAME['review'][i])                                      
    except:                                                       
       lang='no'                                                  
       #print("This row throws error:", NEG_DATAFRAME['review'][i])
       
  return NEG_DATAFRAME

def get_translated_language(DATAFRAME):
  print("Please wait, currently we're translating your negative review into English!")
  if 'index' in DATAFRAME.columns:
      print("You've index column in your dataframe!")
  else:  
      DATAFRAME = DATAFRAME.reset_index()
  NEG_DATAFRAME = detect_lang(DATAFRAME)
  NEG_DATAFRAME = detect_lang2(NEG_DATAFRAME)
  NEG_DATAFRAME = detect_lang3(NEG_DATAFRAME)
  NEG_DATAFRAME = detect_lang4(NEG_DATAFRAME)
  NEG_DATAFRAME = detect_lang5(NEG_DATAFRAME)
  NEG_DATAFRAME = detect_lang6(NEG_DATAFRAME)
  NEG_DATAFRAME = detect_lang7(NEG_DATAFRAME)  
  DATAFRAME = pd.concat([DATAFRAME,NEG_DATAFRAME]).drop_duplicates(['reviewId','version','rating','at'],keep='last').sort_values('index')
  return DATAFRAME

# @title Define data preprocessing1 & preprocessing2 function as "get_preprocess_data1(df)" & "get_preprocess_data2(df, short_word_removal_thresh)"
# contractions dictionary
contractions = { 
"ain't": "am not / are not / is not / has not / have not",
"aren't": "are not / am not",
"can't": "cannot",
"can't've": "cannot have",
"cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had / he would",
"he'd've": "he would have",
"he'll": "he shall / he will",
"he'll've": "he shall have / he will have",
"he's": "he has / he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how has / how is / how does",
"i'd": "i would",
"i'd've": "i would have",
"i'll": "i will",
"i'll've": "i shall have",
"i'm": "i am",
"i've": "i have",
"isn't": "is not",
"it'd": "it had / it would",
"it'd've": "it would have",
"it'll": "it shall / it will",
"it'll've": "it shall have / it will have",
"it's": "it has / it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she had / she would",
"she'd've": "she would have",
"she'll": "she shall / she will",
"she'll've": "she shall have / she will have",
"she's": "she has / she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"that'd": "that would / that had",
"that'd've": "that would have",
"that's": "that has / that is",
"there'd": "there had / there would",
"there'd've": "there would have",
"there's": "there has / there is",
"they'd": "they had / they would",
"they'd've": "they would have",
"they'll": "they shall / they will",
"they'll've": "they shall have / they will have",
"they're": "they are",
"they've": "they have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what shall / what will",
"what'll've": "what shall have / what will have",
"what're": "what are",
"what's": "what has / what is",
"what've": "what have",
"when's": "when has / when is",
"when've": "when have",
"where'd": "where did",
"where's": "where has / where is",
"where've": "where have",
"who'll": "who shall / who will",
"who'll've": "who shall have / who will have",
'n': 'and'
}

stop_words = stopwords.words('english')
l=stop_words.index('not')
stop_words=stop_words[:l]+stop_words[1+1:]

# spacy method for lemmatization
nlp = spacy.load('en', disable=['parser', 'ner'])
lemmatizer = WordNetLemmatizer() 

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    text=regrex_pattern.sub(r'',text)
    text=text.replace('\n',' ')
    text=re.sub(' +', ' ', text)
    
    return text

# expand contraction with this function
def expand_contractions(entry):
    entry=entry.lower()
    entry=re.sub(r"’","'",entry)
    entry=entry.split(" ")

    for idx,word in enumerate(entry):
        if word in contractions:
            entry[idx]=contractions[word]
    return " ".join(entry)

# remove punctuation with this function
def remove_punctuation(entry):
    entry=re.sub(r"[^\w\s]"," ",entry)
    return entry

#might need to extend stop words to include the name of the app --> so 5miles (miles), carousell, etc
# remove stopwords with this function
def remove_stop_words(sentence):
    dummy=sentence.split(" ")
    out=[i for i in dummy if (i not in stop_words) and (len(i)>2)]
    return " ".join(out)

# lemmatizer function
#trying topic modelling with 30 topics taking all tags
def lemmatize(reviews):
    tags=['NOUN','ADJ']
    doc = nlp(reviews)
    output=[token.lemma_ for token in doc if token.pos_ in tags]
    return " ".join(output)

def spacy_lemmatize(reviews):
    #tags=['ADJ','NOUN','']
    doc = nlp(reviews)
    #output.append([token.lemma_ for token in doc])# if token.pos_ in tags])
    return " ".join([token.lemma_ for token in doc])

def get_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    if tag in tag_dict:
      return tag_dict[tag]
    else:
      return 'n'

def nltk_lemmatize(sentence):

  return" ".join(lemmatizer.lemmatize(word,get_pos(word)) for word in nltk.word_tokenize(sentence))

# remove short words
def remove_short_words(sentence,threshold):
  dummy=sentence.split(" ")
  out=[i for i in dummy if len(i)>=threshold and i!="-PRON-"]
  return " ".join(out)

# remove short words with this function
def remove_short_words2(sentence):
  dummy=sentence.split(" ")
  out=[i for i in dummy if len(i)>2]
  return " ".join(out)

# Only take the negative reviews (rating of 1,2, and 3)
def take_negative(df):
  df=df[df['rating']<4]
  return df

# @title n-gram function "get_n_grams(df)"
def get_ngrams_init(df):
  pos=df[df['rating'].isin([4,5])] #keep the index this way, will use the indexes later
  neg=df[df['rating'].isin([1,2,3])] 
  pos_lemma=[val.split(" ") for val in pos['review'].values]
  neg_lemma=[val.split(" ") for val in neg['review'].values]
  return pos.index,neg.index,pos_lemma,neg_lemma

def get_bigrams(pos_lemma,neg_lemma):
  #Can make this customizable in the package..
  pos_bigrams=gensim.models.Phrases(pos_lemma,min_count=3,threshold=10)
  pos_bigram_reviews=pos_bigrams[pos_lemma] 
  neg_bigrams=gensim.models.Phrases(neg_lemma,min_count=3,threshold=6)
  neg_bigram_reviews=neg_bigrams[neg_lemma] 
  return pos_bigram_reviews,neg_bigram_reviews

def get_trigrams(pos_bigram_reviews,neg_bigram_reviews):
  #Can make this customizable later on in the package..
  pos_trigrams=gensim.models.Phrases(pos_bigram_reviews,min_count=2,threshold=15)
  pos_trigram_reviews=pos_trigrams[pos_bigram_reviews]
  neg_trigrams=gensim.models.Phrases(neg_bigram_reviews,min_count=2,threshold=8)
  neg_trigram_reviews=neg_trigrams[neg_bigram_reviews]
  return pos_trigram_reviews,neg_trigram_reviews

def get_put_n_grams_in_df(df,index,reviews):
  dummy=[" ".join(tri) for tri in reviews]
  pointer=0
  for idx in index:
    df['review'][idx]=dummy[pointer]
    pointer+=1
  return df

def get_n_grams(df):
  #Inputs:
  #df--combined_df_preprocessed 
  #Outputs:
  #A dataframe with the sentences transformed to contain bigrams, trigrams
  pos_index,neg_index,pos_lemma,neg_lemma= get_ngrams_init(df)
  pos_bigram_reviews,neg_bigram_reviews=get_bigrams(pos_lemma,neg_lemma)
  pos_trigram_reviews,neg_trigram_reviews=get_trigrams(pos_bigram_reviews,neg_bigram_reviews)
  df= get_put_n_grams_in_df(df,pos_index,pos_trigram_reviews)
  df= get_put_n_grams_in_df(df,neg_index,neg_trigram_reviews)
  return df

# combine most of the functions above to one "preprocess_data" function below
def get_preprocess_data1(df):
  print("Please wait, currently we're doing first preprocessing for your review data!")
  df=df.copy()
  df=take_negative(df)
  df['review']=df['review'].astype(str)
  df['review']=df['review'].apply(lambda x: x.lower()) #lowering case
  df['review']=df['review'].apply(deEmojify)           #removing emoji
  df['review']=df['review'].apply(expand_contractions) 
  df['review']=df['review'].apply(remove_punctuation)   
  df['review']=df['review'].apply(lambda s: re.sub(r"[^a-zA-Z]"," ",s)) #keep only alphabetical words
  df['review']=df['review'].apply(nltk_lemmatize)
  df['review']=df['review'].apply(spacy_lemmatize)
  df['review']=df['review'].apply(remove_stop_words)
  df['review']=df['review'].apply(lambda s:re.sub(' +', ' ', s))   #remove + sign
  df['review']=df['review'].apply(lambda s: s.replace('-PRON-',""))
  df.drop(df[df['review'].apply(lambda x: len(x)==0)].index,inplace=True)
  #df.reset_index(inplace=True,drop=True) 
  return df

# combine most of the functions above to one "preprocess_data" function below
def get_preprocess_data2(df, short_word_removal_thresh):
    print("Please wait, currently we're doing second preprocessing for your review data!")
    df=df.copy()
    df['review']=df['review'].astype(str)
    df['review']=df['review'].apply(lambda x: x.lower()) #lowering case
    df['review']=df['review'].apply(deEmojify)           #removing emoji
    df['review']=df['review'].apply(expand_contractions) 
    df['review']=df['review'].apply(remove_punctuation)   
    df['review']=df['review'].apply(lambda s: re.sub(r"[^a-zA-Z]"," ",s)) #keep only alphabetical words
    df['review']=df['review'].apply(lemmatize)
    df['review']=df['review'].apply(remove_stop_words) #also removes short words
    df['review']=df['review'].apply(lambda s:re.sub(' +', ' ', s))   #remove + sign
    df['review']=df['review'].apply(remove_short_words,args=(short_word_removal_thresh,))
    df.drop(df[df['review'].apply(lambda x: len(x)==0)].index,inplace=True)
    return df

"""#MODELING"""

#@title Define Topic Modeling as "get_topic_modeling_pharma(preprocessed1)"
model_path = 'supertype_supervised_model/topic_model/saved_model.pb'
tokenizer_path = 'supertype_supervised_model/tokenizer.pickle'
with open('supertype_supervised_model/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

class TopicModel():
  def __init__(self, tokenizer_path, model_path):
    with open(tokenizer_path, 'rb') as handle:
      self.tokenizer = pickle.load(handle)
    self.model = load_model(model_path)

  def predict(self, texts):
    sequences = self.tokenizer.texts_to_sequences(texts)
    X = pad_sequences(sequences, 200)
    return 1 * (self.model.predict(X) > 0.5)

def topic_model(path):
  topicModel = TopicModel(path+'tokenizer.pickle', path+'topic_model')
  return topicModel

def get_topicModel(path):
  topicModel = TopicModel(path+'tokenizer.pickle', path+'topic_model')
  return topicModel

def get_topic_modeling_pharma(preprocessed1): 
  print("Please wait, currently we're doing topic modeling for your preprocessed1 review data!")
  path = 'supertype_supervised_model/'
  topicModel = get_topicModel(path)
  topicModel = topic_model(path)
  topics = ['stock logistics', 'delivery logistics', 'customer service', 
          'app functionality', 'service functionality', 'locational constraints']
  #preprocessed = get_preprocess_data1(DATAFRAME)
  preprocessed1 = preprocessed1.reset_index(drop=True)
  preds = topicModel.predict(preprocessed1['review'])
  NEG_DATAFRAME = pd.concat([preprocessed1, pd.DataFrame(preds, columns=topics)], axis=1)
  return NEG_DATAFRAME, topics

# @title Define data processing function as "get_HAC(neg_dataframe)"

def get_tag_list_spacy(x):
  #Get the noun/adjective words and store it in tagList for spacy
  tagList = []
  for word in x:
    if(word.tag_ == "NN" or word.tag_ == "JJ"):
      #taglist only needs to keep into account the NN and JJ, because the nouns and adjectives are added sequentially left to right
      tagList.append(tuple([word.text,word.tag_]))
  return tagList

def get_tag_list_nltk(x):
  #Get the noun/adjective words and store it in tagList for nltk
  tagList = []
  for word in x:
    if(word[1] == "NN" or word[1] == "JJ"):
      #taglist only needs to keep into account the NN and JJ, because the nouns and adjectives are added sequentially left to right
      tagList.append(word)
  return tagList

def add_nouns(tagList,nounScores):
  for e in tagList:
    if e[1] == "NN":
      if e[0] not in nounScores:
        nounScores[e[0]] = 0
  return nounScores

def check_right(j,l,tagList,maxHops,rightHop):
  for j in range(l + 1, len(tagList)):
    #j starts off at the right of adjective
    if(j == l + maxHops):
      break
    if("NN" in tagList[j][1]):
      rightHop = (j - l)  #since rightHop started one pos to the right, we subtract original position, l, to get num of hops
      break
  return j,rightHop

def check_left(k,l,tagList,maxHops,leftHop):
  for k in range(l - 1, -1, -1):
    #k initialized to the left of the current adjective
    #Incase hopped the 'maxHops' number of words and no noun was found, ignore the adjective
    if(k == l - maxHops):
      #modified this from j == l -maxHops into k==1-maxHops
      break
    if("NN" in tagList[k][1]):
      leftHop = (l - k)
      break
  return k,leftHop

def confirm_noun(leftHop,rightHop,tagList,j,k,nounScores):
  if (leftHop > 0 and rightHop > 0): 				#If nouns exist on both sides of adjective
    if (leftHop - rightHop) >= 0: #If left noun is farther	
      noun= tagList[j][0]					
      nounScores[tagList[j][0]] += 1
    else:													#If right noun is farther
      noun= tagList[k][0]
      nounScores[tagList[k][0]] += 1
  elif leftHop > 0:											#If noun is not found on RHS of adjective
    noun=tagList[k][0]
    nounScores[tagList[k][0]] += 1
  elif rightHop > 0:										#If noun is not found on LHS of adjective
    noun=tagList[j][0]
    nounScores[tagList[j][0]] += 1
  return noun,nounScores
#might have to pass nounScores in if nounScores is not a global variable


####
def HAC_sentiment_scoring (phrase,b):
  #phrase--> phrase to be scored
  #b --> sentiment analyzer to be used, either TextBlob or Vader for now
  if b == 'textblob':
    score=TextBlob(phrase).sentiment.polarity
  elif b=='vader':
    analyzer=SIA()
    score=analyzer.polarity_scores(phrase)['compound']
  return score
  
def check_inversion_and_severity(noun,a,l,tagList,inversion_threshold,b,severity_threshold):
  thresh=(inversion_threshold/100)*-1 #threshold has to become negative
  severity_threshold= severity_threshold/100
  analyzer=SIA()
  score=HAC_sentiment_scoring(tagList[l][0],b)
  #score=TextBlob(tagList[l][0]).sentiment.polarity


  sentence=a.split(" ")
  for idx,token in enumerate(sentence):
    if token == tagList[l][0]:
      #check for position of adjective in original sentence, not tag list

      if (idx-2)>=0:

        #Take phrase to be two words to the left + present adj
        phrase = sentence[idx - 2] + " " + sentence[idx - 1] + " " + sentence[idx]
        phrase_score=HAC_sentiment_scoring(phrase,b)

        if ((phrase_score * score) < thresh): 
          #basically check if the score of the adjective phrase is the opposite sign of the score of the adjective alone
          #if indeed the phrase is an inversion, then these two would always have a score<0

          noun_phrase=phrase+" " +noun 
          #print(f"Inversion detected: {noun_phrase} ")

        elif (abs(phrase_score)-abs(score))>severity_threshold: #checking abs difference in sentiment scores if not inversions
          noun_phrase=phrase+" " +noun
          #print(f"{phrase} is more extreme than {tagList[l][0]}")
        else:
          noun_phrase=tagList[l][0]+" "+noun

      elif (idx-1)>=0:

        #Take phrase to be one word to the left + present adj
        phrase = sentence[idx - 1] + " " + sentence[idx]
        phrase_score=HAC_sentiment_scoring(phrase,b) * score 

        if ((phrase_score) < thresh): 
          #if indeed the phrase is an inversion

          noun_phrase=phrase+" " + noun
          #print(f"Inversion detected: {noun_phrase} ")
        elif (abs(phrase_score)-abs(score))>severity_threshold:
          noun_phrase=phrase+" " +noun
          #print(f"Phrase {phrase} is more extreme than {tagList[l][0]}")
        else:
          noun_phrase=tagList[l][0]+" "+noun
      else:
        noun_phrase=tagList[l][0]+" "+noun
  return noun_phrase

def format_into_df(adjDict):
  adj_phrase=[" ".join(i[0].split(" ")[:-1]) for i in adjDict.items()]
  noun=[i[0].split(" ")[-1] for i in adjDict.items()]
  scores=[i[1] for i in adjDict.items()]
  dff=pd.DataFrame(columns=['adj_phrase','noun','frequency'])
  dff['adj_phrase']=adj_phrase
  dff['noun']=noun
  dff['frequency']=scores
  dff.sort_values('frequency',ignore_index=True,inplace=True,ascending=False)
  return dff

def HAC(reviewContent, tagger,maxHops=3,inversion_threshold=5,severity_threshold=5,analyzer='vader'):
  nounScores = dict()

  #adjDict dict contains adjective and the corresponding noun which it is assigned to
  adjDict = dict()

  for a in reviewContent: 
    #a being each sentence	

    #Tokenize and pos tag it
    if tagger== 'spacy':
      doc=nlp(a)
      tagList=get_tag_list_spacy(doc)
    elif tagger == 'nltk':
      x = nltk.pos_tag(nltk.word_tokenize(a))
      tagList=get_tag_list_nltk(x)

    #add the nouns(which are not in the nounScores dict) to the dict not scoring yet, just add nouns
    nounScores=add_nouns(tagList,nounScores)

    #For every adjective, find nearby noun
    for l in range(len(tagList)):
      #l is the index position of a word

      #at this point, taglist is a list of tuples [(word,pos),(word,pos),..]
      if("JJ" in tagList[l][1]):
        #check whether the word at position l is an adjective

        j = k = leftHop = rightHop = -1

        #Find the closest noun to the right of the adjective in the line
        j,rightHop=check_right(j,l,tagList,maxHops,rightHop)

        #Find the closest noun to the left of the adjective in the line
        k,leftHop=check_left(k,l,tagList,maxHops,leftHop)

        #checking for whether or not a noun was found to the left or right of the adjective
        #if both are still -1, means noun was not found close to that adj.
        if (leftHop>0) or (rightHop) > 0:

          #call function to confirm noun, and to modify nounScore
          noun,nounScores=confirm_noun(leftHop,rightHop,tagList,j,k,nounScores)

          #call function to check inversion
          noun_phrase=check_inversion_and_severity(noun,a,l,tagList,inversion_threshold,analyzer,severity_threshold)

          #now we make adjDict contain the noun_phrase and record it
          if noun_phrase not in adjDict.keys():
            adjDict[noun_phrase] =1
          else:
            adjDict[noun_phrase]+=1

  return adjDict,nounScores

def get_HAC(neg_dataframe):
  print("Please wait, currently we're doing preprocessing2 for your negative labeled review data!")
  neg_preprocessed2 = get_preprocess_data2(neg_dataframe,short_word_removal_thresh=3)
  reviewContent=neg_preprocessed2.review.values

  print("Please wait, currently we're getting HAC for your preprocessed negative review data!")
  HAC_adjDict, nounScores = HAC(reviewContent,"spacy",maxHops=3,
                            inversion_threshold=5,severity_threshold=20,analyzer='vader')
  hac_result_df = format_into_df(HAC_adjDict)
  hac_result_df[hac_result_df['adj_phrase'].apply(lambda x: len(x.split(" "))==3)]

  #print(f"ADJ PHRASE IS: {hac_result_df.loc[84]['adj_phrase']}")
  #phrase = " ".join(hac_result_df.loc[84]['adj_phrase'].split(" ")[:-1])
  #adj = hac_result_df.loc[84]['adj_phrase'].split(" ")[-1]
  #print(f"PHRASE IS: {phrase}")
  #print(f"THE ADJECTIVE IS: {adj}")
  hac = hac_result_df[hac_result_df['adj_phrase'].apply(lambda x: len(x.split(" "))==3)]
  return hac, hac_result_df, nounScores, neg_preprocessed2

# @title Define data processing function as "get_sentence_ranking(hac, nounScores, df_preprocessed, NEG_DATAFRAME)"

def inspect(df,score_type):
  analyzer=SIA()
  scores=[]
  pos=0
  neg=0
  for i in df['adj_phrase'].values:
    score=analyzer.polarity_scores(i)
    if score['pos']>score['neg']:
      pos+=1
    else:
      neg+=1
    scores.append([score['pos'],score['neg'],score['compound']])
  scores=np.array(scores)

  if (pos>neg) and (score_type=='ratio'):
    print("Reviews of this group are overall positive")
    scores=scores[:,0]
  elif (neg>=pos) and (score_type=='ratio'):
    print("Review of this group are overall negative")
    scores=-scores[:,1]
  elif score_type=='compound':
    scores=scores[:,2]
    if neg >= pos:
      print("TOPIC IS NEGATIVE")
    else:
      print("TOPIC IS POSITIVE")
  
  dff=df.copy()
  dff['opinion_score']=scores
  return dff

def shift_dist(df,topic_sentiment): 
  #topic_sentiment should either be positive or negative, taken from the inversion test
  if topic_sentiment=='neg':
    factor=max(df['opinion_score'])
    df['opinion_score']=df['opinion_score']-factor
  elif topic_sentiment=='pos':
    factor=min(df['opinion_score'])
    df['opinion_score']=df['opinion_score']+factor
  
  return df,factor

def get_avg_noun_score(inspect_df_shifted,nounScores, inspect_df):
  avg_noun_score={}
  inspect_df_shifted['mult']=inspect_df_shifted['frequency']*inspect_df_shifted['opinion_score']
  for i in nounScores.keys():
    score_sum= np.sum(inspect_df[inspect_df['noun']==i]['mult'])
    avg_noun_score[i]=score_sum/(nounScores[i]+1) #need this for smoothing
  return avg_noun_score

def get_adj_set(shifted_df):
  adj=set()
  for i in shifted_df['adj_phrase'].values:
    tokenized=i.split(" ")
    adj.add(tokenized[-1])
  adj_phrase=set(shifted_df['adj_phrase'])
  return adj,adj_phrase

def scoring_helper_dicts(adj,adj_phrase,factor,sentiment):
  adj_only_dict={}
  adj_phrase_dict={}
  analyzer=SIA()
  for i in adj:
    if sentiment == 'pos':
      adj_only_dict[i]=analyzer.polarity_scores(text=str(i))['compound']+factor
    elif sentiment=='neg':
      adj_only_dict[i]=analyzer.polarity_scores(text=str(i))['compound']-factor
  for j in adj_phrase:
    if sentiment == 'pos':
      adj_phrase_dict[j]=analyzer.polarity_scores(text=str(i))['compound']+factor
    elif sentiment=='neg':
      adj_phrase_dict[j]=analyzer.polarity_scores(text=str(i))['compound']-factor
  return adj_only_dict,adj_phrase_dict

def format_into_df_final(df,df_preprocessed,importances,noun_only,adj_scores):
  final_df=df[['review']]
  final_df['sentence_score']=[0]*len(final_df)
  final_df.loc[df_preprocessed.index,'sentence_score']=np.array(importances).reshape(len(importances),1)
  final_df['noun_score']=[0]*len(final_df)
  final_df.loc[df_preprocessed.index,'noun_score']=np.array(noun_only).reshape(len(noun_only),1)
  final_df['adj_score']=[0]*len(final_df)
  final_df.loc[df_preprocessed.index,'adj_score']=np.array(adj_scores).reshape(len(adj_scores),1)
  return final_df

def sentence_scoring_1(df,nounScores,adj_phrase_dict,adj_only_dict,c):
  print("FORMULA 1 USED")
  #might need to do lookups with dictionary, faster lel
  importances=[]
  adj_scores=[]
  pure_noun_scores=[]
  #all_reviews=np.array(df['review'].apply(lambda x: x.split(" ")))
  for sent in df['review'].values:
    doc=nlp(sent)

    #initialize scores
    score=0
    noun_score=0
    adj_score=0

    #initialize counts
    noun_count=0
    adj_count=0

    #handle the noun part first, sum up the noun scores raw || get noun scores 
    for token in doc:
      if token.pos_=="NOUN":
        noun_count+=1
        if token.text in nounScores:
          noun_score+=nounScores[token.text]
    pure_noun_scores.append(noun_score)
    

    #handle adjective (needs to be optimized) || get adjective scores
    tokenized=sent.split(" ")
    for idx,word in enumerate(tokenized):
      if word in adj_only_dict:
        #if adjective is in dictionary
        
        adj_count+=1
        #check the left side twice of the word
        if idx>1:
          #First need to find the phrase
          #check if adjective phrase position >1

          phrase=tokenized[idx-2]+" "+tokenized[idx-1]+ " " + word
          if phrase in adj_phrase_dict:
            #if phrase 3 words and in dictionary
            adj_score+=adj_phrase_dict[phrase]
          else:
            phrase=tokenized[idx-1]+ " " + word
            if phrase in adj_phrase_dict:
              #phrase 2 words and in dictionary
              adj_score+=adj_phrase_dict[phrase]
            else:
              #phrase only adjective and in dictionary
              adj_score+=adj_only_dict[word]
        elif idx>0:
          #adjective phrase in position 1

          phrase=tokenized[idx-1]+" " + word
          if phrase in adj_phrase_dict:
            #phrase 2 words and in dictionary
            adj_score+=adj_phrase_dict[phrase]
          else:
            #phrase is adj only and in dictionary
            adj_score+=adj_only_dict[word]
        else:
          #adjective is the first word in sentence
          adj_score+=adj_only_dict[word]
    adj_scores.append(adj_score)
    importances.append(c*noun_score+adj_score)

  #scale the importances based on the noun scores only
  log=np.log(df['review'].apply(lambda x: len(x.split(" ")))+1)
 
  importances=np.array(importances) / log

  return importances,pure_noun_scores,adj_scores

def sentence_scoring_2(df,nounScores,adj_phrase_dict,adj_only_dict,c):
  importances=[]
  adj_scores=[]
  pure_noun_scores=[]

  print("FORMULA 2 USED")
  for sent in df['review'].values:
    doc=nlp(sent)

    #initialize scores
    score=0
    noun_score=0
    adj_score=0

    #initialize counts
    noun_count=0
    adj_count=0

    #handle the noun part first, sum up the noun scores raw || get the noun score for sentence
    for token in doc:
      if token.pos_=="NOUN":
        noun_count+=1
        if token.text in nounScores:
          noun_score+=nounScores[token.text]
    pure_noun_scores.append(noun_score)
    

    #handle adjective (needs to be optimized) || get adj score for sentence
    tokenized=sent.split(" ")
    for idx,word in enumerate(tokenized):
      if word in adj_only_dict:
        adj_count+=1
        #check the left side twice of the word
        if idx>1:
          #if the position of adjective is >1 in sentence

          #First need to find the phrase
          phrase=tokenized[idx-2]+" "+tokenized[idx-1]+ " " + word
          if phrase in adj_phrase_dict:
            #if the phrase is 3 words and in the dictionary
            adj_score+=adj_phrase_dict[phrase]
          else:
            phrase=tokenized[idx-1]+ " " + word
            if phrase in adj_phrase_dict:
              #if phrase 2 words and in dictionary
              adj_score+=adj_phrase_dict[phrase]
            else:
              #phrase is the adjective only
              adj_score+=adj_only_dict[word]
        elif idx>0:
          #if adjective is in position 1 in sentence

          phrase=tokenized[idx-1]+" " + word      
          if phrase in adj_phrase_dict:
            #if phrase 2 words and in dictionary
            adj_score+=adj_phrase_dict[phrase]
          else:
            #phrase is adjective only
            adj_score+=adj_only_dict[word]
        else:
          #if adjective is the first word in sentence
          adj_score+=adj_only_dict[word]
 
    adj_scores.append(adj_score)
    #apply log scaling using counts of nouns and adj in sentence
    importances.append(((c*noun_score)+adj_score)/(np.log(noun_count+adj_count+1)+1)) #formula should be adjusted accordingly
  return importances,pure_noun_scores,adj_scores

def scoring(df,nounScores,adj_phrase_dict,adj_only_dict,formula,c):
  if formula == 1:
    importances,noun_scores,adj_scores=sentence_scoring_1(df,nounScores,adj_phrase_dict,adj_only_dict,c)
  elif formula ==2:
    importances,noun_scores,adj_scores=sentence_scoring_2(df,nounScores,adj_phrase_dict,adj_only_dict,c)
  return importances,noun_scores,adj_scores

def sentence_scoring_main(inspect_df_shifted,df_preprocessed,df,nounScores,formula_type,factor,c):
  adj,adj_phrase=get_adj_set(inspect_df_shifted)
  adj_only_dict,adj_phrase_dict=scoring_helper_dicts(adj,adj_phrase,factor,'neg')
  importances,sentence_noun_scores,sentence_adj_scores=scoring(df_preprocessed,nounScores,adj_phrase_dict,adj_only_dict,formula_type,c)
  final_df=format_into_df_final(df,df_preprocessed,importances,sentence_noun_scores,sentence_adj_scores)
  return final_df

def get_sentence_ranking(hac, nounScores, df_preprocessed, NEG_DATAFRAME):
  print("Please wait, currently we're handling sentence ranking with HAC results!")
  
  inspect_df=inspect(hac,'compound')
  inspect_df_shifted,factor=shift_dist(inspect_df,'neg')
  avg_nounScores=get_avg_noun_score(inspect_df_shifted,nounScores, inspect_df)
  sentence_rank_df= sentence_scoring_main(inspect_df_shifted,df_preprocessed,NEG_DATAFRAME,avg_nounScores,2,factor,c=2)
  sentence_rank_df = sentence_rank_df.sort_values('sentence_score')
  return sentence_rank_df

# @title initiate model function for severity score function as "get_severity_scores(DATAFRAME, NEG_DATAFRAME, TOPIC)" 
def get_mapper(df):
  mapping={4:1,
         5:1,
         3:0,
         2:0,
         1:0,
         0:0}
  df['rating']=df['rating'].map(lambda x: mapping[x])
  return df

def get_init_params(df):
  #Inputs:
  #df--combined_df_preprocessed

  df_train,df_test=train_test_split(df,test_size=0.05,stratify=df.rating.values,random_state=2020)
  x_train=df_train['review'].values
  x_test=df_test['review'].values
  #train_index=df_train['review'].index
  #test_index=df_train['review'].index
  y_train=df_train['rating'].values
  y_test=df_test['rating'].values
  return x_train,y_train,x_test,y_test

def get_vectorizer(x_train,x_test):
  cv=CountVectorizer()
  x_train_count=cv.fit_transform(x_train)
  x_test_count=cv.transform(x_test)
  vocab_size=x_train_count.shape[1]
  tfidf=TfidfTransformer()
  x_train=tfidf.fit_transform(x_train_count)
  x_test=tfidf.transform(x_test_count)
  features=cv.get_feature_names()
  return x_train,x_test,vocab_size,features

def get_train_model(x_train,y_train):
  #In this case, it will be a logistic regression model, might need to test out if it shud be trained over entire set? Or hold some of the set back?
  #In the exploratory notebook we held back a bit of the train set, do we need to do that here? --> Should be tested out first 
  log_r=LogisticRegression(random_state=2020,class_weight='balanced',solver='liblinear') #This applies a heuristic class balancing, because we have imbalance towards the number of 1s
  log_r.fit(x_train,y_train)
  coeffs=log_r.coef_
  return coeffs

def get_coeff_df(vocab_size,features,coeffs):
  result_dict=dict(tuple([(features[i],coeffs[0][i]) for i in range(vocab_size)]))
  result_df=pd.DataFrame(sorted(result_dict.items(),key=lambda x:x[1]),columns=['word','coeff'])
  return result_dict,result_df

def get_tf_idf(df):
  #Inputs:
  #df--combined_df_preprocessed
  df= get_mapper(df)
  x_train,y_train,x_test,y_test= get_init_params(df)
  x_train,x_test,vocab_size,features= get_vectorizer(x_train,x_test)
  
  #running the model
  coeffs= get_train_model(x_train,y_train)
  #pred=log_r.predict(x_test)

  coeff_dict,coeff_df=get_coeff_df(vocab_size,features,coeffs)
  return coeff_dict,coeff_df

# @title initiate function needed for severity score function as "get_severity_scores(dataframe,neg_dataframe,topic)"
def get_lookup(df,ref):
  #df should be the original dataframe
  #ref should be the reference/dictionary used so pass in result_dict
  val=df['review'].values
  score_list=[]
  for i in val:
    score=0
    for j in i.split(" "):
      if j in ref:
        score+=ref[j]
      else:
        score+=0
  
    score_list.append(score)
  return score_list 

def get_scoring(df,result_dict):
  #Inputs:
  #df-- combined_df_preprocessed
  score= get_lookup(df,result_dict)
  log_r_scored_df=df.copy()
  log_r_scored_df['score']=score
  return log_r_scored_df

def get_add_attributes(df):
  #This function is to add lengths and add the zscores
  #Input:
  #df--scored_unscaled_df

  lengths=df['review'].apply(lambda x: len(x.split(" "))).values
  #z-statistic will be calculated from lengths

  df['z_score']=zscore(lengths)
  df['lengths']=lengths
  return df

def get_find_outliers(array):
  lower_outlier=int(np.quantile(array,0.25)-st.iqr(array)*1.5)
  upper_outlier=int(st.iqr(array)*1.5+np.quantile(array,0.75))
  return lower_outlier, upper_outlier

def get_outlier_scaling(df, upper, lower):
  #Function assumes that lengths have been added to sentences
  longg=df[df['lengths']>upper].index
  df['score'].loc[longg]=df['score'].loc[longg]/abs(df['z_score'].loc[longg])
  if lower>0:
    small=df[df['lengths']<lower+1].index #so if outlier is lets say 1.6, rounded to 1, we find and scale for those sentences with lengths <2
    df['score'].loc[small]=df['score'].loc[small]*abs(df['z_score'].loc[small])
  return df

def get_match_merge_df(combined_df,scored_scaled_df,similar_index,neg_dataframe):
  #This function is to match. Combined_df contains the reviews which are same with the negative labeled set.
  #So we assign the scaled scores with their respective index, to the combined_df.
  #Then we merge the combined_df (now containing scores) with the labeled set, according "on" the review

  combined_df['score']=scored_scaled_df['score'] #match 
  final_df=pd.merge(combined_df.loc[similar_index][['review','score']],neg_dataframe,how='inner',on=['review']) #merge
  final_df.fillna(0,inplace=True) #deal with nulls
  return final_df

# severity score function as "get_severity_scores(dataframe,neg_dataframe,topic)"
def get_severity_scores(DATAFRAME, NEG_DATAFRAME, TOPIC):
  print("Please wait, currently we're handling severity scoring for your negative labeled data!")
  review_rating_dict={
  'review': list(DATAFRAME['review'].values),
  'rating': list(DATAFRAME['rating'].values)
  }
  combined_df= pd.DataFrame(review_rating_dict)
  combined_df.drop_duplicates(['review'],inplace=True)
  combined_df.reset_index(inplace=True,drop=True)
  similar_index=combined_df[combined_df['review'].isin(NEG_DATAFRAME['review'])].index

  print("Please wait, currently we're doing data preprocessing for your combined df!")
  combined_df_preprocessed = get_preprocess_data2(combined_df, short_word_removal_thresh=3)
  combined_df_preprocessed=get_n_grams(combined_df_preprocessed)
  coeff_dict,coeff_df= get_tf_idf(combined_df_preprocessed)
  scored_unscaled_df= get_scoring(combined_df_preprocessed,coeff_dict)
  scored_unscaled_df= get_add_attributes(scored_unscaled_df)
  lower_outlier,upper_outlier= get_find_outliers(scored_unscaled_df.lengths.values)
  scored_scaled_df= get_outlier_scaling(scored_unscaled_df,upper_outlier,lower_outlier)
  final_df1= get_match_merge_df(combined_df,scored_scaled_df,similar_index,NEG_DATAFRAME)

  sum_array=[]
  sums_only=[]
  for c in TOPIC:
    sum=abs(np.sum(final_df1[final_df1[c]==1]['score'].values))
    sum_array.append((c,sum))
    sums_only.append(sum)

  raw_sum_dict=dict(tuple(sum_array))
  normalizer=np.sum(np.array(sums_only))
  normalized_sum_dict={i[0]:i[1]/normalizer for i in raw_sum_dict.items()}

  raw_sum_dict={k: v for k, v in sorted(raw_sum_dict.items(), key=lambda item: item[1])} #sort this 
  normalized_sum_dict={k: v for k, v in sorted(normalized_sum_dict.items(), key=lambda item: item[1])}
  severity_score = pd.DataFrame([normalized_sum_dict])
  return severity_score

# @title Define Function to Get Importance Score as "get_importancescore(dataframe, x, severity_score, neg_dataframe, topic)"
def get_importancescore(dataframe, x, severity_score, neg_dataframe, topic):
    '''
    This function is used to get importance score

    Parameters:
    dataframe-- data from get_crawl_data (but we can put data from apple scrapper if the columns names are identical)
    neg_dataframe-- neg_df from get_negreview_topic
    topic-- topic from get_negreview_topic
    x-- number of months to inspect

    returns:
    importance_score-- importance score
    '''
    print("Please wait, currently we're getting importance score from severity score of negative labeled review!")
    df = neg_dataframe
    topic = topic    
    df_cubi = dataframe
    df_cubi.index = df_cubi['at']
    df.index = df['at']
    df.index =  pd.to_datetime(df.index)
    df_cubi.index =  pd.to_datetime(df_cubi.index)
    df = df[topic].resample('MS').sum().join(pd.DataFrame(df_cubi['review'].resample('MS').count()))
    for kolom in topic:
      df[kolom] = df[kolom].astype(float)
    df.reset_index(inplace=True)
    for i in range(len(df)):
        for kolom in topic:
          if df[kolom][i] > 0:
            df.at[i,kolom] = round((df[kolom][i] / df['review'][i] * 100),2)

    importance_score = pd.DataFrame()
    importance_score['Topic']= topic
    score=[]
    for i in range(len(topic)):
      x1 = statistics.mean(df[topic[i]][-x:]) / 100 * sum(df['review'][-x:]) * severity_score[topic[i]][0]
      score.insert(i,x1)
    importance_score['importance_score']=score
    return importance_score

# @title Define Function to Get Urgency Score as "get_urgencyscore(dataframe, x, neg_dataframe, topic)"
def get_urgencyscore(dataframe, x, neg_dataframe, topic):
    '''
    This function is used to get urgency score

    Parameters:
    dataframe-- data from get_crawl_data (but we can put data from apple scrapper if the columns names are identical)
    neg_dataframe-- neg_df from get_negreview_topic
    topic-- topic from get_negreview_topic
    x-- number of months to inspect

    returns:
    urgency_score-- urgency score
    '''
    print("Please wait, currently we're getting urgency score for negative labeled review!")
    df = neg_dataframe
    topic = topic    
    df_cubi = dataframe
    df_cubi.index = df_cubi['at']
    df.index = df['at']
    df.index =  pd.to_datetime(df.index)
    df_cubi.index =  pd.to_datetime(df_cubi.index)
    df = df[topic].resample('MS').sum().join(pd.DataFrame(df_cubi['review'].resample('MS').count()))
    for kolom in topic:
      df[kolom] = df[kolom].astype(float)
    df.reset_index(inplace=True)
    for i in range(len(df)):
        for kolom in topic:
          if df[kolom][i] > 0:
            df.at[i,kolom] = round((df[kolom][i] / df['review'][i] * 100),2)
  
    urgency_score = pd.DataFrame()
    urgency_score['Topic']= topic
    score = []
    for i in range(len(topic)):
      y = -(statistics.mean(df[topic[i]][-x:]) - df[topic[i]][-1:]).sum() / np.std(df[topic[i]])
      score.insert(i, y)  
    urgency_score['urgency_score']=score
    return urgency_score

#@title Define Function to Run all of Modeling from Preprocessing, Processing, & Analysis as "get_analysis(DATAFRAME)"
def get_analysis(DATAFRAME):
  '''''
  This function combine all of modeling from data preprocessing, data processing, and data analysis

  Input  : Original dataframe from data scrapping
  Output : 
    1. NEG_DATAFRAME    = Negative Labeled Dataframe from topic modeling
    2. topics           = All declared topics for negative review classification
    3. hac_result_df    = Dataframe for High Adjective Count (HAC)
    4. sentence_rank_df = Dataframe for Sentence Ranking
    5. importance_score = Dataframe for Importance Score
    6. urgency_score    = Dataframe for Urgency Score 
  '''''
  
  DATAFRAME = get_translated_language(DATAFRAME)
  preprocessed1 = get_preprocess_data1(DATAFRAME)
  NEG_DATAFRAME, topics = get_topic_modeling_pharma(preprocessed1)
  hac, hac_result_df, nounScores, neg_preprocessed2 = get_HAC(NEG_DATAFRAME)
  sentence_rank_df = get_sentence_ranking(hac, nounScores, neg_preprocessed2, NEG_DATAFRAME)
  severity_score = get_severity_scores(DATAFRAME, NEG_DATAFRAME, topics) 
  X = int(input('Analyze last __ month: '))
  importance_score = get_importancescore(DATAFRAME, X, severity_score, NEG_DATAFRAME, topics)
  urgency_score = get_urgencyscore(DATAFRAME, X, NEG_DATAFRAME, topics)
  print("Congratulations! You get all of the analysis...")
  print("urgency_score, importance_score, sentence_rank_df, hac_result_df, NEG_DATAFRAME, topics")
  return urgency_score, importance_score, sentence_rank_df, hac_result_df, NEG_DATAFRAME, topics

"""#EXPORT PDF
This code will give you the report extreme review table on PDF
"""

!pip install reportlab
from reportlab.platypus import SimpleDocTemplate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors

def  get_extreme_review_table(DATAFRAME, NEG_DATAFRAME, sentence_rank):
  sentence_rank_df['sentence_score'] = round(sentence_rank_df['sentence_score'], 2)
  extreme_review = sentence_rank_df[['review', 'sentence_score']].reset_index()
  index_review = NEG_DATAFRAME[['index']].rename(columns={'index':'id'}).reset_index()
  extreme_review = pd.merge(extreme_review, index_review, how='outer')  
  DATAFRAME = DATAFRAME.reset_index()
  original_review = DATAFRAME[['index', 'review']].rename(columns = {'index':'id', 'review': 'original_review'}, inplace = False)
  extreme_review = pd.merge(extreme_review, original_review, how='left')
  return extreme_review

def transform_text(extreme_review):
  extreme_review = extreme_review[['original_review', 'sentence_score']]
  sentence_rank_1 = extreme_review[:50].reset_index(drop=True).reset_index(col_fill='class', col_level=1, drop=True)

  for i in range(len(sentence_rank_1)):
    words = sentence_rank_1['original_review'].iloc[i].split()
    new_text = ""
    word_count = 0
    for word in words:
      new_text += word + " "
      for a in word:
        word_count += 1
        if word_count == 170 or ".," in word:
          new_text += "\n"
          word_count = 0
    
    sentence_rank_1['original_review'].iloc[i] = new_text
  sentence_rank_1 = sentence_rank_1[['original_review', 'sentence_score']].rename(columns = {'sentence_score': 'score'}, inplace = False)
  return sentence_rank_1

# Default title text
def get_extreme_review(DATAFRAME):
  DATAFRAME1 = get_translated_language(DATAFRAME)
  preprocessed1 = get_preprocess_data1(DATAFRAME1)
  NEG_DATAFRAME, topics = get_topic_modeling_pharma(preprocessed1) ###bisa dihilangkan
  hac, hac_result_df, nounScores, neg_preprocessed2 = get_HAC(NEG_DATAFRAME)
  sentence_rank_df = get_sentence_ranking(hac, nounScores, neg_preprocessed2, NEG_DATAFRAME)
  extreme_review = get_extreme_review_table(DATAFRAME, NEG_DATAFRAME, sentence_rank_df)
  sentence_rank_1 = transform_text(extreme_review)
  return sentence_rank_1

def convert_to_pdf(DATAFRAME):
  extreme_review = get_extreme_review(DATAFRAME)
  fileName = 'Extreme_review.pdf'
  data = extreme_review.reset_index(drop=True).T.reset_index().T.values.tolist()
  pdf = SimpleDocTemplate(fileName, pagesize=(1366,768))
  table = Table(data)

  style = TableStyle([
    ('BACKGROUND', (0,0), (3,0), colors.green),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
    ('ALIGN',(0,0),(-1,-1),'LEFT'),
    ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 10),
    ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ('BACKGROUND',(0,1),(-1,-1),colors.beige),
  ])
  table.setStyle(style)

  # 2) Alternate backgroud color
  rowNumb = len(data)
  for i in range(1, rowNumb):
    if i % 2 == 0:
        bc = colors.burlywood
    else:
        bc = colors.beige
    
    ts = TableStyle(
        [('BACKGROUND', (0,i),(-1,i), bc)]
    )
    table.setStyle(ts)

  # 3) Add borders
  ts = TableStyle(
    [
    ('BOX',(0,0),(-1,-1),2,colors.black),
    ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
    ('LINEABOVE',(0,2),(-1,2),2,colors.green),
    ('GRID',(0,1),(-1,-1),2,colors.black),
    ]
  )
  table.setStyle(ts)

  elems = []
  elems.append(table)

  pdf.build(elems)

convert_to_pdf(DATAFRAME)

"""#PLOT"""

#@title Total Review across Months Plot Function as "plot_alt_total_review_1(dataframe)"
def plot_alt_totalreview_1(dataframe):
  '''
  This function is used to plot total review

  Parameters:
  dataframe-- data from get_crawl_google (but we can put data from apple scrapper if the columns names are identical)
    
  returns:
  plot
  '''
  # Bar Chart "5Miles User Total Review across Months"

  # Preprocessing
  df = dataframe 
  df = dataframe 
  df['at'] = pd.to_datetime(df['at'])
  df.index = df['at']
  df = pd.DataFrame(df['review'].resample('MS').count()).join(pd.DataFrame(df['rating'].resample('MS').mean()))
  
  # Defining selection
  highlight = alt.selection(type='single', on='mouseover',
                          fields=['symbol'], nearest=True)
  
  # Plot
  base = alt.Chart(df[-12:].reset_index()).encode(
      alt.X('at:T', timeUnit= 'yearmonth', axis=alt.Axis(labels=True, title="User Total Review across Months", grid=False, tickCount=12, titleFontSize=20, labelColor='black')),
      tooltip=[alt.Tooltip('review:Q'),
               alt.Tooltip('at:T', format='%b, %Y')]
  )
  
  bar = base.mark_bar(opacity=1, color='#15D7D6', size=20).encode(
      alt.Y('review:Q',
            axis=alt.Axis(labels=False, title=None, grid=False, tickCount=0, titleFontSize=12, labelColor='#999999')),
            tooltip=[alt.Tooltip('review:Q'),
                     alt.Tooltip('at:T', format='%b, %Y')]     
  )
  points = base.mark_circle().encode(
      opacity=alt.value(0) 

  #Functions selections
  ).add_selection(
      highlight
  )

  plot = alt.layer(bar, points).resolve_scale(
      y = 'independent'

  ).configure_title().configure_axis(
      domain=False,
      grid=False,
      labelFontSize = 12,
      titleFontSize = 25  
  ).configure_view(
      strokeOpacity=0,
      strokeWidth=0,
      height=350,
      width=350,
   
  )
  return plot

# @title User Total Review across Version Plot Function as "plot_alt_totalreview_2(dataframe)"
def plot_alt_totalreview_2(dataframe):
    '''
    This function is used to plot total review by version

    Parameters:
    dataframe-- data from get_crawl_data (but we can put data from apple scrapper if the columns names are identical)
    
    returns:
    plot
    '''
    # Bar Chart "5Miles User Total Review across Months"

    # Preprocessing
    df = dataframe
    conditions = [
        (df['rating'] > 3),
        (df['rating'] <= 3)
        ]
    values = ['positive review', 'negative review']
    df['label'] = np.select(conditions, values)
    grouped_multiple = df.groupby(['version', 'label']).agg({'review': ['count']})
    grouped_multiple.columns = ['review']
    grouped_multiple = grouped_multiple.reset_index()

    # Defining selection
    highlight = alt.selection(type='single', on='mouseover',
                          fields=['symbol'], nearest=True)
    color_scale = alt.Scale(
        domain=[
            "positive review",
            "negative review"
                ],
        range=["#19F509", "#FC1D12",]
    )

    # Plot
    base = alt.Chart(grouped_multiple).encode(
        alt.X('version:O', axis=alt.Axis(title="User Total Review across Version", ticks=False, grid=False, titleFontSize=20, labelColor='black', labels=False)),
        tooltip=['version', 'label:N', 'review']
   

    )

    bar = base.mark_bar(opacity=1, color='#15D7D6', size=10).encode(
        alt.Y('review:Q',
              axis=alt.Axis(labels=False, title=None, grid=False, tickCount=0, titleFontSize=12, labelColor='#999999')),
              tooltip=['version', 'label','review'],
              color=alt.Color('label:N', legend=None, scale=color_scale)
          
       
    )
    points = base.mark_circle().encode(
        opacity=alt.value(1),
 
    #Functions selections
    ).add_selection(
        highlight
    )

    plot = alt.layer(bar).resolve_scale(
        y = 'independent'

    ).configure_title().configure_axis(
        domain=False,
        grid=False,
        labelFontSize = 12,
        titleFontSize = 25,
    ).configure_view(
        strokeOpacity=0,
        strokeWidth=0,
        height=500,
        width=1900
    )
    return plot

# @title User Rating Plot Function as "plot_alt_rating_3(dataframe)"
def plot_alt_rating_3(dataframe):
    '''
    This function is used to plot total review by version

    Parameters:
    dataframe-- data from get_crawl_data (but we can put data from apple scrapper if the columns names are identical)
    
    returns:
    plot
    '''
    # Bar Chart "5Miles User Rating"
    # Preprocessing
    df = dataframe
    grouped_multiple = df.groupby(['rating']).agg({'review': ['count']})
    grouped_multiple.columns = ['review']
    grouped_multiple = grouped_multiple.reset_index()
    grouped_multiple.sort_values(by=['rating', 'review'], inplace=True, ascending=False)
    grouped_multiple['value'] = (grouped_multiple['review'] / grouped_multiple['review'].sum()) * 100
    grouped_multiple['value'] = grouped_multiple['value'].round(2).astype(str) + '%'
    grouped_multiple['star'] = grouped_multiple['rating']
    grouped_multiple['star'] = grouped_multiple['star'].astype(str) + '★'
    grouped_multiple
    
    #Defining selection
    highlight = alt.selection(type='single', on='mouseover',
                              fields=['symbol'], nearest=True)
    
    # Plot
    # Double percentage calculation, needs to be improved
    base = alt.Chart(grouped_multiple).transform_joinaggregate(
        TotalReview='sum(review)',
    ).transform_calculate(
        PercentofReview='datum.review / datum.TotalReview' 
    ).mark_bar().encode(
        alt.X('PercentofReview:Q', axis=alt.Axis(title="Total Rating", grid=False, titleFontSize=20, labelColor='black', tickCount=0, format=('.0%'), labels=False))
        
    )
    bar = base.mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10, cornerRadiusBottomLeft=10, cornerRadiusBottomRight=10, opacity=1, color='#8BFC12', size=20).encode(
        alt.Y('star:N', sort=alt.EncodingSortField(field="rating", op="count", order='ascending'),
              axis=alt.Axis(labels=True, title=None, grid=False, tickCount=0, ticks=False, labelColor='black', labelFontSize=15)),
              tooltip=['value'],
              color=alt.Color('rating', legend=None, 
                              scale=alt.Scale(
                                  domain=['1', '2', '3', '4', '5'],
                                  range=['#FF0000', '#ff6600', '#FFFF00', '#99ff00', '#33ff00'])) #Color condition is too complicated, should be improved
    )
    
    points = base.mark_circle().encode(
        opacity=alt.value(1),
        
    #Functions selections
    ).add_selection(
        highlight
    )
    plot = alt.layer(bar).resolve_scale(
        y = 'independent'
        
    ).configure_title().configure_axis(
        domain=False,
        grid=False,
        labelFontSize = 100,
        titleFontSize = 100,
    ).configure_view(
        strokeOpacity=1,
        strokeWidth=0,
        height=100,
        width=700    
    ).configure_axis(
        grid=True, 
        domain=False
    ).properties(height=400)
    return plot

# @title User Complaints by Review Plot ver. 3 Function as "plot_alt_total_negative_three(dataframe, neg_dataframe, topic, addAll = True)"
def plot_alt_total_negative_three(DATAFRAME, NEG_DATAFRAME, TOPIC):
  '''
  Description: Function to show bar chart for complaint by review (v.3).

  Parameter: Total dataframe, negative dataframe, list of topics.

  Return: Altair Chart.

  '''
  # Summarize the data in each month
  df = DATAFRAME
  df_neg = NEG_DATAFRAME
  topic = TOPIC

  df.index = pd.to_datetime(df['at'])
  df_neg.index = pd.to_datetime(df_neg['at'])

  df_neg = df_neg[topic].resample('MS').sum().join(pd.DataFrame(df['review'].resample('MS').count()))

  for kolom in topic:
    df_neg[kolom] = df_neg[kolom].astype(float)

  df_neg.reset_index(inplace=True)

  # Calculate the data and turn it into percent
  for i in range(len(df_neg)):
    for kolom in topic:
      if df_neg[kolom][i] > 0:
        df_neg.at[i,kolom] = round((df_neg[kolom][i] / df_neg['review'][i] * 100),2)

  df_neg.index = df_neg['at']

  # Drop the review column
  no_review = df_neg.drop(['review'], axis=1)

  # Melting the dataframe into something that can easily process in Altair
  new_data = no_review.melt(id_vars=["at"], var_name="Topic", value_name="Total")

  # Dropdown input to filter the bar but, as I expected but still a little bit messy on the look 
  input_dropdown = alt.binding_select(options=topic+[None])
  selection = alt.selection_single(fields=['Topic'], bind=input_dropdown, name='Topic')
  color = alt.condition(selection,
                      alt.Color('Topic:N', legend=None),
                      alt.value('lightgray'))

  chart = alt.Chart(new_data, title="User Complaints").mark_bar().encode(
    column=Column('at', timeUnit='yearmonth', title="Month"),
    x=alt.X('Topic', axis=None),
    y=alt.Y('Total', axis=None),
    color=color,
    tooltip=['Topic', 'Total']
  ).add_selection(selection).configure_title(fontSize=18).configure_axis(grid=False)

  return chart

# @title User Complaints Trendline Plot Function as "plot_alt_total_negative_trendline(dataframe, neg_dataframe, topic, addAll = True)" 
def plot_alt_total_negative_trendline(DATAFRAME, NEG_DATAFRAME, TOPIC):
  '''
  Description: Function to show trendline for complaint by review.

  Parameter: Total dataframe, negative dataframe, list of topics.

  Return: Altair Chart.

  '''
  # Summarize the data in each month
  df = DATAFRAME
  df_neg = NEG_DATAFRAME
  topic = TOPIC

  df.index = pd.to_datetime(df['at'])
  df_neg.index = pd.to_datetime(df_neg['at'])

  df_neg = df_neg[topic].resample('MS').sum().join(pd.DataFrame(df['review'].resample('MS').count()))

  for kolom in topic:
    df_neg[kolom] = df_neg[kolom].astype(float)

  df_neg.reset_index(inplace=True)

  # Calculate the data and turn it into percent
  for i in range(len(df_neg)):
    for kolom in topic:
      if df_neg[kolom][i] > 0:
        df_neg.at[i,kolom] = round((df_neg[kolom][i] / df_neg['review'][i] * 100),2)

  df_neg.index = df_neg['at']

  # Drop the review column
  no_review = df_neg.drop(['review'], axis=1)

  # Melting the dataframe into something that can easily process in Altair
  new_data = no_review.melt(id_vars=["at"], var_name="Topic", value_name="Total")

  # Calculating the Gaussian to smoothen the trendline
  a = gaussian_filter1d(new_data['Total'], 2, mode='nearest')
  a

  # Adding the result as a new column to the dataframe
  new_data['gauss'] = a

  # Make a trendline with drowdown input
  input_dropdown = alt.binding_select(options=topic+[None])
  selection = alt.selection_single(fields=['Topic'], bind=input_dropdown, name='Topic')

  chart = alt.Chart(new_data, title="User Complaints Trendline").mark_line().encode(
      x=alt.X('at', title='Time', axis = alt.Axis(title = 'Time', format = ("%b %Y"))),
      y=alt.Y('gauss', title='Complaint by Reviews (%)', axis=None),
      color=alt.Color('Topic', scale=alt.Scale(scheme='tableau20'), legend=None),
      tooltip=['Topic', 'gauss']
      ).add_selection(selection).transform_filter(selection).configure_title(fontSize=18).configure_axis(grid=False).configure_view(
          strokeWidth=0
      ).properties(
        width=600,
        height=400
      )


  return chart

# @title Problem Solving Priority Matrix function "plot_alt_prioritymatrix(dataframe, neg_dataframe, topic, x)"
def plot_alt_prioritymatrix(dataframe, neg_dataframe, topic, x): 
    '''
    This function is used to plot problem solving priority matrix

    Parameters:
    dataframe-- data from get_crawl_data (but we can put data from apple scrapper if the columns names are identical)
    neg_dataframe-- neg_df from get_negreview_topic
    topic-- topic from get_negreview_topic
    x-- number of months to inspect

    returns:
    priority matrix
    '''
    # priority dataframe from importance score and urgency score
    priority_score = pd.merge(get_importancescore(dataframe, neg_dataframe, topic, x),get_urgencyscore(dataframe, neg_dataframe, topic, x), on='Topic')

    # min max normalization
    importance_score_scaled=[]
    urgency_score_scaled=[]
    score=[]
    for i in range(len(priority_score)):
      z = (priority_score['importance_score'][i] - priority_score['importance_score'].min(axis=0)) / (priority_score['importance_score'].max(axis=0) - priority_score['importance_score'].min(axis=0))
      importance_score_scaled.insert(i,z)
      c = (priority_score['urgency_score'][i] - priority_score['urgency_score'].min(axis=0)) / (priority_score['urgency_score'].max(axis=0) - priority_score['urgency_score'].min(axis=0))
      urgency_score_scaled.insert(i,c)
      a = c+z
      score.insert(i,a)
    priority_score['importance_score_scaled'] = importance_score_scaled
    priority_score['urgency_score_scaled'] = urgency_score_scaled
    priority_score['score'] = score
    priority_score.sort_values(by='score',inplace=True,ascending=False)
    priority_score.reset_index(inplace=True,drop=True)
    priority = list(range(1,len(priority_score)+1))
    priority_score['priority'] = priority

    # plot
    chart = alt.Chart(priority_score, title= 'Problem Solving Priority Matrix', ).mark_circle(size=250).encode(
            alt.X('importance_score_scaled', axis=alt.Axis(title='Importance', values=[0,0.5,1])),
            alt.Y('urgency_score_scaled', axis=alt.Axis(title='Urgency', values=[0,0.5,1])),
            tooltip=['Topic','priority']
            )
    chart.properties(width=400,height=400).configure_title(fontSize=20)
  
    return chart
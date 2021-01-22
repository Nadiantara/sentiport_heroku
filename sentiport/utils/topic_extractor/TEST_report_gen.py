from reportlab.pdfgen import canvas 
import pandas as pd
import numpy as np
import re
import regex
from pylab import *
from langdetect import detect

from google_play_scraper import app, reviews, reviews_all, Sort
from topic_extractor import get_crawl_google, tag_topic, get_topic_df, get_topic_table, app_info
# from utilities.crawling import get_crawl_google, app_info
#####################################################
################### Crawl APP ID ####################
#####################################################

# Input Playstore ID and Country ID here (example playstore ID: **com.linkdokter.halodoc.android** ; Country ID: **ID**)
#com.tangelogames.monstertales not ok
#echo.co.uk ok 
#com.mobile.legends ok
#com.aniplex.fategrandorder.en so-so
#jp.naver.line.android so-so
#com.grabtaxi.passenger
#com.tinder
#com.spotify.music
#com.medium.reader
#com.gojek.app
#com.nike.plusgps
#com.linkdokter.halodoc.android
PLAYSTORE_ID = 'echo.co.uk'
COUNTRY = 'GB'

appinfo = app(
    PLAYSTORE_ID,
    lang='en',
    country=COUNTRY
)

DATAFRAME, appDesc = get_crawl_google(PLAYSTORE_ID, COUNTRY)
# appDesc = app_info(PLAYSTORE_ID, COUNTRY)
df = DATAFRAME
df.rename(columns = {'content' : 'review', 'score' : 'rating'}, inplace = True)
df.dropna(subset=['review'], inplace = True)
df['review'].isna().sum()
print(df)

#####################################################
################### Reportlab PDF ###################
#####################################################
# get the full app title (ex: Halodoc - Doctors, Medicine, & Appiontments)

def deEmojify(text):
    '''
    Remove emoji from review data
    '''
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

def get_preprocess_data2(df):
    '''
    Preprocessing 2 : Remove emoji from review data
    '''
    # print("Please wait, currently we're doing second preprocessing for your review data!")
    df=df.copy()
    df['review']=df['review'].apply(deEmojify)           #removing emoji
    return df

def detect_lang(DATAFRAME):
  '''
  Identify every review data using detect language library
  '''
  # print("Please wait, we're currently detecting the review language!")
  list_lang = []
  row_x = []
  row_xx = []
  min_words_other = 2 #min words filtered 

  for i in range(len(DATAFRAME)):
      if len(DATAFRAME.review[i].split()) <= min_words_other:
        row_xx.append(i)
  DATAFRAME = DATAFRAME.drop(row_xx).reset_index(drop=True)

  for i in range(len(DATAFRAME)):
    try:  
      x = detect(DATAFRAME['review'][i])
      list_lang.append(x)
    except:
      x='no'  
      row_x.append(i)
  DATAFRAME = DATAFRAME.drop(row_x).reset_index(drop=True)
  DATAFRAME['lang'] = pd.DataFrame(list_lang)
  return DATAFRAME

df_lang = detect_lang(df)

# get the full app title (ex: Halodoc - Doctors, Medicine, & Appiontments)
app_title_name, app_desc = app_info(PLAYSTORE_ID, COUNTRY)
# cut the name into short name (ex: Halodoc)
def nama_app (app_title_name):
  app_name=[]
  app_name_count = app_title_name.split()
  if len(app_name_count) > 3 :
    if ':' in app_title_name:
      for i in range(len(app_title_name)):
        if app_title_name[i] == ":":
          for yy in app_title_name[:i]:
            app_name.append(yy)
      app_name = ''.join(app_name)
    elif "–" in app_title_name:
      for i in range(len(app_title_name.split())):
        if app_title_name.split()[i] == "–":
          for yy in app_title_name.split()[(len(app_title_name.split())-i+1):]:
            app_name.append(yy)
      app_name = ' '.join(app_name)
    elif "-" in app_title_name:
      for i in range(len(app_title_name.split())):
        if app_title_name.split()[i] == "-":
          for yy in app_title_name.split()[:i]:
            app_name.append(yy)
      app_name = ' '.join(app_name)
    else:
      app_name = app_title_name.split()
      app_name = app_name[0] 
  else:
    app_name = app_title_name
  return app_name

app_name = nama_app(app_title_name)

# create the report filename using app name
fileName = app_name+'_review_analysis.pdf'

# create the document title 
documentTitle = app_title_name

# define canvas to create the report
pdf = canvas.Canvas(fileName, pagesize=(1366,768))


#############################################################

keyword_df, avg_rating_list, avg_sentiment_list, review_count_list = get_topic_df(df_lang, app_desc, app_title_name)
keyword_df = tag_topic(keyword_df)
list_of_topic = keyword_df.keyword.unique()

for i in range(len(list_of_topic)):  
  #pdf.drawInlineImage("Plain Page Template.png",0,0, width=1366, height=768)
  df_split = keyword_df[keyword_df['keyword']==list_of_topic[i]].reset_index(drop=True).rename(columns={0:'polarity_score'})
  avg_rating = avg_rating_list[i]
  avg_sentiment = avg_sentiment_list[i]
  review_count = review_count_list[i]

  review_table = get_topic_table(df_split)
 
  # set the position of bad review table
  w, h = review_table.wrap(0, 0)
  review_table.drawOn(pdf, 40, 768-675)

  keyword1 = list_of_topic[i]
  average_sentiment = round(avg_sentiment,2)
  average_rating = round(avg_rating,2)
  review_counts = review_count
  rev_len = len(df_split)

  pdf.setFont("Helvetica", 40)
  pdf.drawString(40,768-145, f"Keyword:")
  pdf.setFont("Helvetica-Bold", 40)
  pdf.drawString(215,768-145, f"{keyword1}")
  pdf.setFont("Helvetica", 23)
  pdf.drawString(40,768-180, f"Average Sentiment:")
  pdf.setFont("Helvetica-Bold", 23)
  pdf.drawString(250,768-180, f"{average_sentiment}")
  pdf.setFont("Helvetica", 23)
  pdf.drawString(550,768-180, f"Average Rating:")
  pdf.setFont("Helvetica-Bold", 23)
  pdf.drawString(720,768-180, f"{average_rating}")
  pdf.setFont("Helvetica", 23)
  pdf.drawString(900,768-180, f"Total Reviews:")
  pdf.setFont("Helvetica-Bold", 23)
  pdf.drawString(1060,768-180, f"{rev_len}")
  pdf.setFont("Helvetica", 23)
  pdf.drawString(1080,768-180, f"from")
  pdf.setFont("Helvetica-Bold", 23)
  pdf.drawString(1140,768-180, f"{review_count}")

  pdf.showPage()

############################################################

pdf.save()
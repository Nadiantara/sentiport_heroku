# -*- coding: utf-8 -*-
"""HAC & Sentence Ranking.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wKskKUBDTrliMqBpVbaYWcTvEMovWQDJ
"""

!pip install PyDrive
!pip install reportlab
import pandas as pd
from google.colab import auth
from google.colab import files
from oauth2client.client import GoogleCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors

#@title Google Drive Authentication
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)
# Download dataset from "DATAFRAME_halodoc_translated.csv"
# https://drive.google.com/file/d/1TFwZWD6ctiTPbexsdLfDJl5JeRzdTGSx/view?usp=sharing
downloaded = drive.CreateFile({'id':"1TFwZWD6ctiTPbexsdLfDJl5JeRzdTGSx"})   
downloaded.GetContentFile('DATAFRAME_halodoc_translated.csv')
# https://drive.google.com/file/d/16Uc9YxKpAPMgfULqIb3P7G0_lIPvoACe/view?usp=sharing
downloaded = drive.CreateFile({'id':"16Uc9YxKpAPMgfULqIb3P7G0_lIPvoACe"})   
downloaded.GetContentFile('NEG_DATAFRAME_halodoc_translated.csv')
# https://drive.google.com/file/d/1OIZ8eaN1-3Xb-klZkQ7wZOLU3mTM9sb0/view?usp=sharing
downloaded = drive.CreateFile({'id':"1OIZ8eaN1-3Xb-klZkQ7wZOLU3mTM9sb0"})   
downloaded.GetContentFile('sentence_rank.csv')

DATAFRAME = pd.read_csv('DATAFRAME_halodoc_translated.csv')
NEG_DATAFRAME = pd.read_csv('NEG_DATAFRAME_halodoc_translated.csv')
sentence_rank = pd.read_csv('sentence_rank.csv')

def transform_text(sentence_rank):
  sentence_rank_1 = sentence_rank[:50].reset_index(drop=True)
  sentence_rank_1 = sentence_rank_1.drop('Unnamed: 0',axis='columns').reset_index(col_fill='class', col_level=1, drop = True)

  sentence_rank_1 = sentence_rank[:50].reset_index(drop=True)
  sentence_rank_1 = sentence_rank_1.drop(['Unnamed: 0','sentence_score','noun_score', 'adj_score'],axis='columns').reset_index(col_fill='class', col_level=1)

  for i in range(len(sentence_rank_1)):
    words = sentence_rank_1['review'].iloc[i].split()
    new_text = ""
    word_count = 0
    #print(list_word)
    for word in words:
      new_text += word + " "
      for a in word:
        word_count += 1
        if word_count == 80 or "." in word:
          new_text += "\n"
          word_count = 0
    
    sentence_rank_1['review'].iloc[i] = new_text
  return sentence_rank_1
    
def convert_to_pdf(sentence_rank):
  sentence_rank_1 = transform_text(sentence_rank)
  fileName = 'Extreme_review.pdf'
  data = sentence_rank_1.reset_index(drop=True).T.reset_index().T.values.tolist()
  pdf = SimpleDocTemplate(
      fileName,
      pagesize=letter
  )

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

convert_to_pdf(sentence_rank)
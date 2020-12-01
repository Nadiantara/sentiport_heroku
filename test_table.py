from reportlab.pdfgen import canvas 
from utilities.crawling import *
from pdf_table_reportlab.bad_good_review import get_top5_bad_review,get_top5_good_review,transform_bad_review,transform_good_review
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors

PLAYSTORE_ID = 'com.linkdokter.halodoc.android'
COUNTRY = 'ID'

print("Start!")

start = time.time()
DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY)
one_yr_ago = datetime.now() - relativedelta(years=1)
DATAFRAME.index = DATAFRAME['at']
DATAFRAME = DATAFRAME[DATAFRAME.index.map(pd.to_datetime)>one_yr_ago]
DATAFRAME.reset_index(drop=True, inplace=True)
end = time.time()
print(f"Crawling done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
bad_review = get_top5_bad_review(DATAFRAME)
bad_review = transform_bad_review(bad_review)

good_review = get_top5_good_review(DATAFRAME)
good_review = transform_good_review(good_review)

data = bad_review.reset_index(drop=True).T.reset_index().T.values.tolist()
data1 = good_review.reset_index(drop=True).T.reset_index().T.values.tolist()


table = Table(data)
table1 = Table(data1)

# 1) Set font style
font = TableStyle([
  ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
  ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
  ('FONTSIZE', (0,0), (1,1), 15),
  ('FONTSIZE', (0,1), (1,1), 23),
  ('FONTSIZE', (0,2), (1,2), 21),
  ('FONTSIZE', (0,3), (1,3), 19),
  ('FONTSIZE', (0,4), (1,4), 17),
  ('FONTSIZE', (0,5), (1,5), 15),
  #('FONTSIZE', (0,1), (-1,-1), 15),
])

table.setStyle(font)
table1.setStyle(font)

# 2) Set Table padding
padding = TableStyle([
  ('ALIGN',(0,0),(-1,0),'CENTER'),
  ('ALIGN',(1,1),(-1,-1),'CENTER'),
  ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
  ('ALIGN',(0,1),(-1,0),'LEFT'),
  ('BOTTOMPADDING', (0,0), (-1,0), 15),
  ('BOTTOMPADDING', (0,1), (-1,-1), 12),
  ('TOPPADDING', (0,0), (-1,0), 12),
  ('TOPPADDING', (0,1), (-1,-1), 12),
  ('LEADING', (0,1), (1,1), 25),
  ('LEADING', (0,2), (1,2), 23),
  ('LEADING', (0,3), (1,3), 21),
  ('LEADING', (0,4), (1,4), 19),
  ('LEADING', (0,5), (1,5), 17),

  ('BACKGROUND',(0,1),(-1,-1),colors.burlywood),
])

table.setStyle(padding)
table1.setStyle(padding)

# 3) Alternate backgroud color    
color = TableStyle([
  ('BACKGROUND', (0,0), (3,0), colors.HexColor('#6d0000')),
  ('BACKGROUND', (0,1),(2,1), colors.HexColor('#e66c6c')),
  ('BACKGROUND', (0,2),(2,2), colors.HexColor('#f78686')),
  ('BACKGROUND', (0,3),(2,3), colors.HexColor('#f7a1a1')), 
  ('BACKGROUND', (0,4),(2,4), colors.HexColor('#ffbfbf')), 
  ('BACKGROUND', (0,5),(2,5), colors.HexColor('#ffd6d6')), 
  ]
)

color1 = TableStyle([
  ('BACKGROUND', (0,0), (3,0), colors.green),
  ('BACKGROUND', (0,1),(2,1), colors.HexColor('#57d964')),
  ('BACKGROUND', (0,2),(2,2), colors.HexColor('#71e37d')),
  ('BACKGROUND', (0,3),(2,3), colors.HexColor('#91ed9a')), 
  ('BACKGROUND', (0,4),(2,4), colors.HexColor('#b8fcbf')), 
  ('BACKGROUND', (0,5),(2,5), colors.HexColor('#d6ffda')), 
  ]
)

table.setStyle(color)
table1.setStyle(color1)

end = time.time()
print(f"Good-Bad Review done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

fileName = 'testes.pdf'
pdf = canvas.Canvas(fileName, pagesize=(1366,768))

pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/template_negative_reviews.png',0,0, width=1366, height=768)

w, h = table.wrap(0, 0)
table.drawOn(pdf, 40, 768-620)

pdf.showPage()

pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/positive_review.png',0,0, width=1366, height=768)

w, h = table1.wrap(0, 0)
table1.drawOn(pdf, 40, 768-620)

pdf.save()
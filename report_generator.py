# ###################################
# Content

from utilities.crawling import *
from utilities.helper import *
from plot_detect_language.detect_language import plot_detect_language2
from plot_rating.rating import *
from plot_sentiment_analysis.sentiment_analysis import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from reportlab.pdfgen import canvas 
import time

start = time.time()
PLAYSTORE_ID = 'com.linkdokter.halodoc.android'
COUNTRY = 'ID'
DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY)
one_yr_ago = datetime.now() - relativedelta(years=1)
DATAFRAME.index = DATAFRAME['at']
DATAFRAME = DATAFRAME[DATAFRAME.index.map(pd.to_datetime)>one_yr_ago]
DATAFRAME.reset_index(drop=True, inplace=True)
end = time.time()

print(f"waktu proses crawling data adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
sentiment_dataframe = sentiment_visual_preprocessing(DATAFRAME)
end = time.time()
print(f"waktu pre-proses sentiment adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")


fileName = 'app_overall_analysis.pdf'
documentTitle = app_title(PLAYSTORE_ID, COUNTRY)
title = app_title(PLAYSTORE_ID, COUNTRY)
subTitle = 'Overall Playstore Review Analysis'

start = time.time()
overall_rating = "Current Rating: "+value_overall_rating(PLAYSTORE_ID)
end = time.time()
print(f"waktu proses scrap rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
total_review = "Current Review: "+value_total_review(PLAYSTORE_ID)
end = time.time()
print(f"waktu proses scrap adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_lang, most_lang = plot_detect_language2(DATAFRAME)
end = time.time()
print(f"waktu proses plot language adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_overall_rating = plot_overall_rating(DATAFRAME)
end = time.time()
print(f"waktu proses plot overall rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

# start = time.time()
# fig_rating_time = plot_rating_time(DATAFRAME)
# end = time.time()
# print(f"waktu proses plot rating across time adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

# start = time.time()
# fig_rating_version = plot_rating_version(DATAFRAME)
# end = time.time()
# print(f"waktu proses plot rating across version adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_totalreview_time = plot_totalreview_time(sentiment_dataframe)
end = time.time()
print(f"waktu proses plot total review-time rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_totalreview_version = plot_totalreview_version(sentiment_dataframe)
end = time.time()
print(f"waktu proses plot total review-version rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_totalreview_sentiment = plot_totalreview_sentiment(sentiment_dataframe)
end = time.time()
print(f"waktu proses plot total review-sentiment rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_sentiment_time = plot_sentiment_time(sentiment_dataframe)
end = time.time()
print(f"waktu proses plot total sentiment-time rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

start = time.time()
fig_sentiment_version = plot_sentiment_version(sentiment_dataframe)
end = time.time()
print(f"waktu proses plot total sentiment-version rating adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")

# fig_totalreview_time = 'fig_totalreview_time.png'
# fig_totalreview_version = 'fig_totalreview_version.png'
# fig_totalreview_sentiment = 'fig_review_sentiment.png'
# fig_sentiment_time = 'fig_sentiment_time.png'
# fig_sentiment_version = 'fig_sentiment_version.png'

start = time.time()

pdf = canvas.Canvas(fileName)
pdf.setTitle(documentTitle)

# PAGE 1
# drawMyRuler(pdf)

# App Name - Title 
pdf.setFont("Times-Bold", 14)
pdf.drawCentredString(300, 810, title)

# Sub Title 
pdf.setFont("Times-Roman", 13)
pdf.drawCentredString(300,795, subTitle)

# Draw a line
pdf.line(30, 790, 550, 790)

pdf.setFont("Times-Roman", 12)
pdf.drawCentredString(175,775, overall_rating)

pdf.setFont("Times-Roman", 12)
pdf.drawCentredString(400,775, total_review)

pdf.line(30, 770, 550, 770)

pdf.drawInlineImage(fig_lang, 30, 100, width=550, height=275)
pdf.drawInlineImage(fig_overall_rating, 5, 400, width=325, height=325)
pdf.drawInlineImage(fig_totalreview_sentiment, 350, 400, width=250, height=325)

# page 2
pdf.showPage()

# drawMyRuler(pdf)

# App Name - Title 
pdf.setFont("Times-Bold", 14)
pdf.drawCentredString(300, 810, title)

# Sub Title 
pdf.setFont("Times-Roman", 13)
pdf.drawCentredString(300,795, subTitle)

# Draw a line
pdf.line(30, 790, 550, 790)

# Draw
# pdf.drawInlineImage(, 10, 25, width=550, height=225)
# pdf.drawInlineImage(fig_rating_time, 30, 25, width=550, height=225)
pdf.drawInlineImage(fig_totalreview_time, 30, 275, width=550, height=225)
pdf.drawInlineImage(fig_totalreview_version, 30, 550, width=550, height=225)

# page 3
pdf.showPage()

# drawMyRuler(pdf)

# App Name - Title 
pdf.setFont("Times-Bold", 14)
pdf.drawCentredString(300, 810, title)

# Sub Title 
pdf.setFont("Times-Roman", 13)
pdf.drawCentredString(300,795, subTitle)

# Draw a line
pdf.line(30, 790, 550, 790)

# Draw
# pdf.drawInlineImage(fig_rating_version, 30, 550, width=550, height=225)
pdf.drawInlineImage(fig_sentiment_time, 30, 300, width=550, height=225)
pdf.drawInlineImage(fig_sentiment_version, 30, 50, width=550, height=225)

pdf.save()

end = time.time()
print(f"waktu proses pembuatan pdf file adalah {(end-start)/60} menit dengan jumlah review {(len(DATAFRAME))}")
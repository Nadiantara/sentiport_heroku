from reportlab.pdfgen import canvas 
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from datetime import date
from email.headerregistry import Address
from email.message import EmailMessage
import smtplib
from email.mime.base import MIMEBase 
from email import encoders 

# importing unit 4's functions
from sentiport.utils.utilities.crawling import *
from sentiport.utils.utilities.helper import *
from sentiport.utils.plot_detect_language.detect_language import plot_detect_language2
from sentiport.utils.plot_rating.rating import *
from sentiport.utils.plot_sentiment_analysis.sentiment_analysis import *
from sentiport.utils.pdf_table_reportlab.bad_good_review import get_top5_bad_review, get_top5_good_review, transform_bad_review, transform_good_review

# playstore id and country id input
PLAYSTORE_ID = input('Enter Playstore ID: ')
COUNTRY = input('Enter COUNTRY ID: ')

# targeted email input
targetmail=input('Enter recipient email: ')

# dividing the email into uname and domain (for email function)
for i in range(len(targetmail)):
  if targetmail[i] == '@':
    uname_targetmail = (targetmail[0:i])
    domain_targetmail = (targetmail[-(len(targetmail)-i-1):])

print("Start!")

"""PREPARING PLOTS AND VALUE"""

start = time.time()
# crawling
DATAFRAME = get_crawl_google(PLAYSTORE_ID, COUNTRY) 

# cutting dataframe into maximum 1 year of data
one_yr_ago = datetime.now() - relativedelta(years=1)
DATAFRAME.index = DATAFRAME['at']
DATAFRAME = DATAFRAME[DATAFRAME.index.map(pd.to_datetime)>one_yr_ago]
DATAFRAME.reset_index(drop=True, inplace=True)
end = time.time()
print(f"Crawling done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")
start = time.time()
# sentiment data preprocessing
sentiment_dataframe = sentiment_visual_preprocessing(DATAFRAME)
end = time.time()
print(f"Sentiment pre-processing done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# scrapping current rating
current_rating = value_overall_rating(PLAYSTORE_ID)
end = time.time()
print(f"Rating scrapping done! \n processing time: {(end-start)/60} min")

start = time.time()
# scrapping current total review
current_review = value_total_review(PLAYSTORE_ID)
end = time.time()
print(f"Total Review scrapping done! \n processing time: {(end-start)/60} min")

start = time.time()
# call detect language plot and most language value
fig_lang, most_lang = plot_detect_language2(DATAFRAME)
end = time.time()
print(f"Review Language done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# call overall rating plot
fig_overall_rating = plot_overall_rating(DATAFRAME)
end = time.time()
print(f"Overall Rating done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# call total review by time plot and all the value
fig_totalreview_time, MostReview_Month, MostReview_Month_Value = plot_totalreview_time(sentiment_dataframe)
end = time.time()
print(f"Total review-rating across months done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# call total review by version plot and all the value
fig_totalreview_version, MostReview_Version, MostReview_Version_Value = plot_totalreview_version(DATAFRAME)
end = time.time()
print(f"Total review-rating across version done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# call total review sentiment plot and all the value
fig_totalreview_sentiment, most_sentiment = plot_totalreview_sentiment(sentiment_dataframe)
end = time.time()
print(f"Overall review sentiment done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# call sentiment by time plot and all the value
fig_sentiment_time = plot_sentiment_time(sentiment_dataframe)
end = time.time()
print(f"Review sentiment across time done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# call sentiment by version plot and all the value
fig_sentiment_version, MostPos_Version, MostNeg_Version = plot_sentiment_version(sentiment_dataframe)
end = time.time()
print(f"Review sentiment across version done! \n processing time: {(end-start)/60} min with {(len(DATAFRAME))} reviews")

start = time.time()
# prepare good review and bad review table for plot
bad_review = get_top5_bad_review(DATAFRAME)
bad_review = transform_bad_review(bad_review)
good_review = get_top5_good_review(DATAFRAME)
good_review = transform_good_review(good_review)
bad_tab = bad_review.reset_index(drop=True).T.reset_index().T.values.tolist()
pos_tab = good_review.reset_index(drop=True).T.reset_index().T.values.tolist()
table = Table(bad_tab, [1180, 100])
table1 = Table(pos_tab, [1180, 100])
# Set font style
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
# Set Table padding
padding = TableStyle([
  ('ALIGN',(0,0),(-1,0),'CENTER'),
  ('ALIGN',(1,1),(-1,-1),'CENTER'),
  ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
  ('ALIGN',(0,1),(-1,0),'LEFT'),
  ('BOTTOMPADDING', (0,0), (-1,0), 15),
  ('BOTTOMPADDING', (0,1), (-1,-1), 8),
  ('TOPPADDING', (0,0), (-1,0), 12),
  ('TOPPADDING', (0,1), (-1,-1), 8),
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

# get the full app title (ex: Halodoc - Doctors, Medicine, & Appiontments)
app_title_name = app_title(PLAYSTORE_ID, COUNTRY)

# cut the name into short name (ex: Halodoc)
if "-" in app_title_name:
  app_name=[]
  for i in range(len(app_title_name.split())):
    if app_title_name.split()[i] == "-":
      for yy in app_title_name.split()[:i]:
        app_name.append(yy)
  app_name = ' '.join(app_name)
if ':' in app_title_name:
  app_name = []
  for i in range(len(app_title_name)):
    if app_title_name[i] == ":":
      for yy in app_title_name[:i]:
        app_name.append(yy)
  app_name = ''.join(app_name)
else:
  app_name=app_title_name.split()
  app_name=app_name[0]

# create the report filename using app name
fileName = app_name+'_review_analysis.pdf'

# create the document title 
documentTitle = app_title_name

# define canvas to create the report
pdf = canvas.Canvas(f"sentiport/artifacts/{fileName}", pagesize=(1366, 768))

# get today's date
today = date.today()
hari_ini = today.strftime("%B %d, %Y")

"""CREATING THE PDF"""

print("Creating the PDF")
start = time.time()

""" COVER DEPAN """
# put the opening page template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/cover_template_1.png',0,0, width=1366, height=768)

# set the font, size, and position of date
pdf.setFont("Helvetica", 18)
pdf.drawString(1155,768-63, hari_ini)

# set font, size, and position of app name and report title
pdf.setFont("Helvetica-Bold", 50)
pdf.drawString(75,768-345, app_name)
pdf.setFont("Helvetica", 44)
pdf.drawString(75,768-400, "Application Analysis")

# set font, size, and position of app id and country id
pdf.setFont("Helvetica", 19)
pdf.drawString(75,768-505, f"App ID: {PLAYSTORE_ID}")
pdf.drawString(75,768-525, f"Country ID: {COUNTRY}")

""" TABLE OF CONTENT """
# page break
pdf.showPage()

# put table of content template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/table_of_content.png',0,0, width=1366, height=768)

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Table of Content")

""" EXECUTIVE SUMMARY """
# page break
pdf.showPage()

# put executive summary template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/executive_summary.png',0,0, width=1366, height=768)

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Executive Summary")

""" INTRODUCTION """
# page break
pdf.showPage()

# put the introduction template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/introduction.png',0,0, width=1366, height=768)

# set font, size, and position of app name, app id, country id, and current date
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(117,768-180, "App Name")
pdf.drawString(117,768-215, "App ID")
pdf.drawString(117,768-250, "Country ID")
pdf.drawString(117,768-285, "Current Date")
pdf.setFont("Helvetica-BoldOblique", 20)
pdf.drawString(268,768-180, f": {app_title_name}")
pdf.drawString(268,768-215, f": {PLAYSTORE_ID}")
pdf.drawString(268,768-250, f": {COUNTRY}")
pdf.drawString(268,768-285, f": {hari_ini}")

# set size and position of total rating plot
pdf.drawInlineImage(fig_overall_rating,921,768-635, width=378,height=293) 

# set font, size, and position of current rating and total review
pdf.setFont("Helvetica-Bold", 54)
pdf.drawCentredString(258,768-500, current_review)
pdf.drawCentredString(684,768-500, current_rating)

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Introduction")

""" REVIEW ANALYSIS BY TIME """
# page break
pdf.showPage()

# put review analysis by time template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/review_analysis_by_time.png',0,0, width=1366, height=768)

# set size and position of total review by time plot
pdf.drawInlineImage(fig_totalreview_time,99,768-603, width=1273-99,height=603-125)

# set font, size, and position of insight summary
pdf.setFont("Helvetica-BoldOblique", 36)
pdf.drawCentredString(683,768-665, f"{MostReview_Month} has the highest number of review ({MostReview_Month_Value})")

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Review Analysis by Time")

""" REVIEW ANALYSIS BY VERSION """
# page break
pdf.showPage()

# put review analysis by time template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/review_analysis_by_version.png',0,0, width=1366, height=768)

# set size and position of total review by version plot
pdf.drawInlineImage(fig_totalreview_version,99,768-603, width=1273-99,height=603-125)

# set font, size, and position of insight summary
pdf.setFont("Helvetica-BoldOblique", 36)
pdf.drawCentredString(683,768-665, f"ver. {MostReview_Version} has the highest number of review ({MostReview_Version_Value})")

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Review Analysis by Version")

""" SENTIMENT ANALYSIS """
# page break
pdf.showPage()

# put sentiment analysis template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/sentiment_analysis.png',0,0, width=1366, height=768)

# set the size and position of sentiment by version plot
pdf.drawInlineImage(fig_sentiment_version,48,768-381, width=910-48,height=381-114)
# set the size and position of sentiment by time plot
pdf.drawInlineImage(fig_sentiment_time,48,768-677, width=910-48,height=677-410)
# set the size and position of total review sentiment plot
pdf.drawInlineImage(fig_totalreview_sentiment,932,768-488, width=1327-932,height=488-113)

# set font, size and position of insight summary
pdf.setFont("Helvetica-BoldOblique", 16)
pdf.drawString(935,768-500, f"\t Most of the Review Sentiment is {most_sentiment}")
pdf.drawString(935,768-545, f"\t ver. {MostPos_Version} has the highest positive review")
pdf.drawString(935,768-590, f"\t ver. {MostNeg_Version} has the highest negative review")

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Review Sentiment Analysis")

""" REVIEW LANGUAGE ANALYSIS """
# page break
pdf.showPage()

# put review analysis template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/review_language_analysis.png',0,0, width=1366, height=768)

# set size and position of review language plot
pdf.drawInlineImage(fig_lang,239,768-595, width=1131-239,height=595-134)

# set font, size, and positon of insight summary
pdf.setFont("Helvetica-BoldOblique", 36)
pdf.drawCentredString(683,768-665, f"{most_lang} is the most language used in the reviews")

# set font, size and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Review Language Analysis")

""" BAD REVIEW """
# page break
pdf.showPage()

# put the bad reviewtemplate
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/template_negative_reviews.png',0,0, width=1366, height=768)

# set the position of bad review table
w, h = table.wrap(0, 0)
table.drawOn(pdf, 40, 768-680)

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Top 5 Negative Review")


""" GOOD REVIEW """
# page break
pdf.showPage()

# put good review template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/positive_review.png',0,0, width=1366, height=768)

# set position of good review table
w, h = table1.wrap(0, 0)
table1.drawOn(pdf, 40, 768-680)

# set font, size, and position of footer
pdf.setFont("Helvetica-Bold", 20)
pdf.drawString(20,768-740, app_title_name)
pdf.setFont("Helvetica-Oblique", 20)
pdf.drawString(683,768-740, "| Top 5 Positive Review")

""" CLOSING PAGE """
# page break
pdf.showPage()

# put closing page template
pdf.drawInlineImage(r'sentiport/utils/Template/asset_template/get_other_features.png',0,0, width=1366, height=768)

# saving the report into pdf
pdf.save()

end = time.time()
print(f"PDF Report done! \n processing time: {(end-start)/60} min")


"""SEND THE REPORT THROUGH EMAIL"""

# Account used to send report
email_address = '*****'
email_password = '*****'

# targeted email
to_address = (
    Address(username=uname_targetmail, domain=domain_targetmail),
)

def create_email_message(from_address, to_address, subject,
                         plaintext, html=None):
    msg = EmailMessage()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.set_content(plaintext)
    if html is not None:
        msg.add_alternative(html, subtype='html')
    return msg

# body message
HTML_MESSAGE = """\
    <p>
        Dear Valued Customer,<br>

        <p>
            We are sure that improving your business’ productivity is a top priority for you. Here we send you the preview analysis of your app based on your app's review on Google Playstore. If you’d like any additional and more thorough information about this analysis, we would welcome you to contact us.
            <br><br>
            As a quick refresher, here is what you’ll take away from our services:
            <br>
            <ul>
                <li>How to get information on the full performance of your app by analyzing your <strong>Overall Rating and Review</strong> rate within 6 to 7 months.</li>
                <li><strong>Average Rating and Review</strong> shows more than just a number, you will have more ability to improve your app through average rating analysis either per version or month.</li>
                <li>Want to detect changes in the overall opinion towards your brand? We can also do <strong>Sentiment Analysis</strong> for you.</li>
                <li>Find out more on what languages mostly used on your app review through our <strong>Detect Language</strong> analysis.</li>
                <li>And many more!!</li>
            </ul>
        </p>

        <p>
            <strong>WARNING:</strong> We also have an exclusive package if you are interested in having a long-term contract with us. Even better, we can do <strong>Customized Analysis</strong> for you based on your business’ needs.
            <br><br>
            This service is worth <strong>197 USD</strong> and it will give you more than just informative insights from our analysis. 
            <br><br>
            Just let us know if you have any questions or would like to have a more in-depth conversation. We are here whenever you need us.

            <br><br>
            Best regards,
            <br><br><br>
            Supertype
        </p>

    </p>
"""

msg = create_email_message(
    from_address=email_address,
    to_address=to_address,
    subject=f'{app_name} Review Analysis Report',
    plaintext="Plain text version.",
    html=HTML_MESSAGE
)

# attaching the report into email
filename = fileName
attachment = open(f"sentiport/artifacts/{fileName}", "rb")

p = MIMEBase('application', 'octet-stream') 
p.set_payload((attachment).read()) 

encoders.encode_base64(p) 

p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 

msg.attach(p)

with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login(email_address, email_password)
    smtp_server.send_message(msg)

print('Email sent successfully')

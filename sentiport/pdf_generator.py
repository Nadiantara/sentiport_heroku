from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import time
from datetime import date
from sentiport.utils.utilities.crawling import get_crawl_google, app_title, value_overall_rating, value_total_review, image_company_logo
# from sentiport.utils.utilities.helper import *
from sentiport.utils.plot_detect_language.detect_language import plot_detect_language2
from sentiport.utils.plot_rating.rating import *
from sentiport.utils.plot_sentiment_analysis.sentiment_analysis import *
from sentiport.utils.pdf_table_reportlab.bad_good_review import good_bad_table
from sentiport.utils.topic_extractor.topic_extractor import tag_topic, app_info, get_topic_df, get_topic_table


def short_name(app_title_name):
    # cut the name into short name (ex: Halodoc)
    if "-" in app_title_name:
        app_name = []
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
        app_name = app_title_name.split()
        app_name = app_name[0]

    return app_name


def create_pdf(DF_SOURCE, PLAYSTORE_ID, COUNTRY, temp_dir):

    # cutting dataframe into maximum 1 year of data
    # cutting dataframe into maximum 1 year of data
    one_yr_ago = datetime.now() - relativedelta(years=1)
    DATAFRAME = DF_SOURCE.copy()
    DATAFRAME.index = DATAFRAME['at']
    DATAFRAME = DATAFRAME[DATAFRAME.index.map(pd.to_datetime) > one_yr_ago]
    DATAFRAME.reset_index(drop=True, inplace=True)
    start = time.time()
    # sentiment data preprocessing
    sentiment_dataframe = sentiment_visual_preprocessing(DATAFRAME)
    end = time.time()
    print(
        f"Sentiment pre-processing done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # scrapping current rating
    company_logo = image_company_logo(PLAYSTORE_ID, temp_dir)
    current_rating = value_overall_rating(PLAYSTORE_ID)
    end = time.time()
    print(f"Rating scrapping done! \n processing time: {(end-start)} sec")

    start = time.time()
    # scrapping current total review
    current_review = value_total_review(PLAYSTORE_ID)
    end = time.time()
    print(
        f"Total Review scrapping done! \n processing time: {(end-start)} sec")

    start = time.time()
    # scrapping current rating
    company_logo = image_company_logo(PLAYSTORE_ID, temp_dir)
    end = time.time()
    print(
        f"Company logo scrapping done! \n processing time: {(end-start)} sec")

    start = time.time()
    # call detect language plot and most language value
    fig_lang, most_lang, df_lang = plot_detect_language2(DATAFRAME, temp_dir)
    end = time.time()
    print(
        f"Review Language done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call overall rating plot
    fig_overall_rating = plot_overall_rating(DATAFRAME, temp_dir)
    end = time.time()
    print(
        f"Overall Rating done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call total review by time plot and all the value
    fig_totalreview_time, MostReview_Month, MostReview_Month_Value = plot_totalreview_time(
        sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Total review-rating across months done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call total review by version plot and all the value
    fig_totalreview_version, MostReview_Version, MostReview_Version_Value = plot_totalreview_version(
        DATAFRAME, temp_dir)
    end = time.time()
    print(
        f"Total review-rating across version done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call total review sentiment plot and all the value
    fig_totalreview_sentiment, most_sentiment = plot_totalreview_sentiment(
        sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Overall review sentiment done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call sentiment by time plot and all the value
    fig_sentiment_time = plot_sentiment_time(sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Review sentiment across time done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call sentiment by version plot and all the value
    fig_sentiment_version, MostPos_Version, MostNeg_Version = plot_sentiment_version(
        sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Review sentiment across version done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    start = time.time()
    # prepare good review and bad review table for plot
    negative_table, postive_table = good_bad_table(DATAFRAME)
    end = time.time()
    print(
        f"Good-Bad Review done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    # get the full app title (ex: Halodoc - Doctors, Medicine, & Appiontments)
    app_title_name, app_desc = app_info(PLAYSTORE_ID, COUNTRY)
    app_name = short_name(app_title_name)
    print("APP INFO OK")

   # prepare table for keyword extraction
    keyword_df, avg_rating_list, avg_sentiment_list, review_count_list = get_topic_df(
        df_lang, app_desc, app_title_name)
    keyword_df = tag_topic(keyword_df)
    list_of_topic = keyword_df.keyword.unique()
    end = time.time()
    print(
        f"Keyword Extraction done! \n processing time: {(end-start)} sec with {(len(DATAFRAME))} reviews")

    # create the report filename using app name
    fileName = f'{app_name}_review_analysis.pdf'

    # create the document title
    documentTitle = app_title_name

    # define canvas to create the report
    pdf = canvas.Canvas(
        f"sentiport/artifacts/{temp_dir}/{fileName}", pagesize=(1366, 768))

    # get today's date
    today = date.today()
    hari_ini = today.strftime("%B %d, %Y")

    """CREATING THE PDF"""

    print("Creating the PDF")
    start = time.time()

    """ COVER DEPAN """
    # put the opening page template
    pdf.drawInlineImage(
        'sentiport/utils/assets/cover_template.png', 0, 0, width=1366, height=768)

    # set the font, size, and position of date
    pdf.setFont("Helvetica", 18)
    pdf.drawString(1155, 768-63, hari_ini)

    # put logo in front page
    pdf.drawInlineImage(company_logo, 75, 768-350, width=230, height=230)

    # set font, size, and position of app name and report title
    pdf.setFont("Helvetica-Bold", 50)
    pdf.drawString(75, 768-405, app_name)
    pdf.setFont("Helvetica", 44)
    pdf.drawString(75, 768-460, "Application Analysis")

    # set font, size, and position of app id and country id
    pdf.setFont("Helvetica", 19)
    pdf.drawString(75, 768-505, f"App ID: {PLAYSTORE_ID}")
    pdf.drawString(75, 768-525, f"Country ID: {COUNTRY}")

    """ TABLE OF CONTENT """
    # page break
    pdf.showPage()

    # put table of content template
    pdf.drawInlineImage(
        'sentiport/utils/assets/table_of_content.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Table of Content")

    """ EXECUTIVE SUMMARY """
    # page break
    pdf.showPage()

    # put executive summary template
    pdf.drawInlineImage(
        'sentiport/utils/assets/executive_summary.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Executive Summary")

    """ INTRODUCTION """
    # page break
    pdf.showPage()

    # put the introduction template
    pdf.drawInlineImage('sentiport/utils/assets/Introduction.png',
                        0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set font, size, and position of app name, app id, country id, and current date
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(117, 768-180, "App Name")
    pdf.drawString(117, 768-215, "App ID")
    pdf.drawString(117, 768-250, "Country ID")
    pdf.drawString(117, 768-285, "Current Date")
    pdf.setFont("Helvetica-BoldOblique", 20)
    pdf.drawString(268, 768-180, f": {app_title_name}")
    pdf.drawString(268, 768-215, f": {PLAYSTORE_ID}")
    pdf.drawString(268, 768-250, f": {COUNTRY}")
    pdf.drawString(268, 768-285, f": {hari_ini}")

    # set size and position of total rating plot
    pdf.drawInlineImage(fig_overall_rating, 921, 768 -
                        635, width=378, height=293)

    # set font, size, and position of current rating and total review
    pdf.setFont("Helvetica-Bold", 54)
    pdf.drawCentredString(258, 768-500, current_review)
    pdf.drawCentredString(684, 768-500, current_rating)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Introduction")

    """ REVIEW ANALYSIS BY TIME """
    # page break
    pdf.showPage()

    # put review analysis by time template
    pdf.drawInlineImage(
        'sentiport/utils/assets/review_analysis_by_time.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set size and position of total review by time plot
    pdf.drawInlineImage(fig_totalreview_time, 99, 768 -
                        603, width=1273-99, height=603-125)

    # set font, size, and position of insight summary
    pdf.setFont("Helvetica-BoldOblique", 36)
    pdf.drawCentredString(
        683, 768-665, f"{MostReview_Month} has the highest number of review ({MostReview_Month_Value})")

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Review Analysis by Time")

    """ REVIEW ANALYSIS BY VERSION """
    # page break
    pdf.showPage()

    # put review analysis by time template
    pdf.drawInlineImage(
        'sentiport/utils/assets/review_analysis_by_version.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set size and position of total review by version plot
    pdf.drawInlineImage(fig_totalreview_version, 99, 768 -
                        603, width=1273-99, height=603-125)

    # set font, size, and position of insight summary
    pdf.setFont("Helvetica-BoldOblique", 36)
    pdf.drawCentredString(
        683, 768-665, f"ver. {MostReview_Version} has the highest number of review ({MostReview_Version_Value})")

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Review Analysis by Version")

    """ SENTIMENT ANALYSIS """
    # page break
    pdf.showPage()

    # put sentiment analysis template
    pdf.drawInlineImage(
        'sentiport/utils/assets/sentiment_analysis.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set the size and position of sentiment by version plot
    pdf.drawInlineImage(fig_sentiment_version, 48, 768 -
                        381, width=910-48, height=381-114)
    # set the size and position of sentiment by time plot
    pdf.drawInlineImage(fig_sentiment_time, 48, 768-677,
                        width=910-48, height=677-410)
    # set the size and position of total review sentiment plot
    pdf.drawInlineImage(fig_totalreview_sentiment, 932,
                        768-488, width=1327-932, height=488-113)

    # set font, size and position of insight summary
    pdf.setFont("Helvetica-BoldOblique", 16)
    pdf.drawString(
        935, 768-500, f"\t Most of the Review Sentiment is {most_sentiment}")
    pdf.drawString(
        935, 768-545, f"\t {MostPos_Version} has the highest positive review")
    pdf.drawString(
        935, 768-590, f"\t {MostNeg_Version} has the highest negative review")

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Review Sentiment Analysis")

    """ REVIEW LANGUAGE ANALYSIS """
    # page break
    pdf.showPage()

    # put review analysis template
    pdf.drawInlineImage(
        'sentiport/utils/assets/review_language_analysis.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set size and position of review language plot
    pdf.drawInlineImage(fig_lang, 239, 768-595, width=1131-239, height=595-134)

    # set font, size, and positon of insight summary
    pdf.setFont("Helvetica-BoldOblique", 36)
    pdf.drawCentredString(
        683, 768-665, f"{most_lang} is the most used language in the reviews")

    # set font, size and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Review Language Analysis")

    """ BAD REVIEW """
    # page break
    pdf.showPage()

    # put the bad reviewtemplate
    pdf.drawInlineImage(
        'sentiport/utils/assets/template_negative_reviews.png', 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set the position of bad review table
    w, h = negative_table.wrap(0, 0)
    negative_table.drawOn(pdf, 40, 768-675)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Top 5 Negative Review")

    """ GOOD REVIEW """
    # page break
    pdf.showPage()

    # put good review template
    pdf.drawInlineImage(
        "sentiport/utils/assets/positive_review.png", 0, 0, width=1366, height=768)

    # put logo
    pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)

    # set position of good review table
    w, h = postive_table.wrap(0, 0)
    postive_table.drawOn(pdf, 40, 768-675)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768-740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768-740, "| Top 5 Positive Review")

    """ KEYWORD EXTRACTION TABLE """
    # page break
    pdf.showPage()

    for i in range(len(list_of_topic)):
        # background template
        pdf.drawInlineImage(
            'sentiport/utils/assets/topic_extractions_template.png', 0, 0, width=1366, height=768)

        # put logo
        pdf.drawInlineImage(company_logo, 1135, 768-80, width=55, height=55)
        # table making
        df_split = keyword_df[keyword_df['keyword'] == list_of_topic[i]].reset_index(
            drop=True).rename(columns={0: 'polarity_score'})
        avg_rating = avg_rating_list[i]
        avg_sentiment = avg_sentiment_list[i]
        review_count = review_count_list[i]

        review_table = get_topic_table(df_split)

        # set the position of bad review table
        w, h = review_table.wrap(0, 0)
        review_table.drawOn(pdf, 40, 768-675)

        keyword1 = list_of_topic[i]
        average_sentiment = round(avg_sentiment, 2)
        average_rating = round(avg_rating, 2)
        review_counts = review_count
        rev_len = len(df_split)

        pdf.setFont("Helvetica", 40)
        pdf.drawString(40, 768-145, f"Keyword:")
        pdf.setFont("Helvetica-Bold", 40)
        pdf.drawString(215, 768-145, f"{keyword1}")
        pdf.setFont("Helvetica", 23)
        pdf.drawString(40, 768-180, f"Average Sentiment:")
        pdf.setFont("Helvetica-Bold", 23)
        pdf.drawString(250, 768-180, f"{average_sentiment}")
        pdf.setFont("Helvetica", 23)
        pdf.drawString(550, 768-180, f"Average Rating:")
        pdf.setFont("Helvetica-Bold", 23)
        pdf.drawString(720, 768-180, f"{average_rating}")
        pdf.setFont("Helvetica", 23)
        pdf.drawString(900, 768-180, f"Total Reviews:")
        pdf.setFont("Helvetica-Bold", 23)
        pdf.drawString(1060, 768-180, f"{rev_len}")
        pdf.setFont("Helvetica", 23)
        pdf.drawString(1080, 768-180, f"from")
        pdf.setFont("Helvetica-Bold", 23)
        pdf.drawString(1140, 768-180, f"{review_count}")

        # set font, size, and position of footer
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(20, 768-740, app_title_name)
        pdf.setFont("Helvetica-Oblique", 20)
        pdf.drawString(683, 768-740, "| Topics Extraction")

        pdf.showPage()

    """ CLOSING PAGE """
    # put closing page template
    pdf.drawInlineImage(
        'sentiport/utils/assets/get_other_features.png', 0, 0, width=1366, height=768)

    # saving the report into pdf
    pdf.save()

    end = time.time()
    print(f"PDF Report done! \n processing time: {(end-start)} sec")
    return fileName

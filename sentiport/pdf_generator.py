from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from datetime import date
from sentiport.utils.utilities.crawling import *
from sentiport.utils.utilities.helper import *
from sentiport.utils.plot_detect_language.detect_language import plot_detect_language2
from sentiport.utils.plot_rating.rating import *
from sentiport.utils.plot_sentiment_analysis.sentiment_analysis import *
from sentiport.utils.pdf_table_reportlab.bad_good_review import get_top5_bad_review, get_top5_good_review, \
    transform_bad_review, transform_good_review


def create_pdf(DATAFRAME, PLAYSTORE_ID, COUNTRY, temp_dir):
    # cutting dataframe into maximum 1 year of data
    one_yr_ago = datetime.now() - relativedelta(years=1)
    DATAFRAME = DATAFRAME.copy()
    DATAFRAME.index = DATAFRAME['at']
    DATAFRAME = DATAFRAME[DATAFRAME.index.map(pd.to_datetime) > one_yr_ago]
    DATAFRAME.reset_index(drop=True, inplace=True)
    start = time.time()
    # sentiment data preprocessing
    sentiment_dataframe = sentiment_visual_preprocessing(DATAFRAME)
    end = time.time()
    print(
        f"Sentiment pre-processing done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # scrapping current rating
    current_rating = value_overall_rating(PLAYSTORE_ID)
    end = time.time()
    print(f"Rating scrapping done! \n processing time: {(end - start) / 60} min")

    start = time.time()
    # scrapping current total review
    current_review = value_total_review(PLAYSTORE_ID)
    end = time.time()
    print(f"Total Review scrapping done! \n processing time: {(end - start) / 60} min")

    start = time.time()
    # call detect language plot and most language value
    fig_lang, most_lang = plot_detect_language2(DATAFRAME, temp_dir)
    end = time.time()
    print(f"Review Language done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call overall rating plot
    fig_overall_rating = plot_overall_rating(DATAFRAME, temp_dir)
    end = time.time()
    print(f"Overall Rating done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call total review by time plot and all the value
    fig_totalreview_time, MostReview_Month, MostReview_Month_Value = plot_totalreview_time(
        sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Total review-rating across months done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call total review by version plot and all the value
    fig_totalreview_version, MostReview_Version, MostReview_Version_Value = plot_totalreview_version(
        DATAFRAME, temp_dir)
    end = time.time()
    print(
        f"Total review-rating across version done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call total review sentiment plot and all the value
    fig_totalreview_sentiment, most_sentiment = plot_totalreview_sentiment(
        sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Overall review sentiment done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call sentiment by time plot and all the value
    fig_sentiment_time = plot_sentiment_time(sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Review sentiment across time done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # call sentiment by version plot and all the value
    fig_sentiment_version, MostPos_Version, MostNeg_Version = plot_sentiment_version(
        sentiment_dataframe, temp_dir)
    end = time.time()
    print(
        f"Review sentiment across version done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    start = time.time()
    # prepare good review and bad review table for plot
    bad_review = get_top5_bad_review(DATAFRAME)
    bad_review = transform_bad_review(bad_review)
    good_review = get_top5_good_review(DATAFRAME)
    good_review = transform_good_review(good_review)
    bad_tab = bad_review.reset_index(
        drop=True).T.reset_index().T.values.tolist()
    pos_tab = good_review.reset_index(
        drop=True).T.reset_index().T.values.tolist()
    table = Table(bad_tab, [1180, 100])
    table1 = Table(pos_tab, [1180, 100])

    # Set font style
    font = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (1, 1), 15),
        ('FONTSIZE', (0, 1), (1, 1), 23),
        ('FONTSIZE', (0, 2), (1, 2), 21),
        ('FONTSIZE', (0, 3), (1, 3), 19),
        ('FONTSIZE', (0, 4), (1, 4), 17),
        ('FONTSIZE', (0, 5), (1, 5), 15),
        # ('FONTSIZE', (0,1), (-1,-1), 15),
    ])
    table.setStyle(font)
    table1.setStyle(font)
    # Set Table padding
    padding = TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('LEADING', (0, 1), (1, 1), 25),
        ('LEADING', (0, 2), (1, 2), 23),
        ('LEADING', (0, 3), (1, 3), 21),
        ('LEADING', (0, 4), (1, 4), 19),
        ('LEADING', (0, 5), (1, 5), 17),

        ('BACKGROUND', (0, 1), (-1, -1), colors.burlywood),
    ])
    table.setStyle(padding)
    table1.setStyle(padding)

    # 3) Alternate backgroud color
    color = TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#6d0000')),
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#e66c6c')),
        ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#f78686')),
        ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#f7a1a1')),
        ('BACKGROUND', (0, 4), (2, 4), colors.HexColor('#ffbfbf')),
        ('BACKGROUND', (0, 5), (2, 5), colors.HexColor('#ffd6d6')),
    ]
    )
    color1 = TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.green),
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#57d964')),
        ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#71e37d')),
        ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#91ed9a')),
        ('BACKGROUND', (0, 4), (2, 4), colors.HexColor('#b8fcbf')),
        ('BACKGROUND', (0, 5), (2, 5), colors.HexColor('#d6ffda')),
    ]
    )
    table.setStyle(color)
    table1.setStyle(color1)
    end = time.time()
    print(f"Good-Bad Review done! \n processing time: {(end - start) / 60} min with {(len(DATAFRAME))} reviews")

    # get the full app title (ex: Halodoc - Doctors, Medicine, & Appiontments)
    app_title_name = app_title(PLAYSTORE_ID, COUNTRY)

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
        f'sentiport/utils/Template/asset_template/cover_template.png', 0, 0, width=1366, height=768)

    # set the font, size, and position of date
    pdf.setFont("Helvetica", 18)
    pdf.drawString(1155, 768 - 63, hari_ini)

    # set font, size, and position of app name and report title
    pdf.setFont("Helvetica-Bold", 50)
    pdf.drawString(75, 768 - 345, app_name)
    pdf.setFont("Helvetica", 44)
    pdf.drawString(75, 768 - 400, "Application Analysis")

    # set font, size, and position of app id and country id
    pdf.setFont("Helvetica", 19)
    pdf.drawString(75, 768 - 505, f"App ID: {PLAYSTORE_ID}")
    pdf.drawString(75, 768 - 525, f"Country ID: {COUNTRY}")

    """ TABLE OF CONTENT """
    # page break
    pdf.showPage()

    # put table of content template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/table_of_content.png', 0, 0, width=1366, height=768)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Table of Content")

    """ EXECUTIVE SUMMARY """
    # page break
    pdf.showPage()

    # put executive summary template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/executive_summary.png', 0, 0, width=1366, height=768)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Executive Summary")

    """ INTRODUCTION """
    # page break
    pdf.showPage()

    # put the introduction template
    pdf.drawInlineImage('sentiport/utils/Template/asset_template/Introduction.png', 0, 0, width=1366, height=768)

    # set font, size, and position of app name, app id, country id, and current date
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(117, 768 - 180, "App Name")
    pdf.drawString(117, 768 - 215, "App ID")
    pdf.drawString(117, 768 - 250, "Country ID")
    pdf.drawString(117, 768 - 285, "Current Date")
    pdf.setFont("Helvetica-BoldOblique", 20)
    pdf.drawString(268, 768 - 180, f": {app_title_name}")
    pdf.drawString(268, 768 - 215, f": {PLAYSTORE_ID}")
    pdf.drawString(268, 768 - 250, f": {COUNTRY}")
    pdf.drawString(268, 768 - 285, f": {hari_ini}")

    # set size and position of total rating plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_overall_rating}"
    pdf.drawInlineImage(img, 921, 768 - 635, width=378, height=293)
    

    # set font, size, and position of current rating and total review
    pdf.setFont("Helvetica-Bold", 54)
    pdf.drawCentredString(258, 768 - 500, current_review)
    pdf.drawCentredString(684, 768 - 500, current_rating)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Introduction")

    """ REVIEW ANALYSIS BY TIME """
    # page break
    pdf.showPage()

    # put review analysis by time template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/review_analysis_by_time.png', 0, 0, width=1366,
                        height=768)

    # set size and position of total review by time plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_totalreview_time}"
    pdf.drawInlineImage(img, 99, 768 - 603, width=1273 - 99, height=603 - 125)
    

    # set font, size, and position of insight summary
    pdf.setFont("Helvetica-BoldOblique", 36)
    pdf.drawCentredString(
        683, 768 - 665, f"{MostReview_Month} has the highest number of review ({MostReview_Month_Value})")

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Review Analysis by Time")

    """ REVIEW ANALYSIS BY VERSION """
    # page break
    pdf.showPage()

    # put review analysis by time template
    pdf.drawInlineImage(f'sentiport/utils/Template/asset_template/review_analysis_by_version.png', 0, 0, width=1366,
                        height=768)

    # set size and position of total review by version plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_totalreview_version}"
    pdf.drawInlineImage(img, 99, 768 - 603, width=1273 - 99, height=603 - 125)
    

    # set font, size, and position of insight summary
    pdf.setFont("Helvetica-BoldOblique", 36)
    pdf.drawCentredString(
        683, 768 - 665, f"ver. {MostReview_Version} has the highest number of review ({MostReview_Version_Value})")

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Review Analysis by Version")

    """ SENTIMENT ANALYSIS """
    # page break
    pdf.showPage()

    # put sentiment analysis template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/sentiment_analysis.png', 0, 0, width=1366, height=768)

    # set the size and position of sentiment by version plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_sentiment_version}"
    pdf.drawInlineImage(img, 48, 768 - 381, width=910 - 48, height=381 - 114)
    
    
    # set the size and position of sentiment by time plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_sentiment_time}"
    pdf.drawInlineImage(img, 48, 768 - 677, width=910 - 48, height=677 - 410)
    

    # set the size and position of total review sentiment plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_totalreview_sentiment}"
    pdf.drawInlineImage(img, 932, 768 - 488, width=1327 - 932, height=488 - 113)
    

    # set font, size and position of insight summary
    pdf.setFont("Helvetica-BoldOblique", 16)
    pdf.drawString(
        935, 768 - 500, f"\t Most of the Review Sentiment is {most_sentiment}")
    pdf.drawString(
        935, 768 - 545, f"\t ver. {MostPos_Version} has the highest positive review")
    pdf.drawString(
        935, 768 - 590, f"\t ver. {MostNeg_Version} has the highest negative review")

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Review Sentiment Analysis")

    """ REVIEW LANGUAGE ANALYSIS """
    # page break
    pdf.showPage()

    # put review analysis template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/review_language_analysis.png', 0, 0, width=1366, height=768)

    # set size and position of review language plot
    img = f"sentiport/artifacts/{temp_dir}/{fig_lang}"
    pdf.drawInlineImage(img, 239, 768 - 595, width=1131 - 239, height=595 - 134)
    

    # set font, size, and positon of insight summary
    pdf.setFont("Helvetica-BoldOblique", 36)
    pdf.drawCentredString(
        683, 768 - 665, f"{most_lang} is the most language used in the reviews")

    # set font, size and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Review Language Analysis")

    """ BAD REVIEW """
    # page break
    pdf.showPage()

    # put the bad reviewtemplate
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/template_negative_reviews.png', 0, 0, width=1366, height=768)

    # set the position of bad review table
    try:
        w, h = table.wrap(0, 0)
        table.drawOn(pdf, 40, 768 - 680)
    except IndexError:
        pass

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Top 5 Negative Review")

    """ GOOD REVIEW """
    # page break
    pdf.showPage()

    # put good review template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/positive_review.png', 0, 0, width=1366, height=768)

    # set position of good review table
    w, h = table1.wrap(0, 0)
    table1.drawOn(pdf, 40, 768 - 680)

    # set font, size, and position of footer
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(20, 768 - 740, app_title_name)
    pdf.setFont("Helvetica-Oblique", 20)
    pdf.drawString(683, 768 - 740, "| Top 5 Positive Review")

    """ CLOSING PAGE """
    # page break
    pdf.showPage()

    # put closing page template
    pdf.drawInlineImage(
        f'sentiport/utils/Template/asset_template/get_other_features.png', 0, 0, width=1366, height=768)

    # saving the report into pdf
    pdf.save()

    end = time.time()
    print(f"PDF Report done! \n processing time: {(end - start) / 60} min")
    return fileName

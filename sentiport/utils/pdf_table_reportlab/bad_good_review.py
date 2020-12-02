import re
import string
import pandas as pd
from googletrans import Translator
from langdetect import detect
from tqdm.notebook import tnrange
from textblob import TextBlob
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from math import log

translator = Translator()


def get_word_count(DATAFRAME):
    DATAFRAME = DATAFRAME.copy()
    dataframe = DATAFRAME[['review', 'rating']]
    word_count = []
    word_count_log2 = []
    for i in range(len(dataframe)):
        word_count.append(len(dataframe['review'][i].split()))
    dataframe['word_count'] = pd.DataFrame(word_count)
    for i in range(len(dataframe)):
        word_count_log2.append(log(dataframe['word_count'][i], 2))
    dataframe['word_count_score'] = pd.DataFrame(word_count_log2)
    return dataframe


def clean_text_round1(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text


def get_clean_review(dataframe):
    def round1(x): return clean_text_round1(x)
    df_clean = pd.DataFrame(dataframe.review.apply(round1))
    df_clean['rating'] = dataframe['rating']
    df_clean['word_count_score'] = dataframe['word_count_score']
    return df_clean

# @title Define Translator as "get_translated_language(DATAFRAME)"


def translate_to_english(review):
    translation = translator.translate(review, dest='en', src='id')
    return translation.text


def detect_lang(NEG_DATAFRAME):
    # print("First batch translations!")
    #NEG_DATAFRAME = get_negative_review(DATAFRAME)
    for i in tnrange(len(NEG_DATAFRAME)):
        try:
            lang = detect(NEG_DATAFRAME['review'][i])
            if lang == 'id':
                NEG_DATAFRAME['review'].iloc[i] = translate_to_english(
                    NEG_DATAFRAME['review'][i])
        except:
            lang = 'no'
            #  print("This row throws error:", NEG_DATAFRAME['review'][i])
    return NEG_DATAFRAME


def detect_lang2(NEG_DATAFRAME):
    # print("Second batch translations!")
    for i in tnrange(len(NEG_DATAFRAME)):
        try:
            lang = detect(NEG_DATAFRAME['review'][i])
            if lang == 'id':
                NEG_DATAFRAME['review'].iloc[i] = translate_to_english(
                    NEG_DATAFRAME['review'][i])
        except:
            lang = 'no'
            #  print("This row throws error:", NEG_DATAFRAME['review'][i])
    return NEG_DATAFRAME


def get_translated_language(DATAFRAME):
    # print("Please wait, currently we're translating your negative review into English!")
    if 'index' in DATAFRAME.columns:
        pass
    else:
        DATAFRAME = DATAFRAME.reset_index()
    NEG_DATAFRAME = detect_lang(DATAFRAME)
    NEG_DATAFRAME = detect_lang2(NEG_DATAFRAME)
    DATAFRAME = pd.concat([DATAFRAME, NEG_DATAFRAME]).drop_duplicates(
        ['review', 'rating', 'word_count_score'], keep='last').sort_values('word_count_score', ascending=False)
    return DATAFRAME


def get_sentiment_score(bad_review):
    def pol(x): return TextBlob(x).sentiment.polarity
    def sub(x): return TextBlob(x).sentiment.subjectivity

    sentiment_df = bad_review
    sentiment_df['polarity'] = sentiment_df['review'].apply(pol)
    sentiment_df['subjectivity'] = sentiment_df['review'].apply(sub)
    sentiment_df['score'] = sentiment_df['word_count_score'] * \
        sentiment_df['polarity']
    sentiment_df = sentiment_df.sort_values(
        'score', ascending=True).reset_index(drop=True)
    return sentiment_df

# def convert_lowercase(text):
#    '''Make text lowercase.'''
#    text = text[0] + text[1:].lower()
#    return text

# def get_lowercase(dataframe):
#  round2 = lambda x: convert_lowercase(x)
#  df_clean = pd.DataFrame(dataframe.original_review.apply(round2))
#  df_clean['index'] = dataframe['index']
#  df_clean['rating'] = dataframe['rating']
#  df_clean['word_count_score'] = dataframe['word_count_score']
#  return df_clean


def top_bad_review(dataframe, bad_review):
    dataframe = dataframe.copy()
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={'review': 'original_review'})
    #dataframe = get_lowercase(dataframe)

    bad_review = bad_review.rename(columns={'score': 'worse_score'})
    bad_review = pd.merge(bad_review, dataframe, on=[
                          'index', 'rating', 'word_count_score'], how='inner')
    bad_review = bad_review[['original_review', 'worse_score']]
    bad_review = bad_review.sort_values(
        'worse_score', ascending=True).reset_index(drop=True)
    bad_review['worse_score'] = - \
        (bad_review['worse_score']/bad_review['worse_score'][0])
    bad_review = bad_review[:5]
    return bad_review


def get_top5_bad_review(DATAFRAME):
    DATAFRAME = DATAFRAME.copy()
    dataframe = get_word_count(DATAFRAME)
    df_clean = get_clean_review(dataframe)
    bad_review = df_clean[df_clean['rating'] < 2]
    bad_review = get_translated_language(bad_review)
    bad_review = bad_review.reset_index(drop=True)
    bad_review = get_sentiment_score(bad_review)
    bad_review = top_bad_review(dataframe, bad_review)
    return bad_review


def get_good_review(dataframe):
    dataframe = dataframe.reset_index()
    good_review = dataframe[dataframe['rating'] == 5].sort_values(
        'word_count_score', ascending=False)  # .reset_index()
    good_review = good_review[:100]
    return good_review


def top_good_review(dataframe, good_review):
    dataframe = dataframe.copy()
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={'review': 'original_review'})
    #dataframe = get_lowercase(dataframe)

    good_review = good_review.rename(columns={'score': 'good_score'})
    good_review = pd.merge(good_review, dataframe, on=[
                           'index', 'rating', 'word_count_score'], how='inner')
    good_review = good_review[['original_review', 'good_score']]
    good_review = good_review.sort_values(
        'good_score', ascending=False).reset_index(drop=True)
    good_review['good_score'] = good_review['good_score'] / \
        good_review['good_score'][0]
    good_review = good_review[:5]
    return good_review


def get_top5_good_review(DATAFRAME):
    DATAFRAME = DATAFRAME.copy()
    dataframe = get_word_count(DATAFRAME)
    good_review = get_good_review(dataframe)
    df_clean = get_clean_review(good_review)
    good_review = get_translated_language(df_clean)
    good_review = good_review.reset_index(drop=True)
    good_review = get_sentiment_score(good_review)
    good_review = top_good_review(dataframe, good_review)
    return good_review


def add_enter(dataframe, row_number):
    if row_number == 0:
        max_number = 82
        max_enter = 4
    if row_number == 1:
        max_number = 92
        max_enter = 3
    if row_number == 2:
        max_number = 102
        max_enter = 3
    if row_number == 3:
        max_number = 112
        max_enter = 3
    if row_number == 4:
        max_number = 122
        max_enter = 3
    if row_number > 4:
        max_number = 132
        max_enter = 2

    words_count = len(dataframe['original_review'].iloc[row_number])
    words = dataframe['original_review'].iloc[row_number][:450].split()
    str1 = dataframe['original_review'].iloc[row_number][:450]

    total = 0
    for i in str1:
        total = total + 1

    new_text = ""
    word_count = 0
    num_enter = 0
    word_count_total = 0
    for word in words:
        new_text += word + " "
        for a in word:
            count1 = 0
            count2 = 0
            if(a.islower()):
                count1 = 1
            elif(a.isupper()):
                count2 = 1.5
            word_count += count1 + count2
            if word_count == max_number or ".," in word:
                new_text += "\n"
                num_enter += 1
                word_count = 0

    if words_count > len(str1):
        new_text += "..."

    for i in new_text:
        word_count_total = word_count_total + 1

    if word_count_total == total+1+num_enter:
        enter_needed = max_enter - num_enter
        for i in range(enter_needed):
            new_text += "\n"

    dataframe['original_review'].iloc[row_number] = new_text
    return dataframe


def transform_bad_review(bad_review):
    bad_review = bad_review.copy()
    bad_review['worse_score'] = round(bad_review['worse_score'], 2)
    bad_review = bad_review[['original_review', 'worse_score']]
    sentence_rank_1 = bad_review[:50].reset_index(
        drop=True).reset_index(col_fill='class', col_level=1, drop=True)

    for i in range(len(sentence_rank_1)):
        sentence_rank_1 = add_enter(sentence_rank_1, i)

    sentence_rank_1 = sentence_rank_1[['original_review', 'worse_score']].rename(
        columns={'original_review': 'Reviews'}, inplace=False)
    return sentence_rank_1


def transform_good_review(good_review):
    good_review = good_review.copy()
    good_review['good_score'] = round(good_review['good_score'], 2)
    good_review = good_review[['original_review', 'good_score']]
    sentence_rank_1 = good_review[:50].reset_index(
        drop=True).reset_index(col_fill='class', col_level=1, drop=True)

    for i in range(len(sentence_rank_1)):
        sentence_rank_1 = add_enter(sentence_rank_1, i)

    sentence_rank_1 = sentence_rank_1[['original_review', 'good_score']].rename(
        columns={'original_review': 'Reviews'}, inplace=False)
    return sentence_rank_1


def convert_to_pdf(DATAFRAME):

    bad_review = get_top5_bad_review(DATAFRAME)
    bad_review = transform_bad_review(bad_review)

    good_review = get_top5_good_review(DATAFRAME)
    good_review = transform_good_review(good_review)

    fileName = 'good_bad_review_report.pdf'
    data = bad_review.reset_index(drop=True).T.reset_index().T.values.tolist()
    data1 = good_review.reset_index(
        drop=True).T.reset_index().T.values.tolist()
    pdf = SimpleDocTemplate(fileName, pagesize=(1366, 768))

    titleTable = Table([['']], 1200)
    table = Table(data, [1100, 100])
    table1 = Table(data1, [1100, 100])

    # 1) Set font style
    font = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (1, 1), 15),
        ('FONTSIZE', (0, 1), (1, 1), 23),
        ('FONTSIZE', (0, 2), (1, 2), 21),
        ('FONTSIZE', (0, 3), (1, 3), 19),
        ('FONTSIZE', (0, 4), (1, 4), 17),
        ('FONTSIZE', (0, 5), (1, 5), 15),
        #('FONTSIZE', (0,1), (-1,-1), 15),
    ])

    table.setStyle(font)
    table1.setStyle(font)

    # 2) Set Table padding
    padding = TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
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
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#9f8159')),
        ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#b59a76')),
        ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#c2aa8a')),
        ('BACKGROUND', (0, 4), (2, 4), colors.HexColor('#c9b69d')),
        ('BACKGROUND', (0, 5), (2, 5), colors.HexColor('#dcd3c4')),
    ]
    )

    color1 = TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.black),
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#9f8159')),
        ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#b59a76')),
        ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#c2aa8a')),
        ('BACKGROUND', (0, 4), (2, 4), colors.HexColor('#c9b69d')),
        ('BACKGROUND', (0, 5), (2, 5), colors.HexColor('#dcd3c4')),
    ]
    )

    table.setStyle(color)
    table1.setStyle(color1)

    #   3) Add borders
    #   ts = TableStyle(
    #     [
    #     ('BOX',(0,0),(-1,-1),2,colors.black),
    #     ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
    #     ('LINEABOVE',(0,2),(-1,2),2,colors.green),
    #     ('GRID',(0,1),(-1,-1),2,colors.black),
    #     ]
    #   )
    #   table.setStyle(ts)

    #   ts1 = TableStyle(
    #     [
    #     ('BOX',(0,0),(-1,-1),2,colors.black),
    #     ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
    #     ('LINEABOVE',(0,2),(-1,2),2,colors.green),
    #     ('GRID',(0,1),(-1,-1),2,colors.black),
    #     ]
    #   )
    #   table1.setStyle(ts1)

    mainTable = Table([
        [table],
        [table1]
    ])

    elems = []
    elems.append(mainTable)

    pdf.build(elems)


def generate_table_config(len_table):
    font_config = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (1, 1), 15),
    ] + [
        ('FONTSIZE', (0, i), (1, i), 21) for i in range(1, len_table + 1)
    ]
    font = TableStyle(font_config)

    pad_config = [
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, 0), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ] + [
        ('LEADING', (0, i), (1, i), 23) for i in range(1, len_table + 1)
    ] + [
        ('BACKGROUND', (0, 1), (-1, -1), colors.burlywood)
    ]
    padding = TableStyle(pad_config)

    color_config = [
        ('BACKGROUND', (0, 0), (3, 0), colors.black),
    ] + [
        ('BACKGROUND', (0, 1), (2, 1), colors.HexColor('#9f8159')),
        ('BACKGROUND', (0, 2), (2, 2), colors.HexColor('#b59a76')),
        ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#c2aa8a')),
        ('BACKGROUND', (0, 4), (2, 4), colors.HexColor('#c9b69d')),
        ('BACKGROUND', (0, 5), (2, 5), colors.HexColor('#dcd3c4')),
    ][:len_table]
    color = TableStyle(color_config)

    return font, padding, color


def good_bad_table(DATAFRAME):
    bad_review = get_top5_bad_review(DATAFRAME)
    bad_review = transform_bad_review(bad_review)
    good_review = get_top5_good_review(DATAFRAME)
    good_review = transform_good_review(good_review)
    bad_tab = bad_review.reset_index(
        drop=True).T.reset_index().T.values.tolist()
    pos_tab = good_review.reset_index(
        drop=True).T.reset_index().T.values.tolist()
    negative_table = Table(bad_tab, [1180, 100])
    positive_table = Table(pos_tab, [1180, 100])

    font_bad, paddding_bad, color_bad = generate_table_config(len(bad_review))
    font_good, paddding_good, color_good = generate_table_config(
        len(bad_review))

    negative_table.setStyle(font_bad)
    positive_table.setStyle(font_good)

    negative_table.setStyle(paddding_bad)
    positive_table.setStyle(paddding_good)

    negative_table.setStyle(color_bad)
    positive_table.setStyle(color_good)
    return negative_table, positive_table

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
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from math import log
styleSheet = getSampleStyleSheet()
translator = Translator()


def get_word_count(DATAFRAME):
    dataframe = DATAFRAME.copy()[['review', 'rating']]
    word_count = []
    word_count_log2 = []
    for i in range(len(dataframe)):
        word_count.append(len(dataframe['review'][i].split()))
    # dataframe['word_count'] = pd.DataFrame(word_count)
    dataframe.loc[:, 'word_count'] = word_count
    for i in range(len(dataframe)):
        word_count_log2.append(log(dataframe['word_count'][i], 2))
    # dataframe['word_count_score'] = pd.DataFrame(word_count_log2)
    dataframe.loc[:, 'word_count_score'] = word_count_log2
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
    # NEG_DATAFRAME = get_negative_review(DATAFRAME)
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


def deEmojify(text):
    '''
    Remove emoji from review data
    '''
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                u"\U00002702-\U000027B0"
                                u"\U000024C2-\U0001F251"
                                u"\U0001f926-\U0001f937"
                                u"\U00010000-\U0010ffff"
                                u"\u2640-\u2642"
                                u"\u2600-\u2B55"
                                u"\u200d"
                                u"\u23cf"
                                u"\u23e9"
                                u"\u231a"
                                u"\ufe0f"  # dingbats
                                u"\u3030"
                                "]+", flags=re.UNICODE)
    text = regrex_pattern.sub(r'', text)
    text = text.replace('\n', ' ')
    text = re.sub(' +', ' ', text)

    return text


def remove_emoji(dataframe):
    '''
    Preprocessing 2 : Remove emoji from review data
    '''
    print("Please wait, currently we're doing second preprocessing for your review data!")
    dataframe = dataframe.copy()
    dataframe['original_review'] = dataframe['original_review'].apply(
        deEmojify)  # removing emoji
    return dataframe


def top_bad_review(dataframe, bad_review):
    dataframe = dataframe.copy()
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={'review': 'original_review'})
    # dataframe = get_lowercase(dataframe)
    dataframe = remove_emoji(dataframe)

    # bad_review = bad_review.rename(columns={'score':'score'})
    bad_review = pd.merge(bad_review, dataframe, on=[
                          'index', 'rating', 'word_count_score'], how='inner')
    bad_review = bad_review[['original_review', 'score']]
    bad_review = bad_review.sort_values(
        'score', ascending=True).reset_index(drop=True)
    bad_review['score'] = -(bad_review['score']/bad_review['score'][0])
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
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={'review': 'original_review'})
    # dataframe = get_lowercase(dataframe)
    dataframe = remove_emoji(dataframe)

    # good_review = good_review.rename(columns={'score':'score'})
    good_review = pd.merge(good_review, dataframe, on=[
                           'index', 'rating', 'word_count_score'], how='inner')
    good_review = good_review[['original_review', 'score']]
    good_review = good_review.sort_values(
        'score', ascending=False).reset_index(drop=True)
    good_review['score'] = good_review['score']/good_review['score'][0]
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
    # dataframe['original_review'].iloc[row_number] = new_text
    dataframe.iloc[row_number, dataframe.columns.get_loc(
        'original_review')] = new_text
    return dataframe


def tag_words(dataframe, row_number):
    words = dataframe.original_review[row_number].split()

    senti_words = []
    sent_words = []
    for word in words:
        sent_words.append(word)
        senti_words.append(TextBlob(word).sentiment.polarity)

    senti_dict = [(sent_words[idx], senti_words[idx])
                  for idx in range(len(words))]

    new_text = ""
    i = 0
    for word, senti_score in senti_dict:
        if senti_score > 0:
            if i == 0:
                new_text = "<font color=#199600><b>" + word + "</b></font>"
            elif i > 0:
                new_text += " " + "<font color=#199600><b>" + word + "</b></font>"
        elif senti_score < 0:
            if i == 0:
                new_text = "<font color=#8a0000><b>" + word + "</b></font>"
            elif i > 0:
                new_text += " " + "<font color=#8a0000><b>" + word + "</b></font>"
        elif senti_score == 0:
            if i == 0:
                new_text = word
            elif i > 0:
                new_text += " " + word
        i += 1

    new_text

    # dataframe['original_review'].iloc[row_number] = new_text
    dataframe.iloc[row_number, dataframe.columns.get_loc(
        'original_review')] = new_text

    return dataframe


def transform_bad_review(bad_review):
    bad_review['score'] = round(bad_review['score'], 2)
    bad_review = bad_review[['original_review', 'score']]
    sentence_rank_1 = bad_review[:50].reset_index(
        drop=True).reset_index(col_fill='class', col_level=1, drop=True)

    for i in range(len(sentence_rank_1)):
        sentence_rank_1 = add_enter(sentence_rank_1, i)
        sentence_rank_1 = tag_words(sentence_rank_1, i)

    sentence_rank_1 = sentence_rank_1[['original_review', 'score']].rename(
        columns={'original_review': 'Reviews'}, inplace=False)
    return sentence_rank_1


def transform_good_review(good_review):
    good_review['score'] = round(good_review['score'], 2)
    good_review = good_review[['original_review', 'score']]
    sentence_rank_1 = good_review[:50].reset_index(
        drop=True).reset_index(col_fill='class', col_level=1, drop=True)

    for i in range(len(sentence_rank_1)):
        sentence_rank_1 = add_enter(sentence_rank_1, i)
        sentence_rank_1 = tag_words(sentence_rank_1, i)

    sentence_rank_1 = sentence_rank_1[['original_review', 'score']].rename(
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
        # ('FONTSIZE', (0,1), (-1,-1), 15),
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

    mainTable = Table([
        [table],
        [table1]
    ])

    elems = []
    elems.append(mainTable)

    pdf.build(elems)


def good_bad_table(DATAFRAME):
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    ps = ParagraphStyle('title', fontSize=20, leading=22)

    bad_review = get_top5_bad_review(DATAFRAME)
    bad_review = transform_bad_review(bad_review)
    bad_review = bad_review[bad_review['score'] < 0]
    good_review = get_top5_good_review(DATAFRAME)
    good_review = transform_good_review(good_review)
    good_review = good_review[good_review['score'] > 0]

    # bad_tab = bad_review.reset_index(drop=True).T.reset_index().T.values.tolist()
    # pos_tab = good_review.reset_index(drop=True).T.reset_index().T.values.tolist()

    list_bad_reviews = ['', '', '', '', '']
    list_bad_scores = ['', '', '', '', '']
    list_good_reviews = ['', '', '', '', '']
    list_good_scores = ['', '', '', '', '']

    for i in range(len(bad_review)):
        list_bad_reviews[i] = bad_review.Reviews[i]
        list_bad_scores[i] = bad_review.score[i]

    for i in range(len(good_review)):
        list_good_reviews[i] = good_review.Reviews[i]
        list_good_scores[i] = good_review.score[i]

    bad_tab = [['Reviews', 'score'],
               [Paragraph(list_bad_reviews[0], ps), list_bad_scores[0]],
               [Paragraph(list_bad_reviews[1], ps), list_bad_scores[1]],
               [Paragraph(list_bad_reviews[2], ps), list_bad_scores[2]],
               [Paragraph(list_bad_reviews[3], ps), list_bad_scores[3]],
               [Paragraph(list_bad_reviews[4], ps), list_bad_scores[4]]]
    pos_tab = [['Reviews', 'score'],
               [Paragraph(list_good_reviews[0], ps), list_good_scores[0]],
               [Paragraph(list_good_reviews[1], ps), list_good_scores[1]],
               [Paragraph(list_good_reviews[2], ps), list_good_scores[2]],
               [Paragraph(list_good_reviews[3], ps), list_good_scores[3]],
               [Paragraph(list_good_reviews[4], ps), list_good_scores[4]]]

    negative_table = Table(bad_tab, [1180, 100],
                           rowHeights=(40, 105, 105, 105, 105, 105))
    positive_table = Table(pos_tab, [1180, 100],
                           rowHeights=(40, 105, 105, 105, 105, 105))
    # Set font style
    font = TableStyle([
        ('FONTNAME', (0, 0), (-1, 5), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (1, 1), 15),
        ('FONTSIZE', (0, 1), (1, 1), 21),
        ('FONTSIZE', (0, 2), (1, 2), 21),
        ('FONTSIZE', (0, 3), (1, 3), 21),
        ('FONTSIZE', (0, 4), (1, 4), 21),
        ('FONTSIZE', (0, 5), (1, 5), 21),
        # ('FONTSIZE', (0,1), (-1,-1), 15),
    ])
    negative_table.setStyle(font)
    positive_table.setStyle(font)
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
        ('LEADING', (0, 1), (1, 1), 23),
        ('LEADING', (0, 2), (1, 2), 23),
        ('LEADING', (0, 3), (1, 3), 23),
        ('LEADING', (0, 4), (1, 4), 23),
        ('LEADING', (0, 5), (1, 5), 23),

        ('BACKGROUND', (0, 1), (-1, -1), colors.burlywood),
    ])
    negative_table.setStyle(padding)
    positive_table.setStyle(padding)

    # 3) Alternate backgroud color
    cx = colors.white
    c0 = colors.black
    c1 = colors.HexColor('#9f8159')
    c2 = colors.HexColor('#b59a76')
    c3 = colors.HexColor('#c2aa8a')
    c4 = colors.HexColor('#c9b69d')
    c5 = colors.HexColor('#dcd3c4')

    list_color = [c0, cx, cx, cx, cx, cx]

    row = len(bad_review)
    if row == 0:
        list_color = [c0, cx, cx, cx, cx, cx]
    elif row == 1:
        list_color = [c0, c1, cx, cx, cx, cx]
    elif row == 2:
        list_color = [c0, c1, c2, cx, cx, cx]
    elif row == 3:
        list_color = [c0, c1, c2, c3, cx, cx]
    elif row == 4:
        list_color = [c0, c1, c2, c3, c4, cx]
    elif row == 5:
        list_color = [c0, c1, c2, c3, c4, c5]

    color = TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), list_color[0]),
        ('BACKGROUND', (0, 1), (2, 1), list_color[1]),
        ('BACKGROUND', (0, 2), (2, 2), list_color[2]),
        ('BACKGROUND', (0, 3), (2, 3), list_color[3]),
        ('BACKGROUND', (0, 4), (2, 4), list_color[4]),
        ('BACKGROUND', (0, 5), (2, 5), list_color[5]),
    ]
    )

    row = len(good_review)
    if row == 0:
        list_color = [c0, cx, cx, cx, cx, cx]
    elif row == 1:
        list_color = [c0, c1, cx, cx, cx, cx]
    elif row == 2:
        list_color = [c0, c1, c2, cx, cx, cx]
    elif row == 3:
        list_color = [c0, c1, c2, c3, cx, cx]
    elif row == 4:
        list_color = [c0, c1, c2, c3, c4, cx]
    elif row == 5:
        list_color = [c0, c1, c2, c3, c4, c5]

    color1 = TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), list_color[0]),
        ('BACKGROUND', (0, 1), (2, 1), list_color[1]),
        ('BACKGROUND', (0, 2), (2, 2), list_color[2]),
        ('BACKGROUND', (0, 3), (2, 3), list_color[3]),
        ('BACKGROUND', (0, 4), (2, 4), list_color[4]),
        ('BACKGROUND', (0, 5), (2, 5), list_color[5]),
    ]
    )

    negative_table.setStyle(color)
    positive_table.setStyle(color1)
    return negative_table, positive_table

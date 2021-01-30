import re
import string
import pandas as pd
import numpy as np
import emoji
import regex
from googletrans import Translator
from langdetect import detect
from tqdm.notebook import tnrange
from textblob import TextBlob
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from math import log
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
import textacy
from spacy.util import filter_spans
import spacy
styleSheet = getSampleStyleSheet()

translator = Translator()

# @title get word count score


def get_word_count(DATAFRAME):
    # dataframe = DATAFRAME[['review','rating']]
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
    dataframe = dataframe.sort_values(
        'word_count_score', ascending=False).reset_index(drop=True)
    dataframe['word_count_score'] = dataframe['word_count_score'] / \
        dataframe['word_count_score'][0]
    return dataframe


def get_bad_review(dataframe):
    dataframe = dataframe.reset_index()
    good_review = dataframe[dataframe['rating'] <= 3].sort_values(
        'word_count_score', ascending=False)  # .reset_index()
    good_review = good_review[:25]
    return good_review


def get_good_review(dataframe):
    dataframe = dataframe.reset_index()
    good_review = dataframe[dataframe['rating'] >= 4].sort_values(
        'word_count_score', ascending=False)  # .reset_index()
    good_review = good_review[:25]
    return good_review


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
    NEG_DATAFRAME = DATAFRAME  # detect_lang(DATAFRAME)
    #NEG_DATAFRAME = detect_lang2(NEG_DATAFRAME)
    DATAFRAME = pd.concat([DATAFRAME, NEG_DATAFRAME]).drop_duplicates(
        ['review', 'rating', 'word_count_score'], keep='last').sort_values('word_count_score', ascending=False)
    return DATAFRAME

# @title get sentiment score


def get_sentiment_score(dataframe):
    final_score = []
    nlp = spacy.load('en_core_web_sm')
    for i in range(len(dataframe)):
        about_text = dataframe.review[i]
        about_doc = nlp(about_text)
        sentences = list(about_doc.sents)
        sent_score = 0
        for sentence in sentences:
            sent = TextBlob(str(sentence)).sentiment.polarity
            sent_score += sent

        final_score.append(dataframe.word_count_score[i]*sent_score)

    dataframe['score'] = pd.DataFrame(final_score)
    dataframe = dataframe.sort_values(
        'score', ascending=True).reset_index(drop=True)

    return dataframe

# @title get top bad & good original review


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
    #print("Please wait, currently we're doing second preprocessing for your review data!")
    dataframe = dataframe.copy()
    dataframe['original_review'] = dataframe['original_review'].apply(
        deEmojify)  # removing emoji
    return dataframe


def split_count(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI for char in word):
            emoji_list.append(word)
    return emoji_list


def detect_emoji(dataframe):
    dataframe['counter'] = np.nan
    for i in range(len(dataframe)):
        counter_length = len(split_count(dataframe.original_review[i]))
        if counter_length > 0:
            dataframe['counter'].iloc[i] = len(
                split_count(dataframe.original_review[i]))

    review_emoji = dataframe.loc[dataframe['counter'] > 0]

    for i in range(len(review_emoji)):
        print([i], ">", review_emoji.original_review[i])


def top_bad_review(dataframe, bad_review):
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={'review': 'original_review'})
    #dataframe = get_lowercase(dataframe)
    dataframe = remove_emoji(dataframe)

    #bad_review = bad_review.rename(columns={'score':'worse_score'})
    bad_review = pd.merge(bad_review, dataframe, on=[
                          'index', 'rating', 'word_count_score'], how='inner')
    bad_review = bad_review[['original_review', 'score']]
    bad_review = bad_review.sort_values(
        'score', ascending=True).reset_index(drop=True)
    if len(bad_review) > 0:
        bad_review['score'] = -(bad_review['score']/bad_review['score'][0])
    else:
        pass
    bad_review = bad_review[:5]
    return bad_review


def top_good_review(dataframe, good_review):
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={'review': 'original_review'})
    # dataframe = get_lowercase(dataframe)
    dataframe = remove_emoji(dataframe)

    #good_review = good_review.rename(columns={'score':'score'})
    good_review = pd.merge(good_review, dataframe, on=[
                           'index', 'rating', 'word_count_score'], how='inner')
    good_review = good_review[['original_review', 'score']]
    good_review = good_review.sort_values(
        'score', ascending=False).reset_index(drop=True)
    if len(good_review) > 0:
        good_review['score'] = good_review['score']/good_review['score'][0]
    else:
        pass
    good_review = good_review[:5]
    return good_review


def add_pos_tagger_bad(bad_review):
    color_green1 = '#71e379'
    color_green2 = '#a7ebac'
    color_green3 = '#ccedce'
    color_green4 = '#ddedde'
    color_font_green = '#007008'
    color_red1 = '#ff7878'
    color_red2 = '#ff9696'
    color_red3 = '#ffb5b5'
    color_red4 = '#ffe6e6'
    color_font_red = '#850000'

    nlp = spacy.load('en_core_web_sm')
    verb_pattern = [{"POS": "VERB", "OP": "*"}, {"POS": "ADV", "OP": "*"},
                    {"POS": "VERB", "OP": "+"}, {"POS": "PART", "OP": "*"}]
    new_sentences_list = []
    for i in range(len(bad_review)):
        text_review = bad_review.original_review[i]
        #print("[", bad_review.index[i], "]", text_review)

        word_counts = len(text_review)
        review_words = text_review[:450].split()
        string1 = text_review[:450]

        if word_counts > len(string1):
            string1 += "..."

        text_review_doc = nlp(string1)
        sentences = list(text_review_doc.sents)

        # Get sentiment score per sentence
        score = 0
        new_sentences = ''
        texts_edit = ""

        for sentence in sentences:
            texts_new = ''
            sentiment_score = TextBlob(str(sentence)).sentiment.polarity
            score += sentiment_score
            texts = str(sentence)

            if sentiment_score < 0:
                if sentiment_score < -0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_red1) + texts + "</font> "
                elif -0.6 > sentiment_score >= -0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_red2) + texts + "</font> "
                elif -0.3 > sentiment_score >= -0.6:
                    texts_edit = "<font backcolor={}>".format(
                        color_red3) + texts + "</font> "
                elif 0 > sentiment_score >= -0.3:
                    texts_edit = "<font backcolor={}>".format(
                        color_red4) + texts + "</font> "
            elif sentiment_score > 0:
                if sentiment_score > 0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_green1) + texts + "</font> "
                elif 0.6 < sentiment_score <= 0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_green2) + texts + "</font> "
                elif 0.3 < sentiment_score <= 0.6:
                    texts_edit = "<font backcolor={}>".format(
                        color_green3) + texts + "</font> "
                elif 0 < sentiment_score <= 0.3:
                    texts_edit = "<font backcolor={}>".format(
                        color_green4) + texts + "</font> "
            elif sentiment_score == 0:
                texts_edit = texts

            texts_new += texts_edit
            #print("      (", round(sentiment_score, 2), ")", '==>', sentence)

            # Get noun phrases & it's sentiment score
            doc = nlp(texts)
            split_texts = texts.split()
            char_pos = 0

            for chunk in doc.noun_chunks:
                if chunk.text in texts:
                    sent = TextBlob(chunk.text).sentiment.polarity
                    if sent < 0:
                        #print("             ", "> [Noun Phrases]", chunk, sent)
                        texts_edit = texts_edit.replace(
                            chunk.text, "DETECTED_NP")
                        texts_new = texts_edit.replace(
                            "DETECTED_NP", "<font color={0}><b> {1}</b></font>".format(color_font_red, chunk.text))

            # Get verb phrases & it's sentiment score
            sentence_doc = textacy.make_spacy_doc(
                texts_edit, lang='en_core_web_sm')
            verb_phrases = filter_spans(
                textacy.extract.matches(sentence_doc, verb_pattern))

            for chunk in verb_phrases:
                if chunk.text in texts:
                    sent = TextBlob(chunk.text).sentiment.polarity
                    if sent < 0:
                        #print("             ", "> [Verb Phrases]", chunk.text, sent)
                        texts_edit = texts_edit.replace(
                            chunk.text, "DETECTED_VP")
                        texts_new = texts_new.replace(
                            chunk.text, "DETECTED_VP")
                        texts_new = texts_new.replace(
                            "DETECTED_VP", "<font color={0}><b> {1}</b></font>".format(color_font_red, chunk.text))

            texts_new = texts_new.replace(
                "<font backcolor=", " <font backcolor=")
            texts_new = texts_new.replace(
                "  <font backcolor=", " <font backcolor=")
            # Get undected verb and noun phrases & it's sentiment score
            words = texts_edit.split()

            for word in words:
                sent = TextBlob(word).sentiment.polarity
                if sent < 0:
                    #print("             ", "> [Other]", word, sent)
                    texts_new = texts_new.replace(word, "DETECTED_OTHER")
                    texts_new = texts_new.replace(
                        "DETECTED_OTHER", "<font color={0}><b> {1}</b></font>".format(color_font_red, word))

            texts_new = texts_new.replace(" <font color={}>".format(
                color_font_red), "<font color={}>".format(color_font_red))
            new_sentences += str(texts_new)

        new_sentences_list.append(new_sentences)
        # print(new_sentences)
        #print('Final Sentiment Score:', round(score, 2))
        #print('Final Worse Score:', round(bad_review.score[i], 2), '\n')
    bad_review['original_review'] = pd.DataFrame(new_sentences_list)
    return bad_review


def add_pos_tagger_good(good_review):
    color_green1 = '#71e379'
    color_green2 = '#a7ebac'
    color_green3 = '#ccedce'
    color_green4 = '#ddedde'
    color_font_green = '#007008'
    color_red1 = '#ff7878'
    color_red2 = '#ff9696'
    color_red3 = '#ffb5b5'
    color_red4 = '#ffe6e6'
    color_font_red = '#850000'

    nlp = spacy.load('en_core_web_sm')
    verb_pattern = [{"POS": "VERB", "OP": "*"}, {"POS": "ADV", "OP": "*"},
                    {"POS": "VERB", "OP": "+"}, {"POS": "PART", "OP": "*"}]
    new_sentences_list = []
    for i in range(len(good_review)):
        text_review = good_review.original_review[i]
        #print("[", good_review.index[i], "]", text_review)

        word_counts = len(text_review)
        review_words = text_review[:450].split()
        string1 = text_review[:450]

        if word_counts > len(string1):
            string1 += "..."

        text_review_doc = nlp(string1)
        sentences = list(text_review_doc.sents)

        # Get sentiment score per sentence
        score = 0
        new_sentences = ''
        texts_edit = ""

        for sentence in sentences:
            texts_new = ''
            sentiment_score = TextBlob(str(sentence)).sentiment.polarity
            score += sentiment_score
            texts = str(sentence)

            if sentiment_score > 0:
                if sentiment_score > 0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_green1) + texts + "</font> "
                elif 0.6 < sentiment_score <= 0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_green2) + texts + "</font> "
                elif 0.3 < sentiment_score <= 0.6:
                    texts_edit = "<font backcolor={}>".format(
                        color_green3) + texts + "</font> "
                elif 0 < sentiment_score <= 0.3:
                    texts_edit = "<font backcolor={}>".format(
                        color_green4) + texts + "</font> "
            elif sentiment_score == 0:
                texts_edit = texts
            elif sentiment_score < 0:
                if sentiment_score < -0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_red1) + texts + "</font> "
                elif -0.6 > sentiment_score >= -0.85:
                    texts_edit = "<font backcolor={}>".format(
                        color_red2) + texts + "</font> "
                elif -0.3 > sentiment_score >= -0.6:
                    texts_edit = "<font backcolor={}>".format(
                        color_red3) + texts + "</font> "
                elif 0 > sentiment_score >= -0.3:
                    texts_edit = "<font backcolor={}>".format(
                        color_red4) + texts + "</font> "

            texts_new += texts_edit
            #print("      (", round(sentiment_score, 2), ")", '==>', sentence)

            # Get noun phrases & it's sentiment score
            doc = nlp(texts)
            split_texts = texts.split()
            char_pos = 0

            for chunk in doc.noun_chunks:
                if chunk.text in texts:
                    sent = TextBlob(chunk.text).sentiment.polarity
                    if sent > 0:
                        #print("             ", "> [Noun Phrases]", chunk, sent)
                        texts_edit = texts_edit.replace(
                            chunk.text, "DETECTED_NP")
                        texts_new = texts_edit.replace(
                            "DETECTED_NP", "<font color={0}><b> {1}</b></font>".format(color_font_green, chunk.text))

            # Get verb phrases & it's sentiment score
            sentence_doc = textacy.make_spacy_doc(
                texts_edit, lang='en_core_web_sm')
            verb_phrases = filter_spans(
                textacy.extract.matches(sentence_doc, verb_pattern))

            for chunk in verb_phrases:
                if chunk.text in texts:
                    sent = TextBlob(chunk.text).sentiment.polarity
                    if sent > 0:
                        #print("             ", "> [Verb Phrases]", chunk.text, sent)
                        texts_edit = texts_edit.replace(
                            chunk.text, "DETECTED_VP")
                        texts_new = texts_new.replace(
                            chunk.text, "DETECTED_VP")
                        texts_new = texts_new.replace(
                            "DETECTED_VP", "<font color={0}><b> {1}</b></font>".format(color_font_green, chunk.text))

            texts_new = texts_new.replace(
                "<font backcolor=", " <font backcolor=")
            texts_new = texts_new.replace(
                "  <font backcolor=", " <font backcolor=")
            # Get undected verb and noun phrases & it's sentiment score
            words = texts_edit.split()

            for word in words:
                sent = TextBlob(word).sentiment.polarity
                if sent > 0:
                    #print("             ", "> [Other]", word, sent)
                    texts_new = texts_new.replace(word, "DETECTED_OTHER")
                    texts_new = texts_new.replace(
                        "DETECTED_OTHER", "<font color={0}><b> {1}</b></font>".format(color_font_green, word))

            texts_new = texts_new.replace(" <font color={}>".format(
                color_font_green), "<font color={}>".format(color_font_green))
            new_sentences += str(texts_new)

        new_sentences_list.append(new_sentences)
        # print(new_sentences)
        #print('Final Sentiment Score:', round(score, 2))
        #print('Final Worse Score:', round(good_review.score[i], 2), '\n')

    good_review['original_review'] = pd.DataFrame(new_sentences_list)
    return good_review

# @title combine function


def get_top5_bad_review(DATAFRAME):
    dataframe = get_word_count(DATAFRAME)
    bad_review = get_bad_review(dataframe)
    df_clean = get_clean_review(bad_review)
    bad_review = df_clean[df_clean['rating'] <= 3]
    bad_review = get_translated_language(bad_review)
    bad_review = bad_review.reset_index(drop=True)
    bad_review = get_sentiment_score(bad_review)
    bad_review = top_bad_review(dataframe, bad_review)
    bad_review['score'] = round(bad_review['score'], 2)
    bad_review = bad_review[bad_review['score'] < 0]
    bad_review = add_pos_tagger_bad(bad_review)
    return bad_review


def get_top5_good_review(DATAFRAME):
    dataframe = get_word_count(DATAFRAME)
    good_review = get_good_review(dataframe)
    df_clean = get_clean_review(good_review)
    good_review = get_translated_language(df_clean)
    good_review = good_review.reset_index(drop=True)
    good_review = get_sentiment_score(good_review)
    good_review = top_good_review(dataframe, good_review)
    good_review['score'] = round(good_review['score'], 2)
    good_review = good_review[good_review['score'] > 0]
    good_review = add_pos_tagger_good(good_review)
    return good_review


def good_bad_table(DATAFRAME):
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    ps = ParagraphStyle('title', fontSize=20, leading=22)

    bad_review = get_top5_bad_review(DATAFRAME)
    good_review = get_top5_good_review(DATAFRAME)

    #bad_tab = bad_review.reset_index(drop=True).T.reset_index().T.values.tolist()
    #pos_tab = good_review.reset_index(drop=True).T.reset_index().T.values.tolist()

    list_bad_reviews = ['', '', '', '', '']
    list_bad_scores = ['', '', '', '', '']
    list_good_reviews = ['', '', '', '', '']
    list_good_scores = ['', '', '', '', '']

    for i in range(len(bad_review)):
        list_bad_reviews[i] = bad_review.original_review[i]
        list_bad_scores[i] = bad_review.score[i]

    for i in range(len(good_review)):
        list_good_reviews[i] = good_review.original_review[i]
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

    negative_table = Table(
        bad_tab, [1180, 100], rowHeights=(40, 105, 105, 105, 105, 105))
    positive_table = Table(
        pos_tab, [1180, 100], rowHeights=(40, 105, 105, 105, 105, 105))
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
        #('FONTSIZE', (0,1), (-1,-1), 15),
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

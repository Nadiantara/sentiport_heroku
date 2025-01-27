import pandas as pd
import numpy as np
import re
import regex
from google_play_scraper import app, reviews, reviews_all, Sort
from tqdm import tqdm
from tqdm.notebook import tnrange, tqdm_notebook
from textblob import TextBlob
from googletrans import Translator
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from dateutil.relativedelta import relativedelta
from datetime import datetime


path_title = 'sentiport/utils/Helvetica-Font/Helvetica-Bold.ttf'
path_label = 'sentiport/utils/Helvetica-Font/Helvetica.ttf'
fontprop = fm.FontProperties(fname=path_title, size=15)
fontprop_label = fm.FontProperties(fname=path_label, size=12)


def translate_dataframe(DATAFRAME):
    try:
        translator = Translator()
        return translator.translate(DATAFRAME).text
    except:
        return None


def polarity_calc(text):
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return None


def subjectivity_calc(text):
    try:
        return TextBlob(text).sentiment.subjectivity
    except:
        return None


def preprocessing_weeks(TRANSLATED_DATAFRAME):
    TRANSLATED_DATAFRAME['time'] = pd.to_datetime(TRANSLATED_DATAFRAME['time'])

    week_number = []
    for i in range(len(TRANSLATED_DATAFRAME)):
        week_number.append(TRANSLATED_DATAFRAME['time'][i].week)

    TRANSLATED_DATAFRAME['week_number'] = pd.DataFrame(week_number)

    week_list = []
    for i in TRANSLATED_DATAFRAME['week_number']:
        week_list.append('Week ' + str(i))

    TRANSLATED_DATAFRAME['week_time'] = week_list
    TRANSLATED_DATAFRAME.drop('week_number', axis=1, inplace=True)

    if "Unnamed: 0" in TRANSLATED_DATAFRAME.columns:
        TRANSLATED_DATAFRAME.drop('Unnamed: 0', axis=1, inplace=True)

    if "Unnamed: 0.1" in TRANSLATED_DATAFRAME.columns:
        TRANSLATED_DATAFRAME.drop('Unnamed: 0.1', axis=1, inplace=True)

    return TRANSLATED_DATAFRAME


def get_translated_dataframe(DATAFRAME):
    TRANSLATED_REVIEW = DATAFRAME['review'].apply(translate_dataframe)
    TRANSLATED_REVIEW = pd.DataFrame(TRANSLATED_REVIEW)
    TRANSLATED_REVIEW['version'] = DATAFRAME['version']
    TRANSLATED_REVIEW['rating'] = DATAFRAME['rating']
    TRANSLATED_REVIEW['time'] = DATAFRAME['at']
    return TRANSLATED_REVIEW


def get_sentiment_dataframe(TRANSLATED_DATAFRAME):
    # USE THIS LINE IF YOU WANNA SKIP TRANSLATION
    TRANSLATED_DATAFRAME['version'] = TRANSLATED_DATAFRAME['version']
    TRANSLATED_DATAFRAME['rating'] = TRANSLATED_DATAFRAME['rating']
    TRANSLATED_DATAFRAME['time'] = TRANSLATED_DATAFRAME['at']

    # USE THIS AND SKIP ABOVE IF YOU WANNA USE TRANSLATION
    TRANSLATED_DATAFRAME['polarity'] = TRANSLATED_DATAFRAME['review'].apply(
        polarity_calc)
    TRANSLATED_DATAFRAME['subjectivity'] = TRANSLATED_DATAFRAME['review'].apply(
        subjectivity_calc)

    TRANSLATED_DATAFRAME['sentiment'] = np.nan

    for i in range(len(TRANSLATED_DATAFRAME)):
        if TRANSLATED_DATAFRAME.polarity[i] > 0:
            # TRANSLATED_DATAFRAME['sentiment'].iloc[i] = 'Positive'
            TRANSLATED_DATAFRAME.iloc[i, TRANSLATED_DATAFRAME.columns.get_loc(
                'sentiment')] = 'Positive'
        elif TRANSLATED_DATAFRAME.polarity[i] == 0:
            # TRANSLATED_DATAFRAME['sentiment'].iloc[i] = 'Neutral'
            TRANSLATED_DATAFRAME.iloc[i, TRANSLATED_DATAFRAME.columns.get_loc(
                'sentiment')] = 'Neutral'
        elif TRANSLATED_DATAFRAME.polarity[i] < 0:
            # TRANSLATED_DATAFRAME['sentiment'].iloc[i] = 'Negative'
            TRANSLATED_DATAFRAME.iloc[i, TRANSLATED_DATAFRAME.columns.get_loc(
                'sentiment')] = 'Negative'

    TRANSLATED_DATAFRAME['time'] = pd.to_datetime(TRANSLATED_DATAFRAME['time'])
    TRANSLATED_DATAFRAME['time'] = TRANSLATED_DATAFRAME['time'].dt.strftime(
        '%Y-%m-%d')
    TRANSLATED_DATAFRAME['time'] = pd.to_datetime(TRANSLATED_DATAFRAME['time'])

    # Checking if time is more than 3 months
    check_month = TRANSLATED_DATAFRAME.copy()
    check_month['time'] = check_month['time'].dt.strftime('%b %Y')
    check_month['at'] = pd.to_datetime(check_month['time'])
    months = check_month['time'].nunique()

    if months >= 4:
        return check_month
    else:
        print("Data less than 4  mos")
        TRANSLATED_DATAFRAME = preprocessing_weeks(TRANSLATED_DATAFRAME)
        return TRANSLATED_DATAFRAME


def plot_totalreview_time(data, temp_dir):
    if "week_time" in data.columns:
        review_by_time = pd.DataFrame(data.groupby('week_time').count()['review']).join(
            data.groupby('week_time').mean()['rating'])
        review_by_time = review_by_time.reset_index()
        review_by_time['time'] = review_by_time['week_time']
    else:
        review_by_time = pd.DataFrame(data.groupby('at').count()['review']).join(
            data.groupby('at').mean()['rating'])
        review_by_time = review_by_time.reset_index()
        review_by_time['time'] = pd.to_datetime(review_by_time['at'])
        review_by_time['time'] = review_by_time['time'].dt.strftime("%b %Y")

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "", ["#bba68a", "#957347", "#8b6636"])

    # Plot graph with 2 y axes
    fig, ax1 = plt.subplots(figsize=(11.8726, 4.9648), dpi=100)

    # Plot bars
    ax1.bar(review_by_time['time'], review_by_time['review'], color=cmap(
        review_by_time['review'].values/review_by_time['review'].values.max()))

    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('Total Review', color="#8b6636",
                   fontproperties=fontprop_label)

    # Set up ax2 to be the second y axis with x shared
    ax2 = ax1.twinx()
    # Plot a line
    ax2.plot(review_by_time['time'], review_by_time['rating'],
             marker='o', linestyle='dashed', color="#6d0000")
    # Make the y-axis label and tick labels match the line color.
    ax2.set_ylabel('Average Rating', color="#6d0000",
                   fontproperties=fontprop_label)
    ax2.set_ylim(0, 5)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax1.patch.set_facecolor('white')
    ax2.patch.set_facecolor('white')
    plt.title('Total Review and Average Rating across Months',
              fontproperties=fontprop)
    plt.box(False)
    plt.savefig(f'sentiport/artifacts/{temp_dir}/fig_review_rating_time.png',
                bbox_inches='tight')

    # review_by_time = data.groupby('time').review.nunique()
    # review_by_time = pd.DataFrame(review_by_time)
    # review_by_time = review_by_time.reset_index()

    idmax = review_by_time['review'].idxmax()
    idmin = review_by_time['review'].idxmin()

    max_time = review_by_time['time'][idmax]
    max_value = review_by_time['review'][idmax]
    min_time = review_by_time['time'][idmin]
    min_value = review_by_time['review'][idmin]

    return f'sentiport/artifacts/{temp_dir}/fig_review_rating_time.png', max_time, max_value


def plot_totalreview_version(data, temp_dir):
    review_by_version = pd.DataFrame(data.groupby('version').count(
    )['review']).join(data.groupby('version').mean()['rating'])
    review_by_version = review_by_version.reset_index()

    percent = []

    for i in range(len(review_by_version)):
        persen = review_by_version['review'][i] / \
            sum(review_by_version['review'])
        percent.insert(i, persen)

    review_by_version['percent'] = percent
    value = 0
    panjang_data = []

    for i in reversed(review_by_version.index):
        value = value + review_by_version['percent'][i]
        if value < 0.9:
            panjang_data.append(i)

    review_by_version = review_by_version[-len(panjang_data):]
    review_by_version.reset_index(inplace=True)

    version = review_by_version['version'].nunique()
    if version > 20:
        review_by_version = review_by_version[:20]

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "", ["#aa6a6a", "#791515", "#6d0000"])

    # Plot graph with 2 y axes
    fig, ax1 = plt.subplots(figsize=(11.8726, 4.9648), dpi=100)

    # Plot bars
    ax1.bar(review_by_version['version'], review_by_version['review'], color=cmap(
        review_by_version['review'].values/review_by_version['review'].values.max()))
    ax1.set_xticklabels(review_by_version['version'], rotation=90)

    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('Total Review', color="#6d0000",
                   fontproperties=fontprop_label)

    # Set up ax2 to be the second y axis with x shared
    ax2 = ax1.twinx()
    # Plot a line
    ax2.plot(review_by_version['version'], review_by_version['rating'],
             marker='o', markersize=5, linestyle='dashed', color="#8b6636")
    # Make the y-axis label and tick labels match the line color.
    ax2.set_ylabel('Average Rating', color="#8b6636",
                   fontproperties=fontprop_label)
    ax2.set_ylim(0, 5.2)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax1.patch.set_facecolor('white')
    ax2.patch.set_facecolor('white')

    plt.title('Total Review and Average Rating across Versions',
              fontproperties=fontprop)
    plt.box(False)
    plt.savefig(f'sentiport/artifacts/{temp_dir}/fig_review_rating_version.png',
                bbox_inches='tight')

    # review_by_version = data.groupby('version').review.nunique()
    # review_by_version = pd.DataFrame(review_by_version)
    # review_by_version = review_by_version.reset_index()

    idmax = review_by_version['review'].idxmax()
    idmin = review_by_version['review'].idxmin()

    max_version = review_by_version['version'][idmax]
    max_value = review_by_version['review'][idmax]
    min_version = review_by_version['version'][idmin]
    min_value = review_by_version['review'][idmin]

    return f'sentiport/artifacts/{temp_dir}/fig_review_rating_version.png', max_version, max_value


def plot_totalreview_sentiment(data, temp_dir):
    review_by_sentiment = data['sentiment'].value_counts()
    review_by_sentiment = pd.DataFrame(review_by_sentiment).reset_index()
    review_by_sentiment.rename(
        columns={'index': 'sentiment', 'sentiment': 'total'}, inplace=True)
    review_by_sentiment = review_by_sentiment.sort_values(
        by=['sentiment'], ascending=False)
    sentiment = []
    for i in review_by_sentiment['sentiment']:
        sentiment.append(i)

    total = review_by_sentiment['total'].sum()
    labels = []
    sizes = review_by_sentiment['total']
    colours = {}

    if "Positive" in sentiment:
        pos_index = review_by_sentiment[review_by_sentiment['sentiment']
                                        == 'Positive']['total'].index.values[0]
        pos = review_by_sentiment['total'][pos_index]
        pos_percentage = (pos / total) * 100
        labels.append('Positive {:.2f}%'.format(pos_percentage))
        colours['Positive {:.2f}%'.format(pos_percentage)] = '#1B290D'

    if "Neutral" in sentiment:
        neu_index = review_by_sentiment[review_by_sentiment['sentiment']
                                        == 'Neutral']['total'].index.values[0]
        neu = review_by_sentiment['total'][neu_index]
        neu_percentage = (neu / total) * 100
        labels.append('Neutral {:.2f}%'.format(neu_percentage))
        colours['Neutral {:.2f}%'.format(neu_percentage)] = '#8b6636'

    if "Negative" in sentiment:
        neg_index = review_by_sentiment[review_by_sentiment['sentiment']
                                        == 'Negative']['total'].index.values[0]
        neg = review_by_sentiment['total'][neg_index]
        neg_percentage = (neg / total) * 100
        labels.append('Negative {:.2f}%'.format(neg_percentage))
        colours['Negative {:.2f}%'.format(neg_percentage)] = '#6d0000'

    obj = plt.figure(figsize=(3.95, 3.75), dpi=100)

    patches, texts = plt.pie(
        sizes, colors=[colours[key] for key in labels], startangle=90)
    obj = plt.legend(patches, labels, loc='center left',
                     bbox_to_anchor=(1, 0.5), frameon=False)
    obj = plt.title('Review by Sentiment', fontproperties=fontprop)
    obj = plt.box(False)
    obj = plt.grid(False)
    obj = plt.tick_params(left=False)
    obj = plt.axis('equal')
    obj = plt.tight_layout()
    obj = plt.savefig(
        f'sentiport/artifacts/{temp_dir}/fig_totalreview_sentiment.png', bbox_inches='tight')
    idmax = review_by_sentiment['total'].idxmax()
    max_sentiment = review_by_sentiment['sentiment'][idmax]
    max_value = review_by_sentiment['total'][idmax]

    return f'sentiport/artifacts/{temp_dir}/fig_totalreview_sentiment.png', max_sentiment


def plot_sentiment_time(data, temp_dir):
    if "week_time" in data.columns:
        sentiment_summary = pd.DataFrame(
            data['sentiment'].groupby(data['week_time']).value_counts())  # at
        sentiment_summary.rename(columns={'sentiment': 'total'}, inplace=True)
        sentiment_summary = sentiment_summary.reset_index()

        pivot = pd.pivot_table(
            sentiment_summary, index='week_time', columns='sentiment', values='total')  # at
        pivot = pivot.reset_index()
        pivot = pivot.rename(columns={'sentiment': 'no'})

        pivot['time'] = pivot['week_time']
    else:
        sentiment_summary = pd.DataFrame(
            data['sentiment'].groupby(data['at']).value_counts())  # at
        sentiment_summary.rename(columns={'sentiment': 'total'}, inplace=True)
        sentiment_summary = sentiment_summary.reset_index()

        pivot = pd.pivot_table(sentiment_summary, index='at',
                               columns='sentiment', values='total')  # at
        pivot = pivot.reset_index()
        pivot = pivot.rename(columns={'sentiment': 'no'})
        pivot['time'] = pivot['at'].dt.strftime("%b %Y")  # at

        # sentiment = []
    # for i in pivot['sentiment']:
    #   sentiment.append(i)

    labels = pivot['time']

    x_vals = range(0, len(pivot['time']))
    x = np.arange(len(labels))
    width = 0.35

    obj = plt.figure()
    fig, ax = plt.subplots(figsize=(8.7084, 2.7394), dpi=100)

    if "Negative" in pivot.columns:
        idmax_neg = pivot['Negative'].idxmax()
        idmin_neg = pivot['Negative'].idxmin()

        neg_max_value = pivot['Negative'][idmax_neg]
        neg_min_value = pivot['Negative'][idmin_neg]
        neg_max_time = pivot['time'][idmax_neg]
        neg_min_time = pivot['time'][idmin_neg]
        neg = pivot['Negative']
        obj = ax.bar(x - width, neg, width, label='Negative', color='#6d0000')

    if "Neutral" in pivot.columns:
        idmax_neu = pivot['Neutral'].idxmax()
        idmin_neu = pivot['Neutral'].idxmin()

        nue_max_value = pivot['Neutral'][idmax_neu]
        neu_min_value = pivot['Neutral'][idmin_neu]
        neu_max_time = pivot['time'][idmax_neu]
        neu_min_time = pivot['time'][idmin_neu]
        neu = pivot['Neutral']
        obj = ax.bar(x, neu, width, label='Neutral', color='#8b6636')

    if "Positive" in pivot.columns:
        idmax_pos = pivot['Positive'].idxmax()
        idmin_pos = pivot['Positive'].idxmin()

        pos_max_value = pivot['Positive'][idmax_pos]
        pos_min_value = pivot['Positive'][idmin_pos]
        pos_max_time = pivot['time'][idmax_pos]
        pos_min_time = pivot['time'][idmin_pos]
        pos = pivot['Positive']
        obj = ax.bar(x + width, pos, width, label='Positive', color='#1B290D')

    obj = ax.set_title('Review Sentiment Across Time', fontproperties=fontprop)
    # obj = ax.legend()
    obj = plt.xticks(x_vals, pivot['time'], fontsize=7)
    obj = plt.ylabel("Number of Review", fontproperties=fontprop_label)
    obj = plt.box(False)
    obj = plt.grid(False)
    plt.savefig(
        f'sentiport/artifacts/{temp_dir}/fig_sentiment_time.png', bbox_inches='tight')

    return f'sentiport/artifacts/{temp_dir}/fig_sentiment_time.png'


def plot_sentiment_version(data, temp_dir):
    sentiment_summary = pd.DataFrame(
        data['sentiment'].groupby(data['version']).value_counts())
    sentiment_summary.rename(columns={'sentiment': 'total'}, inplace=True)
    sentiment_summary = sentiment_summary.reset_index()
    percent = []
    for i in range(len(sentiment_summary)):
        persen = sentiment_summary['total'][i]/sum(sentiment_summary['total'])
        percent.insert(i, persen)
    sentiment_summary['percent'] = percent
    value = 0
    panjang_data = []
    for i in reversed(sentiment_summary.index):
        value = value + sentiment_summary['percent'][i]
        if value < 0.9:
            panjang_data.append(i)
    sentiment_summary = sentiment_summary[-len(panjang_data):]
    sentiment_summary.reset_index(inplace=True)

    pivot = pd.pivot_table(sentiment_summary, index='version',
                           columns='sentiment', values='total')
    pivot = pivot.reset_index()
    pivot = pivot.rename(columns={'sentiment': 'no'})

    version = pivot['version'].nunique()
    if version > 20:
        pivot = pivot[:20]

    idmax_pos = pivot['Positive'].idxmax()
    idmin_pos = pivot['Positive'].idxmin()

    pos_max_value = pivot['Positive'][idmax_pos]
    pos_min_value = pivot['Positive'][idmin_pos]
    pos_max_version = pivot['version'][idmax_pos]
    pos_min_version = pivot['version'][idmin_pos]

    idmax_neg = pivot['Negative'].idxmax()
    idmin_neg = pivot['Negative'].idxmin()

    neg_max_value = pivot['Negative'][idmax_neg]
    neg_min_value = pivot['Negative'][idmin_neg]
    neg_max_version = pivot['version'][idmax_neg]
    neg_min_version = pivot['version'][idmin_neg]

    labels = pivot['version']
    neg = pivot['Negative']
    neu = pivot['Neutral']
    pos = pivot['Positive']

    x_vals = range(0, len(pivot['version']))
    x = np.arange(len(labels))
    width = 0.35

    obj = plt.figure()
    fig, ax = plt.subplots(figsize=(8.7084, 2.7394), dpi=100)
    obj = ax.bar(x - width, neg, width, label='Negative', color='#6d0000')
    obj = ax.bar(x, neu, width, label='Neutral', color='#8b6636')
    obj = ax.bar(x + width, pos, width, label='Positive', color='#1B290D')

    obj = ax.set_title('Review Sentiment Across Version',
                       fontproperties=fontprop)
    #obj = ax.legend()
    obj = plt.xticks(x_vals, pivot['version'], rotation=90, fontsize=7)
    obj = plt.ylabel("Number of Review", fontproperties=fontprop_label)
    obj = plt.box(False)
    obj = plt.grid(False)
    plt.savefig(f'sentiport/artifacts/{temp_dir}/fig_sentiment_version.png',
                bbox_inches='tight')

    return f'sentiport/artifacts/{temp_dir}/fig_sentiment_version.png', pos_max_version, neg_max_version


def sentiment_visual_preprocessing(DATAFRAME):

    # TRANSLATING DATAFRAME
    # TRANSLATED_DATAFRAME = get_translated_dataframe(DATAFRAME)

    # USE ONLY THIS LINE IF YOU WANNA SKIP TRANSLATION
    SENTIMENT_DF = get_sentiment_dataframe(DATAFRAME)

    # CALCULATING SENTIMENT ANALYSIS, USE THIS LINE WITH TRANSLATION PROCESS
    # SENTIMENT_DF = get_sentiment_dataframe(TRANSLATED_DATAFRAME)

    return SENTIMENT_DF

# Trial and Error Lines
# DATAFRAME = pd.read_csv('D:\Stuff\Supertype Program\GitHub\data-analyst-github\data_analyst\data-echo-5k.csv')

# one_yr_ago = datetime.now() - relativedelta(years=1)
# DATAFRAME.index = DATAFRAME['at']
# DATAFRAME = DATAFRAME[DATAFRAME.index.map(pd.to_datetime)>one_yr_ago]
# DATAFRAME.reset_index(drop=True, inplace=True)

# DATAFRAME = get_sentiment_dataframe(DATAFRAME)
# # data.to_csv('data-ready-18k.csv')
# print(data.head(10))
# print(data.tail(10))
# print(cek)
# plot_totalreview_time(DATAFRAME)
# plot_totalreview_version(DATAFRAME)
# plot_totalreview_sentiment(DATAFRAME)
# print(b)
# plot_sentiment_time(DATAFRAME)
# plot_sentiment_version(DATAFRAME)

# # PLOTTING DATA
# total_review_by_time(data)
# total_review_by_version(data)
# total_review_by_sentiment(data)
# sentiment_by_time(data)
# sentiment_by_version(data)

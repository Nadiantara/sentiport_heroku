import altair as alt
import cmasher as cmr
import pandas as pd
import numpy as np
import re
from pylab import *
import seaborn as sns
import matplotlib.pyplot as plt
from langdetect import detect
import numpy as np
import matplotlib.colors
import seaborn as sns
import matplotlib.cm
import matplotlib.font_manager as fm
from cycler import cycler


def deEmojify(text):
    '''
    Remove emoji from review data
    '''
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    text = regrex_pattern.sub(r'', text)
    text = text.replace('\n', ' ')
    text = re.sub(' +', ' ', text)

    return text


def get_preprocess_data2(df):
    '''
    Preprocessing 2 : Remove emoji from review data
    '''
    # print("Please wait, currently we're doing second preprocessing for your review data!")
    df = df.copy()
    df['review'] = df['review'].apply(deEmojify)  # removing emoji
    return df


def detect_lang(DATAFRAME):
    '''
    Identify every review data using detect language library
    '''
    # print("Please wait, we're currently detecting the review language!")
    list_lang = []
    row_x = []
    row_xx = []
    min_words_other = 2  # min words filtered

    for i in range(len(DATAFRAME)):
        if len(DATAFRAME.review[i].split()) <= min_words_other:
            row_xx.append(i)
    DATAFRAME = DATAFRAME.drop(row_xx).reset_index(drop=True)

    for i in range(len(DATAFRAME)):
        try:
            x = detect(DATAFRAME['review'][i])
            list_lang.append(x)
        except:
            x = 'no'
            row_x.append(i)
    DATAFRAME = DATAFRAME.drop(row_x).reset_index(drop=True)
    DATAFRAME['lang'] = pd.DataFrame(list_lang)
    return DATAFRAME


def lang_checker(dataframe):
    '''
    Change language outside the country language & mother language (english) 
    '''
    language = 'lang'
    percentage = 'percentage'
    replace_lang = 'ud'
    min_percentage = 10  # in percent(%)
    min_words_other = 2  # min words filtered

    dataframe_grouped = dataframe.groupby(by=[language]).count()
    dataframe_grouped[percentage] = (
        dataframe_grouped.review/dataframe_grouped.review.sum())*100
    top_lang = dataframe_grouped[dataframe_grouped[percentage]
                                 > min_percentage].reset_index()
    top_lang = top_lang[language].tolist()

    other_lang = dataframe[~dataframe[language].isin(
        top_lang)][language].tolist()
    dataframe[language] = dataframe[language].replace(other_lang, replace_lang)

    row_x = []
    for i in range(len(dataframe)):
        if dataframe.lang[i] == replace_lang:
            if len(dataframe.review[i].split()) <= min_words_other:
                row_x.append(i)
    dataframe = dataframe.drop(row_x).reset_index(drop=True)

    return dataframe
############################################################################################################################################################
################################################################PLOT########################################################################################
############################################################################################################################################################


def get_total_language(DATAFRAME):
    '''
    Combine all the language detector into one function 
    '''
    country_list = {"af": "Afrikaans", "ar": "Arabic", "bg": "Bulgarian", "bn": "Bengali", "ca": "Valencian", "cs": "Czech",
                    "cy": "Welsh", "da": "Danish", "de": "German", "el": "Greek", "en": "English", "es": "Spanish",
                    "et": "Estonian", "fa": "Persian", "fi": "Finnish", "fr": "French", "gu": "Gujarati", "he": "Hebrew",
                    "hi": "Hindi", "hr": "Croatian", "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese",
                    "kn": "Kannada", "ko": "Korean", "lt": "Lithuanian", "lv": "Latvian", "mk": "Macedonian", "ml": "Malayalam",
                    "mr": "Marathy", "ne": "Nepali", "nl": "Dutch", "no": "Norwegian", "pa": "Punjabi", "pl": "Polish",
                    "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak", "sl": "Slovenian", "so": "Somali",
                    "sq": "Albanian", "sv": "Swedish", "sw": "Swahili", "ta": "Tamil", "te": "Telugu", "th": "Thai", "tl": "Tagalog",
                    "tr": "Turkish", "uk": "Ukranian", "ur": "Urdu", "vi": "Vietnamese", "zh-cn": "Chinese", "zh-tw": "Taiwan", "ud": "Other"}
    DATAFRAME = get_preprocess_data2(DATAFRAME)
    DATAFRAME1 = detect_lang(DATAFRAME)
    DATAFRAME1 = lang_checker(DATAFRAME1)
    lang = DATAFRAME1.groupby(by="lang").count()
    lang = lang.sort_values(by='review', ascending=False).reset_index()
    list_lang = []
    for i in range(len(lang)):
        list_lang.append(country_list[lang.lang[i]])
    lang['Language'] = pd.DataFrame(list_lang)
    return lang, DATAFRAME1


def plot_total_language(DATAFRAME):
    '''
    Function to get plot total language using altair library
    '''

    lang, DATAFRAME1 = get_total_language(DATAFRAME)
    most_lang = lang['Language'][0]
    short = (lang.Language).tolist()

    plot = alt.Chart(lang).mark_rect().encode(
        alt.X('review:Q'),
        alt.Y('Language:N', sort='-x'),
        alt.Color('Language:N',
                  sort=short, legend=None
                  )
    ).configure_axis(
        grid=False
    )

    return plot, DATAFRAME1


def plot_total_language1(DATAFRAME):
    '''
    Function to get plot total language using matplotlib library
    '''
    lang, DATAFRAME1 = get_total_language(DATAFRAME)
    most_lang = lang['Language'][0]
    max = int(lang['review'].max())
    min = int(lang['review'].min())
    cvals = [min, (min+max)/2, max]
    colors = [(109/255, 0/255, 0/255), (220/255, 211 /
                                        255, 196/255), (0/255, 0/255, 0/255)]

    norm = plt.Normalize(min, max)
    tuples = list(zip(map(norm, cvals), colors))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)
    matplotlib.cm.register_cmap("mycolormap", cmap)
    cpal = sns.color_palette("mycolormap", n_colors=64, desat=0.2)

    plt.rcParams.update({
        "figure.facecolor":  (1.0, 1.0, 1.0, 1.0),  # red   with alpha = 30%
        "axes.facecolor":    (1.0, 1.0, 1.0, 1.0),  # green with alpha = 50%
        "savefig.facecolor": (1.0, 1.0, 1.0, 1.0),  # blue  with alpha = 20%
    })

    obj = plt.figure(figsize=(10, 5))
    #plt.subplot(title='Number of Reviews by Language')

    plt.grid(b=None)
    sub1 = subplot(111)
    ax = sns.barplot(x='review', y='Language', data=lang, palette='mycolormap')

    total = lang['review'].sum()
    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_width()/total)
        number = '{:.0f}'.format(total)
        x = p.get_x() + p.get_width() + 0.02
        y = p.get_y() + p.get_height()/2
        ax.annotate(percentage, (x, y))

    sns.despine(left=True, bottom=True, right=True, top=True)
    grid(False)
    title('Total Review by Language')
    ylabel('')
    xlabel('')

    # I ADDED THIS FOR BORDERLINE
#   autoAxis = sub1.axis()
#   rec = Rectangle((autoAxis[0]-15,autoAxis[2]+0.4),(autoAxis[1]-autoAxis[0])+20,(autoAxis[3]-autoAxis[2])-0.7,fill=False,lw=2)
#   rec = sub1.add_patch(rec)
#   rec.set_clip_on(False)

    obj.savefig('fig_lang_1.png')

    return 'fig_lang_1.png', most_lang, DATAFRAME1


def plot_detect_language2(DATAFRAME, temp_dir):
    '''
    Function to get plot dougnut chart for detect language
    '''
    # get the dataframe & prepare for plot
    lang, DATAFRAME1 = get_total_language(DATAFRAME)
    most_lang = lang['Language'][0]
    # Create new column to get anotate value for plot
    anotate_col = 'anotate'
    percent_format = "{0:.1f}%"
    percent_coeff = 100
    lang[anotate_col] = (lang.review/lang.review.sum())
    lang[anotate_col] = pd.Series([percent_format.format(
        val * percent_coeff) for val in lang[anotate_col]], index=lang.index)
    lang[anotate_col] = lang[anotate_col].str.cat(lang.Language, sep=' ')
    # define value for the label
    anotate = lang.anotate.to_list()
    data = lang.review.to_list()

    # Set parameter for plot
    cmap_type = 'cmr.sepia_r'
    color_format = 'hex'
    rcParams = 'axes.prop_cycle'
    aspect = "equal"
    cmap_n = 5

    cmap_range = (0.15, 0.85)
    width = 0.5
    angle = -40

    # Set color map using cmasher
    colors = cmr.take_cmap_colors(
        cmap_type, cmap_n, cmap_range=cmap_range, return_fmt=color_format)
    plt.rcParams[rcParams] = cycler(color=colors)

    # install font for plot
    path = 'sentiport/utils/Helvetica-Font/Helvetica-Bold.ttf'
    path1 = 'sentiport/utils/Helvetica-Font/Helvetica-Oblique.ttf'
    Helvetica_Bold = fm.FontProperties(fname=path, size=18)
    Helvetica = fm.FontProperties(fname=path1, size=15)

    # Create the plot function to generate dougnut chart
    obj, ax = plt.subplots(figsize=(9.03307, 4.7017),
                           dpi=100, subplot_kw=dict(aspect=aspect))
    wedges, texts = ax.pie(data, wedgeprops=dict(
        width=width), startangle=angle)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(anotate[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw, fontproperties=Helvetica)

    sumstr = 'From\n'+str(lang.review.sum())+'\nReviews'
    ax.text(0., 0., sumstr, horizontalalignment='center',
            verticalalignment='center', fontproperties=Helvetica_Bold)

    fig_path = f'sentiport/artifacts/{temp_dir}/fig_lang.png'
    obj.savefig(fig_path)

    return fig_path, most_lang, DATAFRAME1

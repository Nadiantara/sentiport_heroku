# prepare the environment
import pandas as pd
from google_play_scraper import app, reviews
from tqdm import tqdm
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup


def get_crawl_google(id, country_id):

    BATCH_SIZE = 50
    MAX_REVIEWS = 2000
    appinfo = app(
        id,
        lang='en',
        country=country_id)

    AVAIL_REVIEWS = appinfo.get('reviews')
    TOFETCH_REVIEWS = min(AVAIL_REVIEWS, MAX_REVIEWS)
    ints = list(range(max(TOFETCH_REVIEWS//BATCH_SIZE, 1)))
    result = []
    continuation_token = ""
    t = tqdm(total=TOFETCH_REVIEWS)
    for i in ints:
        if i == 0:
            result, continuation_token = reviews(id,
                                                 count=BATCH_SIZE,
                                                 country=country_id
                                                 )
        res, continuation_token = reviews(
            id, count=BATCH_SIZE, continuation_token=continuation_token)
        result.extend(res)
        t.update(BATCH_SIZE)
    t.close()

    dfp = pd.DataFrame(result)
    dfp.drop_duplicates('reviewId', inplace=True)

    data = [dfp['reviewId'], dfp['content'],
            dfp['reviewCreatedVersion'], dfp['score'], dfp['at']]
    headers = ['reviewId', 'review', 'version', 'rating', 'at']
    df_google = pd.concat(data, axis=1, keys=headers)
    df_google['version'].fillna("null", inplace=True)
    for idx in range(len(df_google)-1):
        if df_google['version'][idx] == 'null':
            df_google.loc[idx, 'version'] = df_google['version'][idx+1]

    for i in range(len(df_google)):
        if "." in df_google['version'][i][1]:
            pass
        elif "." in df_google['version'][i][2]:
            pass
        else:
            df_google.drop(index=i, inplace=True)

    df_google.reset_index(drop=True, inplace=True)
    df_google['at'] = pd.to_datetime(df_google['at'])
    return df_google


def app_title(id, country_id):
    appinfo = app(
        id,
        lang='en',
        country=country_id
    )
    return appinfo['title']


def value_overall_rating(playstore_id):
    target_url = 'https://play.google.com/store/apps/details?id='+playstore_id
    uClient = uReq(target_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    overall_rating = page_soup.findAll("div", {"class": "BHMmbe"})

    return overall_rating[0].text


def value_total_review(playstore_id):
    target_url = 'https://play.google.com/store/apps/details?id='+playstore_id
    uClient = uReq(target_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    total_review = page_soup.findAll("span", {"class": "EymY4b"})

    return total_review[0].findAll("span", {"class": ""})[0].text


def image_company_logo(playstore_id, temp_dir):
    target_url = 'https://play.google.com/store/apps/details?id='+playstore_id
    uClient = uReq(target_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    total_review = page_soup.findAll("div", {"class": "xSyT2c"})
    link_gambar = total_review[0].find(
        "img", {"class": "T75of sHb2Xb"}).get('src')
    gambar = uReq(link_gambar)
    output = open(f"sentiport/artifacts/{temp_dir}/logo_company.png", "wb")
    output.write(gambar.read())
    output.close()
    return f"sentiport/artifacts/{temp_dir}/logo_company.png"

# import data_collector
import pickle
import warnings

# from data_collector import is_available, context_scraper
from parsivar import Normalizer
from sklearn.feature_extraction.text import CountVectorizer
from bs4.element import Comment
import bs4
# import requests
import time
import urllib.request
from urllib.request import Request, urlopen


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# extracts text from html
def text_from_html(body):
    soup = bs4.BeautifulSoup(body, 'html.parser')
    texts = soup.find_all(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


# scrapes context of a website
def context_scraper(url: str):
    for i in range(10):
        delay = 5
        try:
            html = urllib.request.urlopen(url).read()
            text = text_from_html(html)
            if text == '':
                text = 'not scraped'
            break
        except Exception:
            time.sleep(delay)
            delay *= 2
            if i == 9:
                text = 'not scraped'

    return text


# checks if a url is still available
def is_available(url: bool):
    req = Request(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
    try:
        urlopen(req, timeout=10).read()
    except Exception:
        return False
    else:
        return True


# Getting url
url = input("Enter a URL:\n")


while True:

    warnings.filterwarnings("ignore")

    available = is_available(url)

    if available:
        context = context_scraper(url)

        if context == 'not scraped':
            print("This URL Can not Be Scraped!")
            break
        normalizer = Normalizer()
        normed_context = normalizer.normalize(context)

        with open('model/model.pkl', 'rb') as f:
            count_vectorized, model = pickle.load(f)

        context_count = count_vectorized.transform([normed_context])
        prediction = model.predict(context_count)

        if prediction == 1:
            pred_str = 'spam'
        else:
            pred_str = 'ham'
        print("This Website is:\n", pred_str)
        break
    else:
        print("This URL is not Available!")
        break


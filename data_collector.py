import bs4
import requests
import unicodedata
from bs4.element import Comment, SoupStrainer
import urllib.request
import pandas as pd
import time
from urllib.request import Request, urlopen
from tqdm import tqdm
from parsivar import Normalizer
import re


# scrapes urls from a website in order to collect more data
def url_scraper(url: list):
    # fetch all the HTML source from the url
    response = requests.get(url)

    # parse HTML and extract links
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a')

    urls = []
    for link in links:
        if link.get('href') is not None and 'https://' in link.get('href'):
            urls.append(link.get('href'))

    return urls


# # collects websites with .ir domain
# def ir_collector(urls: list):
#     ir_urls = []
#     for url in urls:
#         url = url.replace('\n', '')
#         if '.ir/' in url:
#             ir_urls.append(url)
#
#     return ir_urls


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


data_df = pd.DataFrame()

'''
Spam
'''
spam_df = pd.read_csv('data/spam_urls.csv')

# storing available urls in a list
available_urls = []
print('\navailable spam urls:')
for url in tqdm(spam_df['url']):
    if is_available(url):
        available_urls.append([url, 'spam'])

'''
Ham
# '''
# websites to crawl links from
websites = [
            'https://www.farsnews.ir/',
            'https://www.isna.ir/service/Science-Academia',
            'https://laptopdid.ir/articles',
            'https://utype.ir/docs/',
            'https://www.khabaronline.ir/service/Politics',
            'https://www.digikala.com/mag/',
            'https://www.digikala.com/mag/culture-art/',
            'https://www.digikala.com/mag/literature/',
            'https://www.digikala.com/mag/game/',
            'https://manag.ir/journal/movie/',
            'https://manag.ir/journal/analytic/',
            'https://manag.ir/journal/music/',
            'https://www.offdecor.com/decorplus',
            'https://www.offdecor.com/cook-HJZ174'
            ]

# collecting urls
links = []
for url in websites:
    links.extend(url_scraper(url))

# storing only .ir urls in a list
# ir_links = ir_collector(links)

# checking if urls are available
print('\navailable ham urls:')
for url in tqdm(links):
    if is_available(url) and [url, 'ham'] not in available_urls:
        available_urls.append([url, 'ham'])

'''
Dataset
'''
# scraping urls with BeautifulSoup and normalizing their context
data = []
normalizer = Normalizer()
print('\nscraping all available urls:')
for row in tqdm(available_urls):
    url = row[0]
    context = context_scraper(url)

    if context == 'not scraped':
        continue
    normed_context = normalizer.normalize(context)

    row.insert(1, normed_context)
    data.append(row)

# saving all data in a csv file
data_df = pd.DataFrame(data, columns=['url', 'context', 'category'])
data_df.to_csv('data/data1.csv')

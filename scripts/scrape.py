### Author: Ashlynn Wimer
### Date: 4/3/2024
### About: This Python script uses requests to scrape every Daily Maroon 
###        article's text from the UChicago Library's website.
###        This script *also* provided me an excuse to multithread,
###        since otherwise this takes FOREVER to run (although fwiw,
###        it still takes pretty heckin long).

import requests
from bs4 import BeautifulSoup 
import pandas as pd
from pandas import DataFrame
from concurrent.futures import ThreadPoolExecutor
import threading
import re

BASE_URL = 'https://campub.lib.uchicago.edu'    
START_URL = BASE_URL + '/search/?f1-title=Daily+Maroon&startDoc=1'

def get_all_pages(soup: BeautifulSoup) -> list:
    '''
    Make a list of every URL of pages of Daily Maroon articles in the 
    archive.
    '''
    # Chaotic approach: get all links, subset down
    links = soup.find_all('a')    
    rel_links = set()
    for link in links:
        if 'startDoc' in link.get('href') and 'search' in link.get('href'):
            rel_links.add(link.get('href'))

    return list(rel_links)

def get_all_mag_links(soup: BeautifulSoup) -> DataFrame:
    '''
    Given a soup for a specific Daily Maroon archive webpage, find
    all links to Daily Maroon articles on the webpage.
    '''
    links = soup.find_all('a')
    dates, hrefs = [], []

    for link in links:
        if 'view' in link.get('href') and link.text.strip() != '':        
            dates.append(link.text)
            hrefs.append(BASE_URL + link.get('href'))
    
    df = DataFrame({'date':dates, 'url':hrefs})
    return df

def save_text_multiple(dates, urls) -> None:
    '''
    Given lists of dates and urls of equal size, save the text contents of those
    articles to a transcripts file.
    '''
    for date, url in zip(dates, urls):
        save_text(date, url)

def save_text(date, url) -> None:
    '''
    Given the url of a Daily Maroon article, return the
    text content of that article.
    '''
    text_url = re.sub('view', 'text', url)
    r = requests.get(text_url)
    soup = BeautifulSoup(r.text)
    with open(f'../data/transcripts/{date}.txt', 'w', encoding=r.encoding) as f:
        f.write(soup.text) 

    return 

def multi_thread_save_all(df):
    '''
    Do the actual scraping of text with ~multithreading~
    '''
    with ThreadPoolExecutor(max_workers=7) as executor:
        executor.map(save_text, df['date'].values, df['url'].values)

if __name__ == '__main__':

    # Get initial page and get soup
    r = requests.get(START_URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    print('Getting all pages!')

    # Get all pages to scrape
    pages = get_all_pages(soup)
    pages = [BASE_URL + url for url in pages] + [START_URL]

    print('Got all pages!')
    print('Starting to find URLs for all copies of the Daily Maroon -- this may take a second.')

    # Scrape text from all pages
    df = DataFrame({'date':[], 'url':[]})
    for page in pages[:2]:
        r = requests.get(page)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get every mag link. Yipee!
        df = pd.concat([df, get_all_mag_links(soup)], ignore_index=True)
    
    print('Got the URLs for every copy of the Daily Maroon! Starting to scrape using 5 threads..')

    # Save all text
    multi_thread_save_all(df)
import argparse
from os import link

import datetime
import pandas as pd
from requests.models import HTTPError
from common import config
import logging
logging.basicConfig(level=logging.INFO)
import news_page_objects as news

from yaml import parser
import re

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError


is_well_formed_link=re.compile(r'^https?://.+/.+$')
is_root_path=re.compile(r'^/.+$')



def _news_scraper(new_site_uid):
    host=config()['news_sites'][new_site_uid]['url']
    logging.info('Beginning scraper for {}'.format(host))
    homepage= news.HomePage(new_site_uid,host)
    
    articles=[]
    a_title=[]
    a_body=[]
    a_links=[]
    for link in homepage.article_links:
        article=_fetch_article(new_site_uid,host,link)

        if article:
            logging.info('Article Fetched..!! :D')
            articles.append(article)
            a_links.append(link)
            a_title.append(article.title)
            a_body.append(article.body)

        _save_articles(new_site_uid, a_links, a_title,a_body)

def _save_articles(new_site_uid, a_links, a_title,a_body):
    now=datetime.datetime.now().strftime('%Y_%m_%d')
    df=pd.DataFrame()
    df['title']=a_title
    df['body']=a_body
    df['link']=a_links
    file_name='{}_{}_articles.csv'.format(new_site_uid,now)
    df.to_csv(file_name,index=False)



def _fetch_article(new_site_uid,host,link):
    logging.info('start fetching article at {}'.format(link))

    article=None
    try:
        article=news.ArticlePage(new_site_uid,_build_link(host,link))
    except (HTTPError,MaxRetryError) as e:
        logging.warning('Error while fetching the article',exc_info=False) 
    

    if article and not article.body:
        logging.warning('Invalid article. There is nobody')
        return None
    return article

def _build_link(host,link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host,link)
  

if __name__== '__main__':
    parser = argparse.ArgumentParser()

    news_sites_choices=list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                        help= 'The news sites that you want to scrape',
                        type=str,
                        choices=news_sites_choices)
    
    args=parser.parse_args()
    _news_scraper(args.news_site)


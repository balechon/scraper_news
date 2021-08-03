import requests
import lxml.html as html

from common import config

class NewsPage:
    def __init__(self,new_site_uid,url):
        self._config=config()['news_sites'][new_site_uid]
        self._queries=self._config['queries']
        self._html=None
        self._visit(url)
    
    def _select(self, query_string):
        return self._html.xpath(query_string)
        
    def _visit(self,url):
        response=requests.get(url)
        home=response.content.decode('utf-8')
        self._html=html.fromstring(home)

class HomePage(NewsPage):
    def __init__(self,new_site_uid,url):
        super().__init__(new_site_uid,url)

    @property
    def article_links(self):
        link_list= self._select(self._queries['homepage_article_links'])
        return set(link for link in link_list)

class ArticlePage(NewsPage):
    def __init__(self, new_site_uid,url):
        super().__init__(new_site_uid,url)

    @property
    def body(self):
        result=self._select(self._queries['article_body'])
        return result
    @property
    def title(self):
        result=self._select(self._queries['article_title'])
        return result
         
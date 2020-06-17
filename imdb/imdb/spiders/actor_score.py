# -*- coding: utf-8 -*-
import scrapy
import re

from imdb.pipelines import ImdbPipeline
from imdb.items import ActorItem 

imdbpipeline = ImdbPipeline()

def get_full_url(actor_id):
    base_url = "https://www.imdb.com/title/{}/"
    return base_url.format(actor_id)

def prepare_movie_urls():
    """
        准备movie url
    """
    search_result = imdbpipeline.get_actor_id(type_id=3) 
    base_url = "https://www.imdb.com/name/{}/"
    urls = []
    for result in search_result:
        title = result[0]
        url = base_url.format(title)
        urls.append(url)
    return urls

class ActorScoreSpider(scrapy.Spider):
    name = 'actor_score'
    allowed_domains = ['imdb.com']
    base_url = 'https://www.imdb.com' 
    start_urls = prepare_movie_urls()
    base_title = '/title/{}/'
    def parse(self, response):
        # ---------------------------------------------------------------------------------
        # 获取演员作品集
        try:
            productions = []
            titles = re.findall(r'id="actor-(.*?)"', response.text)
            for title in titles:
                production = self.base_title.format(title)
                productions.append(production)
        except Exception as e:
            print('productions_set Error, ',e)
            productions = []

        # ---------------------------------------------------------------------------------
        # 获取演员名字
        try:
            actor_name = response.xpath('//span[@class="itemprop"]/text()').extract()[0]
        except Exception as e:
            print('actior_name Error, ', e)
            actor_name = ''

        # ---------------------------------------------------------------------------------
        
        if len(productions) == 0:
            pass
        else:
            actor_item = ActorItem()
            actor_item['id'] = self.extract_actor_id_from_url(response.url)[:-1]
            actor_item['actor_name'] = actor_name

            for production in productions:
                production_url = self.base_url+production
                score = imdbpipeline.get_movie_item(actor_item['id'])
                if score != -1:
                    # 首先尝试在movie数据库中寻找，如果不存在，在请求该网页。
                    actor_item['movie_score'] = score
                    actor_item['movie_num'] = movie_num
                    actor_item['actor_score'] = 0
                    yield actor_item
                else:
                    yield scrapy.Request(production_url,
                        callback=self.get_movie_score,
                        meta={'actor_item':actor_item})
    
    def get_movie_score(self, response):
        actor_item = response.meta['actor_item']
        
        # ---------------------------------------------------------------------------------
        # 获取电影评分
        try:
            movie_score = response.xpath(r'//span[@itemprop="ratingValue"]/text()').extract()[0]
            movie_num = 1
        except Exception as e:
            print('movie score Error, ', e)
            movie_score = '0'
            movie_num = 0
        
        actor_item['movie_score'] = str(movie_score)
        actor_item['movie_num'] = movie_num
        actor_item['actor_score'] = '0'
        yield actor_item

    def extract_actor_id_from_url(self, actor_url):
        if actor_url is None:
            return None
        return re.search(r'(nm[0-9]{7}.*?)/', actor_url).group(0)

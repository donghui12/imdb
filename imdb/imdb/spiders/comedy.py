# -*- coding: utf-8 -*-
import scrapy
import time
import re

from imdb.items import MovieItem

class ImdbMovieUrlsProvider:
    def __init__(self):
        pass

    @staticmethod
    def prepare_movie_urls():
        """
            prepare the movie urls from url
        """
        base_url='https://www.imdb.com/search/title/?title_type=movie&genres=comedy&start={}&explore=title_type,genres&ref_=adv_nxt'
        urls = []
        for index in range(500):
            start = index*50+1
            url = base_url.format(start)
            urls.append(url)
        return urls

    @staticmethod
    def prepare_movie_genros_title():
        base_url ='https://www.imdb.com/search/title/?title_type=movie&genres=comedy&after={}%3D%3D&explore=title_type,genres&ref_=adv_nxt'
        urls = []
        start_title = ['WzU0MjE0LCJ0dDg5ODI0MzYiLDExMDUwXQ',
                'WzU0NTc0LCJ0dDAwNjMxODYiLDExMTAwXQ',
                'WzU0ODc4LCJ0dDAwNzk3MzgiLDExMTUwXQ',
                'WzU1MTM1LCJ0dDAwNDY2OTUiLDExMjAwXQ',
                'WzU1NDE0LCJ0dDY1NTA4MDgiLDExMjUwXQ',
                'WzU1NjkyLCJ0dDUxNTQ0NjYiLDExMzAwXQ',
                'WzU1OTM1LCJ0dDAyMDQ5MzIiLDExMzUwXQ',
                'WzU2MTU5LCJ0dDQ2ODY2OTIiLDExNDAwXQ',
                'WzU2NDUwLCJ0dDM3MjUwMjYiLDExNDUwXQ',
                'WzU2Nzc1LCJ0dDAwNTI1NjAiLDExNTAwXQ',
                'WzU3MDY0LCJ0dDgyMjIzNDIiLDExNTUwXQ',
                'WzU3MzE3LCJ0dDAwMzk2OTgiLDExNjAwXQ',
                'WzU3NTgxLCJ0dDA5ODYzMjkiLDExNjUwXQ',
                'WzU3ODUzLCJ0dDAwOTYxNzYiLDExNzAwXQ',
                'WzU4MTI4LCJ0dDAwMzQ4NTAiLDExNzUwXQ',
                'WzU4NTI3LCJ0dDE0MTg3NTciLDExODAwXQ',
                'WzU4ODE3LCJ0dDA0MjE1MjgiLDExODUwXQ',
                'WzU5MTIwLCJ0dDAwNjMwMzQiLDExOTAwXQ',
                'WzU5MzUzLCJ0dDk4ODA5ODIiLDExOTUwXQ',
                'WzU5NjM1LCJ0dDIyOTU3NTAiLDEyMDAwXQ',]
        for title in start_title:
            url = base_url.format(title)
            urls.append(url)
        return urls


class ComedySpider(scrapy.Spider):
    name = 'comedy'
    allowed_domains = ['imdb.com']
    base_url = 'https://www.imdb.com'
    start_urls = ImdbMovieUrlsProvider().prepare_movie_genros_title()
    years = [str(year) for year in range(2000,2020)]

    def parse(self, response):
        try:
            movies_urls = response.xpath('//h3[@class="lister-item-header"]/a/@href').extract()
        except Exception as e:
            print('Error {}, in {}'.format(e, response.url))
            movies_urls = []

        for movies_url in movies_urls: 
            full_movies_url = self.base_url + movies_url
            yield scrapy.Request(url=full_movies_url, callback=self.parse_movie_info)

    def parse_movie_info(self, response):
        """
            获取电影详细信息
        """
        print('*'*100)
        item = MovieItem()
        item['id'] = self.extract_movie_id_from_url(response.url)
        item['url'] = response.url
        item['genres'] = 'Comedy'
         
        # -----------------------------------------------------------------------------
        # 获取电影名字
        try:
            movie_name = response.xpath('//div[@class="title_wrapper"]/h1/text()').extract()[0]
            name = movie_name.translate(dict.fromkeys((ord(c) for c in u'\xa0\n\t')))
        except Exception as e:
            print('movie name Error, ', e)
            name = 'Error'
        item['name'] = name

        # -----------------------------------------------------------------------------
        # 获取电影评分
        try:
            score = response.xpath("//span[@itemprop='ratingValue']/text()").extract()[0]
            score = float(score)
        except Exception as e:
            print('score Error, ', e)
            score = -1
        item['score'] = score

        # -----------------------------------------------------------------------------
        # 获取上映时间
        try:
            release_date = response.xpath('//*[@id="titleYear"]/a/text()').extract()[0]
        except Exception as e:
            print('release_date Error, ', e)
            release_date = 'error date'
        item['release_date'] = release_date
        
        # -----------------------------------------------------------------------------
        # 获取票房收入
        try:
            gross = response.xpath('//h4[contains(text(),"Gross:")]/following-sibling::node()/descendant-or-self::text()').extract()[0]
            gross = gross.strip()
        except Exception as e:
            print('gross Error, ', e)
            gross = -1
        item['gross'] = gross

        # -----------------------------------------------------------------------------
        # 获取电影时长
        try:
            # 由于可能出现两个时间变量，所以需要对此进行少选
            # 一个是 1h 30min, 另一个是90min;
            runtimes = response.xpath(r'//time/text()').extract()
            if len(runtimes) == 2:
                minutes_str = re.sub(' ', '', runtimes[-1])
                minutes = re.search('(.*?)min', minutes_str).group(1)
                duration = int(minutes)
            else:
                hours_minutes = re.sub(' ', "", runtimes[0])
                hours, minutes = re.search(r'(.*?)h(.*?)min', hours_minutes)
                duration = int(hour)*60 + int(minutes)
        except Exception as e:
            print('duration Error, ', e)
            duration = -1
        item['runtime'] = duration

        # -----------------------------------------------------------------------------
        # 获取电影屏幕比例
        try:
            aspect_ratio_str = response.xpath('//h4[contains(text(), "Aspect Ratio:")]/following-sibling::node()/descendant-or-self::text()').extract()[0]
            aspect_ratio_str = aspect_ratio_str.strip()
            aspect_ratio = aspect_ratio_str.translate(dict.fromkeys((ord(c) for c in u'\xa0\n\t')))
            aspect_ratio = re.sub(r' ','', aspect_ratio)
        except Exception as e:
            print('aspect ratio Error, ', e)
            aspect_ratio = '-1'
        item['aspect_ratio'] = aspect_ratio

        # -----------------------------------------------------------------------------
        # 获取导演id
        try:

            director_link = response.xpath('//div[@class="plot_summary_wrapper"]/div[1]/div[2]/a/@href').extract()[0]
            director_id = self.extract_person_id_from_url(director_link)
        except Exception as e:
            print('director Error, ', e)
            director_id = self.random_id()
        item['director_id'] = director_id
                                                    

        # -----------------------------------------------------------------------------
        # 获取演员id
        actor_id, actor = [], []
        actor = {}
        try:
            actor_links = response.xpath(r'//div[@class="plot_summary_wrapper"]/div[1]/div[4]/a/@href').extract()
            actor_1_id = self.extract_person_id_from_url(actor_links[0])
            actor_2_id = self.extract_person_id_from_url(actor_links[1])
            actor_3_id = self.extract_person_id_from_url(actor_links[2])
        except Exception as e:
            actor_1_id = self.random_id()
            actor_2_id = self.random_id()
            actor_3_id = self.random_id()
            print('actors Error', e)
        item['actor_1_id'] = actor_1_id
        item['actor_2_id'] = actor_2_id
        item['actor_3_id'] = actor_3_id

        if item['release_date'] in self.years:
            yield item
                
    def extract_movie_id_from_url(self, link):
        if link is None:
            return None
        return re.search(r'(tt[0-9].*?)/', link).group(1)

    def extract_person_id_from_url(self, link):
        if link is None:
            return None
        return re.search(r'(nm[0-9]{7}.*?)/', link).group(1)

    def random_id(self):
        now_time = time.time()
        random_id = 'er' + str(now_time)[-7:]

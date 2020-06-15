# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    score = scrapy.Field()

class MovieItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    genres = scrapy.Field()
    score = scrapy.Field()
    gross = scrapy.Field()
    aspect_ratio = scrapy.Field()
    release_date = scrapy.Field()
    runtime = scrapy.Field()
    director_id = scrapy.Field()
    actor_1_id = scrapy.Field()
    actor_2_id = scrapy.Field()
    actor_3_id = scrapy.Field()

class DirectorItem(scrapy.Item):
    """
        由于流程原因，现在调整结构，
    """
    id = scrapy.Field()
    director_name = scrapy.Field()
    director_score = scrapy.Field()
    movie_score = scrapy.Field()
    movie_num = scrapy.Field()

class ActorItem(scrapy.Item):
    id = scrapy.Field()
    actor_name = scrapy.Field()
    actor_score = scrapy.Field()
    movie_score = scrapy.Field()
    movie_num = scrapy.Field()

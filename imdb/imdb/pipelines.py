# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from imdb.items import ActorItem
from imdb.items import DirectorItem

class ImdbPipeline:
    def __init__(self):
        self.connect = pymysql.connect( host='localhost',
                                        user='user',
                                        passwd='password',
                                        db='movies')
        self.cursor = self.connect.cursor()
        self.type_id_db = {3:'actor', 1:'movie', 2:'director'}

    def get_movie_item(self, item_id):
        """
            查询item数据
        """
        search_sql = 'select score from movie where id=%s limit 1'
        count = self.cursor.execute(search_sql, [item_id, ])
        if count == 0:
            return -1
        score = self.cursor.fetchall()[0][0]

        return score

    def update_actor_score(self, item, type_id):
        """
            更新演员数据，名字和得分
        """
        director_update_sql = 'update director set actor_name=%s,actor_score=%s, movie_num=%s, actor_total_score=%s where id=%s'
        actor_update_sql = 'update actor set actor_name=%s,actor_score=%s,movie_num=%s, actor_total_score=%s where id=%s'
        if type_id == 2:
            update_sql = director_update_sql
            result = self.cursor.execute(update_sql, [item['director_name'],
                item['director_score'], item['movie_num'],
                item['movie_score'],item['id']])
        else:
            update_sql = actor_update_sql
            result = self.cursor.execute(update_sql, [item['actor_name'],
                item['actor_score'], item['movie_num'], item['movie_score'],
                item['id'],])
        self.connect.commit()


    def get_actor_id(self, type_id):
        """
            获取actor_name为空的actor_id
        """
        actor_search_sql = 'select actor_1_id from movie union select actor_2_id from movie union select actor_3_id from movie'
        director_search_sql = 'select director_id from movie'
        if type_id == 2:
            search_url = actor_search_sql
        else:
            search_url = director_search_sql
        self.cursor.execute(search_url)
        result = self.cursor.fetchall()
        return result

    def process_item(self, item, spider):
        """
            首先对spider的名字进行判断
            进而不同处理结果
        """
        if spider.name == 'thriller' or spider.name=='comedy':
            self.process_movie_item(item)
        else:
            self.process_actor_score_item(item, spider)
    
    def get_actor_item(self, item_id, type_id):
        actor_search_sql = 'select * from actor where id=%s limit 1'
        director_search_sql = 'select * from director where id=%s limit 1'
        if type_id == 2:
            search_sql = actor_search_sql 
        else:
            search_sql = director_search_sql
        count = self.cursor.execute(search_sql, [item_id,])
        items = self.cursor.fetchall()
        if count == 0:
            item = []
        else:
            item = items[0]
        print('*'*30, item)
        return item

    def process_actor_score_item(self, item, spider):
        """
            更新actor或director数据
        """
        if spider.name == 'actor_score':
            type_id = 3
            search_item = self.get_actor_item(item['id'], type_id)
            print(search_item)
            if search_item ==[]:
                eld_item = ActorItem()
                eld_item['id'] = ''
                eld_item['movie_num'] = 0
                eld_item['movie_score'] = ''
            else:
                eld_item = ActorItem()
                eld_item['id'] = search_item[0] 
                eld_item['actor_name'] = search_item[1]
                if not search_item[3] is None:
                    eld_item['movie_score'] = search_item[3]+', '+item['movie_score']
                    total_movie_score = self.get_total_movie_score(eld_item['movie_score'])
                    eld_item['movie_num'] = search_item[-1]+1
                    eld_item['actor_score'] = total_movie_score/eld_item['movie_num']
                else:
                    eld_item['movie_score'] = item['movie_score']
                    total_movie_score = self.get_total_movie_score(eld_item['movie_score'])
                    eld_item['movie_num'] = 1
                    eld_item['actor_score'] = total_movie_score/eld_item['movie_num']
        
 
        else:
            type_id = 2
            search_item = self.get_actor_item(item['id'], type_id)
            print(search_item)
            if search_item ==[]:
                eld_item = DirectorItem()
                eld_item['id'] = ''
                eld_item['movie_num'] = 0
                eld_item['movie_score'] = ''
            else:
                search_item
                eld_item = DirectorItem()
                eld_item['id'] = search_item[0] 
                eld_item['director_name'] = search_item[1]
                if not search_item[3] is None:
                    eld_item['movie_score'] = search_item[3]+', '+item['movie_score']
                    total_movie_score = self.get_total_movie_score(eld_item['movie_score'])
                    eld_item['movie_num'] = search_item[-1]+1
                    eld_item['director_score'] = total_movie_score/eld_item['movie_num']
                else:
                    eld_item['movie_score'] = item['movie_score']
                    total_movie_score = self.get_total_movie_score(eld_item['movie_score'])
                    eld_item['movie_num'] = 1
                    eld_item['director_score'] = total_movie_score/eld_item['movie_num']
        
        self.update_actor_score(eld_item, type_id)
        

    def process_movie_item(self, item):
        """
            插入movie_item, 由于外键原因需要先插入director, actor_1, actor_2,
            actor_3。
        """
        
        movie_insert_sql = "insert into movie(id, url, name, score, aspect_ratio,release_date, runtime, director_id, actor_1_id, actor_2_id, actor_3_id, gross) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


        director_insert_sql = "insert into director(id, actor_name) values (%s,%s)"
        
        actor_1_insert_sql = "insert into actor(id, actor_name) values (%s, %s)"
        actor_2_insert_sql = "insert into actor(id, actor_name) values (%s, %s)"
        actor_3_insert_sql = "insert into actor(id, actor_name) values (%s, %s)"
        
        self.cursor.execute(director_insert_sql, [item['director_id'], ''])
        self.cursor.execute(actor_1_insert_sql, [item['actor_1_id'], ''])
        self.cursor.execute(actor_2_insert_sql, [item['actor_2_id'], ''])
        self.cursor.execute(actor_3_insert_sql, [item['actor_3_id'], ''])
        self.cursor.execute(movie_insert_sql, (item['id'], item['url'],
                                            item['name'], item['score'],
                                            item['aspect_ratio'], item['release_date'],
                                            item['runtime'], item['director_id'],
                                            item['actor_1_id'], item['actor_2_id'],
                                            item['actor_3_id'], item['gross']))
        self.connect.commit()
        

 
    def get_total_movie_score(self, movie_score):
        total_score = 0.0
        print('='*50, movie_score)
        if type(movie_score) == int:
            return movie_score
        for score in movie_score.split(','):
            if len(score) == 0:
                movie_score = 0
            else:
                movie_score = float(score)
            total_score += movie_score
        return total_score

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

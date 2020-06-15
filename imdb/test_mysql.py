# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class ImdbPipeline:
    def __init__(self):
        self.connect = pymysql.connect( host='localhost',
                                        user='imdbspider',
                                        passwd='imdb%spider&&Q1W2E3',
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
        director_update_sql = 'update director set actor_name=%s, actor_score=%s'
        actor_update_sql = 'update actor set actor_name=%s, actor_score=%s where id=%s'
        if type_id == 2:
            update_sql = director_update_sql
        else:
            update_sql = actor_update_sql
        result = self.cursor.execute(update_sql, [item['actor_name'], item['actor_score'], item['id']])
        self.connect.commit()

    def get_actor_id(self, type_id):
        """
            获取actor_name为空的actor_id
        """
        actor_search_sql = 'select id from actor where actor_name=""'
        director_search_sql = 'select id from director where actor_name=""'
        if type_id == 2:
            search_url = actor_search_sql
        else:
            search_url = director_search_sql
        self.cursor.execute(search_url)
        result = self.cursor.fetchall()
        return result

    def process_movie_item(self, item,  spider):
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
        

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

if __name__=='__main__':
    piple = ImdbPipeline()
    # movie_id = piple.get_movie_item('tt5503686')
    movie_item = {'actor_1_id': 'nm2011390',
            'actor_2_id': 'nm0002341',
            'actor_3_id': 'nm0023425',
            'aspect_ratio': '2 : 1',
            'director_id': 'nm1076521',
            'genres': 'Thriller',
            'gross': '$157,563',
            'id': 'tt5503352',
            'name': 'Heros',
            'release_date': '2019',
            'runtime': 100,
            'score': 5.2,
            'url': 'https://www.imdb.com/title/tt5503352/'}
    actor_item = {"id":'nm0023425','actor_name':'jdh','actor_score':10}
    # piple.process_movie_item(movie_item, '1')
    """
    result = piple.get_actor_id(type_id=3)
    print(result)
    """
    piple.update_actor_score(actor_item, 3)

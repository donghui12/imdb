# imdb
### Scrapy爬虫

#### 数据结构分析
需要的数据有：电影名字，电影评分，电影时长，电影票房，电影类型，上映时间，
电影屏宽比，导演信息，演员1信息，演员2信息，演员3信息
根据以上数据，决定使用mysql数据库进行数据存储。一开始使用json进行存储，但是json文件
需要同时获取以上全部信息。使用mysql则可以先抓取电影信息，记录导演和演员的id，随后进行
演员和导演的信息采集。

------------

#### mysql数据建立
对网站分析根据得知，每个电影都有自己的title且该title不重复，所以决定使用title作为主键。
每个导演和演员也有相应的id作为主键，而movie存储导演和演员的id即可。movie表如下。
![](/media/editor/e3ecd9231e5a6fe7a0e6cb690132ce1_20200616114955783504.png)
演员和导演分别存储，其包含的数据一样，分别如下。
![](/media/editor/562db8caa3cb644c508ad3c2c7e76df_20200616115116534359.png)
![](/media/editor/ea781e5ca6d90fb75fb4b094077673e_20200616115130192654.png)
actor_total_score是每个电影的评分，是一个长字符串。主要是存储方便。
movie_num是有效电影数量。
actor_score是actor_total_score/movie_num.

------------

#### items.py
结构如下：
![](/media/editor/09f86b8b2d2fd5084b840005cc1a06f_20200616115703813621.png)

#### piplines.py
    ImdbPipline
    ├── __init__(self) # 连接数据库
    ├── process_item(self, item, spider) # 核心组件，scrapy进入该文件会直接进入该方法，在该方法里需要对spider的类型进行判断，不同spider处理方式不同
    ├── process_movie_item(self, item_id)  # 对电影数据进行处理
    ├── update_actor_score(self, item, type_id)  # 更新演员和导演的数据，type_id是分辨演员还是导演
    ├── get_actor_id(self, type_id)  # 获取演员或导演的全部数据，主要应用在start_urls
    ├── get_movie_item(self, item_id)  # 查询movie_item的id，主要是在获取演员或者导演的作品查询是否存在已有作品。
    ├── get_total_movie_score(self, movie_score) # 获取作品电影评分总和。
    └── close_spiders(self, spider)  # 关闭连接
	在本文件中对电影和演员的处理不同。
	电影：获取电影之后，由于依赖director和actor的外键，所以首先需要对director，actor
		插入id,仅仅插入id，然后插入电影数据。
	演员或导演：获取到item后，首先查询该item的movie_num是否为0，若为0，则说明该actor或director尚未处理，
		则提交item，若不为0，则说明已经处理过，需要添加数据，将该item与search_item进行处理之后提交更新。
		说明：由于在电影阶段这些导演或演员的id已经提交，所以后续操作皆属于更新操作。

#### spide/movie_score.py
    对movie数据的正常获取，不同电影可能xpath不同，需要多次验证获取。

#### spide/director_score.py
    对director数据的正常获取，不同演员可能xpath不同，需要多次验证获取。

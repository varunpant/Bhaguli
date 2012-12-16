import web
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker
from datetime import datetime

engine = create_engine(web.config.dbpath, echo=False)#log
DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata
metadata.bind = engine
Session = sessionmaker(bind=engine)


taggings = Table(u'taggings', metadata,
    Column(u'post_id', INTEGER(), ForeignKey('posts.id'), primary_key=True, nullable=False),
    Column(u'tag_id', INTEGER(), ForeignKey('tags.id'), primary_key=True, nullable=False),
) 


class Archives(DeclarativeBase):
    __tablename__ = 'archives'

    __table_args__ = {}
    
        
    def __init__(self, month, year, posts_count):
        self.month = month
        self.year = year
        self.posts_count = posts_count
        
    def __repr__(self):
        return "<Archives('year: %s','month: %s', 'count: %s')>" % (self.year, self.month, self.posts_count)
    
    #column definitions
    month = Column(u'month', INTEGER(), primary_key=True, nullable=False)
    posts_count = Column(u'posts_count', INTEGER(), nullable=False)
    year = Column(u'year', INTEGER(), primary_key=True, nullable=False)

class Page(DeclarativeBase):
    __tablename__ = 'pages'

    __table_args__ = {}
    
    def __init__(self, title, slug, content, published_at):
        self.title = title
        self.slug = slug
        self.content = content
        self.published_at = published_at
        self.created_at = datetime.now()

    #column definitions
    content = Column(u'content', TEXT(), nullable=False)
    created_at = Column(u'created_at', TIMESTAMP(), nullable=False)
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    published_at = Column(u'published_at', TIMESTAMP())
    slug = Column(u'slug', VARCHAR(length=256), nullable=False)
    title = Column(u'title', VARCHAR(length=256), nullable=False)

class Post(DeclarativeBase):
    __tablename__ = 'posts'

    __table_args__ = {}
    
    def __init__(self, title, slug, content, published_at, excerpt, tags):
        self.title = title
        self.slug = slug
        self.content = content
        self.published_at = published_at
        self.created_at = datetime.now()
        self.excerpt = excerpt
        self.tags = tags
     
    def __repr__(self):
        return "<Post %s, %s, %s, %s, %s, %s>" % (self.title,self.slug,self.content,self.published_at,self.excerpt,self.tags)
    
    #column definitions
    content = Column(u'content', TEXT(), nullable=False)
    created_at = Column(u'created_at', TIMESTAMP(), nullable=False)
    excerpt = Column(u'excerpt', VARCHAR(length=512))
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    published_at = Column(u'published_at', TIMESTAMP())
    slug = Column(u'slug', VARCHAR(length=256), nullable=False)
    title = Column(u'title', VARCHAR(length=256), nullable=False)

    #relation definitions
    tags = relation('Tag', primaryjoin='Post.id==taggings.c.post_id', secondary=taggings, secondaryjoin='taggings.c.tag_id==Tag.id', lazy='joined')

class Setting(DeclarativeBase):
    __tablename__ = 'settings'

    __table_args__ = {}

    #column definitions
    bing_app_id = Column(u'bing_app_id', VARCHAR(length=64))
    blog_title = Column(u'blog_title', VARCHAR(length=256), nullable=False)
    cache_duration_in_seconds = Column(u'cache_duration_in_seconds', INTEGER())
    disqus_short_name = Column(u'disqus_short_name', VARCHAR(length=256))
    disqus_url = Column(u'disqus_url', VARCHAR(length=1028))
    feed_burner_url = Column(u'feed_burner_url', VARCHAR(length=1024))
    google_analytics_code = Column(u'google_analytics_code', VARCHAR(length=24))
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    items_per_page = Column(u'items_per_page', INTEGER(), nullable=False)
    login = Column(u'login', VARCHAR(length=128), nullable=False)
    meta_description = Column(u'meta_description', VARCHAR(length=512))
    meta_keywords = Column(u'meta_keywords', VARCHAR(length=512))
    password = Column(u'password', VARCHAR(length=128), nullable=False)
    posts_in_home = Column(u'posts_in_home', INTEGER(), nullable=False)
    root = Column(u'root', VARCHAR(length=1028), nullable=False)
    tag_line = Column(u'tag_line', VARCHAR(length=256))
    user_bio = Column(u'user_bio', VARCHAR(length=2048))
    user_email = Column(u'user_email', VARCHAR(length=256))
    user_full_name = Column(u'user_full_name', VARCHAR(length=256), nullable=False)
    user_short_name = Column(u'user_short_name', VARCHAR(length=256))

class Tag(DeclarativeBase):
    __tablename__ = 'tags'

    __table_args__ = {}
   
    def __init__(self, title, slug, posts_count):
        self.title = title
        self.slug = slug
        self.posts_count = posts_count
    
    def __repr__(self):
        return "<Tag %s, %s, %s, %s>" % (self.id,self.title,self.slug,self.posts_count)
     
        
    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    posts_count = Column(u'posts_count', INTEGER(), nullable=False)
    slug = Column(u'slug', VARCHAR(length=256), nullable=False)
    title = Column(u'title', VARCHAR(length=256), nullable=False)

    #relation definitions
    posts = relation('Post', primaryjoin='Tag.id==taggings.c.tag_id', secondary=taggings, secondaryjoin='taggings.c.post_id==Post.id')


def getSession():
    return  Session()

def createSchema():
    if web.config.dbpath == "sqlite://":
        session = Session()
        session.configure(bind=engine)
        metadata.create_all(engine)
        
def dropSchema():
    if web.config.dbpath == "sqlite://":
        metadata.drop_all(engine)
        

def executeRaw(sql):
    if web.config.dbpath == "sqlite://":
        session = Session()
        connection = session.connection()
        resp = connection.execute(sql)
        session.commit()
        return resp
        


    
    

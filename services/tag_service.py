###############################################################################
# TAGS Querying Service #######################################################
###############################################################################
from models import *

def get_by_title(title):
        session = getSession()
        return session.query(Tag).filter_by(title=title).scalar()

def get_by_slug(slug):
        session = getSession()
        return session.query(Tag).filter_by(slug=slug).scalar() 

def get_all():
        session = getSession()
        return session.query(Tag).order_by(Tag.title.desc()).all()

def get_published():
        session = getSession()
        return session.query(Tag).filter(Tag.posts.any(Post.published_at != None)).order_by(Tag.posts_count.desc()).all()
    
def get_unpublished():
        session = getSession()
        return session.query(Tag).filter(Tag.posts.any(Post.published_at == None)).order_by(Tag.title.desc()).all()	

def count_all():
        session = getSession()
        return session.query(Tag).count()

def count_published():
        session = getSession()
        return session.query(Tag).filter(Tag.posts.any(Post.published_at != None)).count()
    
def count_unpublished():
        session = getSession()
        return session.query(Tag).filter(Tag.posts.any(Post.published_at == None)).count()

def get_popular(limit):
        session = getSession()
        return session.query(Tag).filter(Tag.posts.any(Post.published_at != None)).order_by(Tag.posts_count.desc()).limit(limit).offset(0).all()
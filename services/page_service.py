###############################################################################
# PAGE Querying Service #######################################################
###############################################################################

from models import *
import shared_helper
isNotNull = shared_helper.IsNotNull


def get_by_id(pageId):
	session = getSession()
	return session.query(Page).get(pageId) 

def get_published_by_slug(slug):
	session = getSession()
	return session.query(Page).filter_by(slug=slug).scalar()
	
def get_all(offset, limit):
	session = getSession()
	return session.query(Page).order_by(Page.published_at.desc()).limit(limit).offset(offset).all()

def get_all_published():
	session = getSession()
	return session.query(Page).filter(Page.published_at != None).order_by(Page.published_at.desc()).all()
	
def get_published(offset, limit):
	session = getSession()
	return session.query(Page).filter(Page.published_at != None).order_by(Page.published_at.desc()).limit(limit).offset(offset).all()

def get_unpublished(offset, limit):
	session = getSession()
	return session.query(Page).filter(Page.published_at == None).order_by(Page.published_at.desc()).limit(limit).offset(offset).all()	
	
def count_all():
	session = getSession()
	return session.query(Page).count()

def count_published():
	session = getSession()
	return session.query(Page).filter(Page.published_at != None).count()

def count_unpublished():
	session = getSession()
	return session.query(Page).filter(Page.published_at == None).count()

###############################################################################
# PAGE Publishing Service #####################################################
###############################################################################

def create(title, slug, content, published_at):
	page = Page(title, slug, content, published_at)
	page.slug = shared_helper.to_url(page.slug) if isNotNull(page.slug) else shared_helper.to_url(page.title)
	session = getSession()
	__commit(session,page)
	
	return page

def update(pageId, title, slug, content, published_at):
	session = getSession()
	page  = session.query(Page).get(pageId) 
	page.title = title
	page.slug = slug
	page.content = content
	page.published_at = published_at
	page.slug = shared_helper.to_url(page.slug) if isNotNull(page.slug) else shared_helper.to_url(page.title)
	__commit(session,page)
	
	return page

def destroy(pageId):
	session = getSession()
	page  = session.query(Page).get(pageId) 
	__destroy(session,page)



def __commit(session,o):
	try:		
		session.add(o)
		session.commit()		
		return True
	except:
		return False

def __destroy(session,o):
	try:		
		session.delete(o)
		session.commit()		
		return True
	except:
		return False

###############################################################################
# Post Querying Service #######################################################
###############################################################################
from models import *
import calendar,shared_helper,re
from datetime import datetime, date
exper = re.compile("(.{240}.*?<\/p>)",re.IGNORECASE|re.MULTILINE|re.DOTALL)
#exper = re.compile("<p>\s*(.+?)\s*</p>",re.IGNORECASE)
isNotNull = shared_helper.IsNotNull

def get_by_id(postId):
	session = getSession()
	return session.query(Post).get(postId)

def get_published_by_slug(slug):
	session = getSession()
	return session.query(Post).filter_by(slug=slug).scalar()

def get_all(offset, limit):
	session = getSession()
	return session.query(Post).order_by(Post.published_at.desc()).limit(limit).offset(offset).all()

def get_all_published():
	session = getSession()
	return session.query(Post).filter(Post.published_at != None).order_by(Post.published_at.desc()).all()

def get_published(offset, limit):
	session = getSession()
	return session.query(Post).filter(Post.published_at != None).order_by(Post.published_at.desc()).limit(limit).offset(offset).all()

def get_unpublished(offset, limit):
	session = getSession()
	return session.query(Post).filter(Post.published_at == None).order_by(Post.published_at.desc()).limit(limit).offset(offset).all()

def find_recent(limit):
	session = getSession()
	return session.query(Post).filter(Post.published_at != None).order_by(Post.published_at.desc()).limit(limit).offset(0).all()

def find_published_by_tag(slug, offset, limit):
	session = getSession()
	return  session.query(Post).filter(Post.published_at != None).order_by(Post.published_at.desc()).filter(Post.tags.any(Tag.slug == slug)).limit(limit).offset(offset).all()

def find_published_by_date_range(start_date, end_date):
	session = getSession()
	return  session.query(Post).filter(Post.published_at.between(start_date, end_date)).order_by(Post.published_at.desc()).all()

def find_published_by_year(year, offset, limit):	 
	session = getSession()
	return  session.query(Post).filter(Post.published_at.between(str(year) + "-01-1 00:00:00", str(year) + "-12-31 00:00:00")).order_by(Post.published_at.desc()).limit(limit).all()

def find_published_by_year_and_month(year, month, offset, limit):	
	session = getSession()
	startDate = date(year, month, 1)	
	endDate = date(year, month, calendar.monthrange(year, month)[1])
	return  session.query(Post).filter(Post.published_at.between(startDate, endDate)).order_by(Post.published_at.desc()).limit(limit).offset(offset).all()

def find_published_by_year_month_and_day(year, month, day, offset, limit):
	session = getSession()
	startDate = datetime(year, month, day, 0, 0, 0)
	endDate = datetime(year, month, day, 23, 59, 59)			
	return  session.query(Post).filter(Post.published_at.between(startDate, endDate)).order_by(Post.published_at.desc()).limit(limit).offset(offset).all()

def count_all():
	session = getSession()
	return session.query(Post).count()

def count_published():
	session = getSession()
	return session.query(Post).filter(Post.published_at != None).count()
	
def count_unpublished():
	session = getSession()
	return session.query(Post).filter(Post.published_at == None).count()

def count_published_by_tag(slug):
	session = getSession()
	return  session.query(Post).filter(Post.published_at != None).filter(Post.tags.any(Tag.slug == slug)).count()

def get_archives():	
	session = getSession()
	return session.query(Archives).filter(Archives.posts_count > 0).order_by(Archives.year.desc(),Archives.month.desc()).all()


###############################################################################
# Post Publishing Service #####################################################
###############################################################################

def create(title, slug, content, published_at, excerpt, tags):	 
	session = getSession()
	post = Post(title, slug, content, published_at, excerpt,[])
	post.slug = shared_helper.to_url(post.slug) if isNotNull(post.slug) else shared_helper.to_url(post.title)
	if not isNotNull(post.excerpt):
		m = exper.search(content)
		post.excerpt = m.group(0) if m else "" 
		
	if tags is not None and len(tags)>0 :
		tags = unique_tags(tags)
		add_tags(session,post, tags)
		
	if __commit(session,post) and published_at is not None :
		increment_archive(session,published_at) 
	
	return post

def update(postId, title, slug, content, published_at, excerpt, tags):
	session = getSession()
	post = session.query(Post).get(postId)
	if post:
		old_published_at = post.published_at
		post.title = title
		post.slug = slug
		post.content = content
		post.published_at = published_at
		post.excerpt = excerpt		
		post.slug = shared_helper.to_url(post.slug) if isNotNull(post.slug) else shared_helper.to_url(post.title)
		if tags is not None and len(tags)>0 :
			tags = unique_tags(tags)
			tags_to_remove = filter(lambda t: t.title.lower() not in tags,post.tags)
			tags_to_add = filter(lambda t: not any(filter(lambda pt:pt.title.lower() == t,post.tags)),tags)
			remove_tags(session,post, tags_to_remove)
			add_tags(session,post, tags_to_add)
		else:
			remove_tags(post, post.tags)
		
		if __commit(session,post) and (published_at == old_published_at):
			if old_published_at is not None:
				decrement_archive(session,old_published_at)
			if published_at is not None:
				increment_archive(session,published_at)			
			
		return post
	else:
		return None

def destroy(postId):
	session = getSession()
	post = session.query(Post).get(postId)
	published_at = post.published_at
	if post.tags is not None and len(post.tags) > 0:
		remove_tags(session,post, post.tags)	 

	if __destroy(session,post) and published_at is not None:
		decrement_archive(session,published_at)
	


def increment_archive(session,published_at):	
	archive = session.query(Archives).filter(Archives.year == published_at.year).filter(Archives.month == published_at.month).scalar()
	if not archive:
		archive = Archives(published_at.month,published_at.year,1)
	else:
		archive.posts_count +=1			
	__commit(session,archive)
	
def decrement_archive(session,published_at):
	archive = session.query(Archives).filter(Archives.year == published_at.year).filter(Archives.month == published_at.month).scalar()
	if not archive:
		archive = Archives(published_at.month,published_at.year,1)
	else:
		archive.posts_count -=1
	__commit(session,archive)

def add_tags(session,post, tags):
	for tag in tags:
		
		_tag = session.query(Tag).filter_by(title=tag).scalar()
		if not _tag:
			_tag = Tag(tag,shared_helper.to_url(tag),1)
		else:
			_tag.posts_count +=1
		post.tags.append(_tag)

def remove_tags(session,post,tags):	
	for tag in tags:
		tag.posts_count -=1
		__commit(session,tag)
		link = taggings.delete(taggings.c.tag_id == tag.id and taggings.c.post_id == post.id)
		link.execute()		 
		for t in post.tags:			
			if (t.id == tag.id):				
				post.tags.remove(t)							
		__commit(session,post)

def unique_tags(tags):
	noDupes = [] 
	[noDupes.append(i.strip().lower()) for i in tags if not noDupes.count(i.strip().lower())]
	return filter(None,noDupes)



def __commit(session,o):
	try:		
		session.add(o)
		session.commit()		
		return True
	except  Exception,e:
		raise
		return False

def __destroy(session,o):
	try:		
		session.delete(o)
		session.commit()		
		return True
	except  Exception,e:
		raise
		return False
	

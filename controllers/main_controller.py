import  web, calendar
from services import shared_helper, post_service, tag_service, page_service, search_service, blog_cache, settings_service

###############################################################################
# General Housekeeping ########################################################
############################################################################### 

blog_settings = settings_service.Settings().get_settings()
start_index = shared_helper.start_index
safe_number = shared_helper.safe_number
total_page = shared_helper.total_page

global_settings = {'settings': blog_settings, 'blog_cache':blog_cache.Cache() }
render = web.template.render('views/themes/light', base='base', globals=global_settings)

def notfound(msg):	 
	raise web.notfound(render.notfound(msg))

def internalerror():
	return web.internalerror(render.notfound("Bad, bad server. No donut for you."))

###############################################################################
# Routes Handlers #############################################################
############################################################################### 


class Index:
	def GET(self):
		p = safe_number(web.input(page="1").page) 
		limit = blog_settings.items_per_page
		offset = start_index(p, limit)
		pageCount = total_page(post_service.count_published(), limit) 
		posts = post_service.get_published(offset, limit)
		nextLink = "?page=" + str(p + 1) if p < pageCount else None
		previousLink = "?page=" + str(p - 1) if p > 1 else None 

		return render.index(posts, nextLink, previousLink)
	
class PostSlug:
	def GET(self, slug):
		post = post_service.get_published_by_slug(slug)
		if post and post.published_at:
			return render.post(post)
		else:
			return notfound("The requested resource was not found on this server.")

class PageSlug:
	def GET(self, slug):
		page = page_service.get_published_by_slug(slug)
		if page and page.published_at:
			return render.page(page)
		else:
			return notfound("The requested resource was not found on this server.")
		
class Topic:
	def GET(self, slug, page):
		page = safe_number(page)
		if page < 1:
			return notfound("The requested resource was not found on this server.Pages start from 1")
		tag = tag_service.get_by_slug(slug)
		if tag:
			count = post_service.count_published_by_tag(tag.slug)
			if count < 1:
				return notfound("No post with this tag was found!")
			offset = start_index(page, blog_settings.items_per_page)
			posts = post_service.find_published_by_tag(tag.slug, offset, blog_settings.items_per_page)
			title = "Topic: " + tag.title + "(" + str(count) + ")"
			page_count = total_page(count, blog_settings.items_per_page)
			nextLink = previousLink = None
			if page < page_count:
				nextLink = "/topics/" + slug + "/" + str(page + 1) 
			if page > 1 :
				previousLink = "/topics/" + slug + "/" + str(page - 1) 
			return render.index(posts, nextLink, previousLink) 
		else:
			return notfound("The requested tag: " + slug + " was not found.")

class Archives:
	def GET(self):
		posts = post_service.get_all_published()
		_archives = post_service.get_archives()
		archives = []
		tags = tag_service.get_published()
		for archive in _archives:
			archives.append({'full_month':calendar.month_name[archive.month], 'month':archive.month, 'year':archive.year, 'posts_count':archive.posts_count})
		return render.archive(posts, tags, archives)

class ArchivePage:
	def GET(self, page):
		page = safe_number(page)
		if page < 1:
			return notfound("The requested resource was not found on this server.Pages start from 1")
		
		limit = blog_settings.items_per_page
		offset = start_index(page, limit)
		posts = post_service.get_published(offset, limit)
		page_count = total_page(len(posts), limit)
		nextLink = previousLink = None
		if page < page_count:
			nextLink = "/archives/" + str(page + 1) 
		if page > 1 :
			previousLink = "/archives/" + str(page - 1) 
		
		return render.index(posts, nextLink, previousLink) 

class ArchivePageYear:
	def GET(self, page, year):
		page = safe_number(page)
		if page < 1:
			return notfound("The requested resource was not found on this server.Pages start from 1")
		year = safe_number(year)
		if year <= 1990:
			return notfound("The requested resources for year: ' " + str(year) + " ' were not found")
		limit = blog_settings.items_per_page	
		offset = start_index(page, limit)			 
		posts = post_service.find_published_by_year(year, offset, limit)
		page_count = total_page(len(posts), limit)
		nextLink = previousLink = None
		if page < page_count:
			nextLink = "/archives/" + str(page + 1) + "/" + year
		if page > 1 :
			previousLink = "/archives/" + str(page - 1) + "/" + year 
		return render.index(posts, nextLink, previousLink)
	
class ArchivePageYearMonth:
	def GET(self, page, year, month):
		page = safe_number(page)
		if page < 1:
			return notfound("Incorrect ' Page ', they start from 1")
		safe_year = safe_number(year)
		if safe_year <= 1990:
			return notfound("Incorrect year: ' " + str(year) + " '")
		safe_month = safe_number(month)
		if safe_month < 1 or safe_month > 12:
			return notfound("Incorrect month ' " + str(safe_month) + " '")		 
		
		limit = blog_settings.items_per_page	
		offset = start_index(page, limit)			 
		posts = post_service.find_published_by_year_and_month(safe_year, safe_month, offset, limit)
		page_count = total_page(len(posts), limit)
		
		nextLink = previousLink = None
		if page < page_count:
			nextLink = "/archives/" + str(page + 1)  + "/" + year  + "/" + month
		if page > 1 :
			previousLink = "/archives/" + str(page - 1)  + "/" + year + "/" + month
		return render.index(posts, nextLink, previousLink)

class ArchivePageYearMonthDay:
	def GET(self, page, year, month, day):
		page = safe_number(page)
		if page < 1:
			return notfound("Incorrect ' Page ', they start from 1")
		safe_year = safe_number(year)
		if safe_year <= 1990:
			return notfound("Incorrect year: ' " + str(year) + " '")
		safe_month = safe_number(month)
		if safe_month < 1 or safe_month > 12:
			return notfound("The requested resources for the month: ' " + str(safe_month) + " '")		
		safe_day = safe_number(day)
		if safe_day < 1 or safe_day > calendar.monthrange(int(year), int(month))[1]:
			return notfound("Incorrect day: ' " + str(day) + " '")		 
		
		limit = blog_settings.items_per_page	
		offset = start_index(page, limit) 
		posts = post_service.find_published_by_year_month_and_day(safe_year, safe_month, safe_day, offset, limit)
		page_count = total_page(len(posts), limit)
		nextLink = previousLink = None
		if page < page_count:
			nextLink = "/archives/" + str(page + 1) + "/" + year  + "/" + month + "/" + day
		if page > 1 :
			previousLink = "/archives/" + str(page - 1) + "/" + year  + "/" + month + "/" + day
		return render.index(posts, nextLink, previousLink)
		
class Contact:
	def GET(self):
		return render.contact(None, None)
	
	def POST(self):
		msg = ""
		user_data = web.input()
		sender = user_data.name.strip() 
		email = user_data.email.strip() 
		subject = user_data.subject.strip() 
		body = user_data.message.strip() 
		if not shared_helper.IsNotNull(sender):
			msg = "name, "
		if not shared_helper.IsNotNull(email) or not shared_helper.validateEmail(email):
			msg += "email, "
		if not shared_helper.IsNotNull(subject):
			msg += "subject, "
		if not shared_helper.IsNotNull(body):
			msg += "and message  "
		if msg == "":
			sender = sender + "  <" + email + ">"
			recipient = u'<' + blog_settings.user_email + '>' 
			try:
				shared_helper.send_email(sender, recipient, subject, body)
				msg = "Thank you for contacting me.I will get back to you as soon as I can" 
			except Exception as e:
				return internalerror("Error while sending mail." + str(e))
		else:
			if msg == "and message  ":
				msg = "message  "            
			msg = "There was an error in sending your message! Please enter a valid  " + msg[0:-2]
		return render.contact(None, msg)

class Search:
	def GET(self):	 
		q = web.input().q
		page = safe_number(web.input(page="1").page) 
		offset = start_index(page, blog_settings.items_per_page) 
		limit = blog_settings.items_per_page			
		count = safe_number(search_service.getCount(q)[0])
		result = []
		msg = None
		nextLink = previousLink = None		
		if count > 0:
			result = search_service.search(q, offset, limit)
			page_count = total_page(count, limit)	 
			if page < page_count:
				nextLink = "/search?q=%s&page=%s" % (q, str(page + 1)) 
			if page > 1 :
				previousLink = "/search?q=%s&page=%s" % (q, str(page - 1)) 
		else:
			msg = "No results were found for query \" " + q + " \""
		
		
		return render.search(q, count, result, nextLink, previousLink, msg)

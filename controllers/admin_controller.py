import web, re, base64
from functools import wraps
from datetime import datetime
from services import shared_helper, settings_service, post_service, page_service, tag_service
from models import Post, Page

###############################################################################
# General Housekeeping ########################################################
############################################################################### 

blog_settings =  settings_service.Settings().get_settings()
 
start_index = shared_helper.start_index
safe_number = shared_helper.safe_number
total_page = shared_helper.total_page

global_settings = {'settings': blog_settings }
render = web.template.render('views/admin', base='layout', globals=global_settings)

def assertLength(val, key, length, nullable):
    val = val.strip()
    if not nullable and (val is None or len(val) == 0) :
        raise Exception("Field " + key + " cannot be empty")
    if len(val) <= length :
        return val 
    else:
        raise Exception("Length of field " + key + " is larger than expected " + str(length))

###############################################################################
# BASIC AUTH      #############################################################
############################################################################### 

def check_auth(username, password): 
    return username == blog_settings.login and password == blog_settings.password

  
def requires_auth(f):
    @wraps(f)     
    def decorated(*args, **kwargs):        
        auth = web.ctx.env['HTTP_AUTHORIZATION'] if 'HTTP_AUTHORIZATION' in  web.ctx.env else None
        if auth:
            auth = re.sub('^Basic ', '', auth)
            username, password = base64.decodestring(auth).split(':')
        if not auth or not check_auth(username, password):
            web.header('WWW-Authenticate', 'Basic realm="admin"')
            web.ctx.status = '401 Unauthorized'
            return Unauthorized()
         
        return f(*args, **kwargs)
    
    return decorated
    
class Unauthorized():
    def GET(self):
        return "401 Unauthorized"

    def POST(self):
        return "401 Unauthorized"

###############################################################################
# Routes Handlers #############################################################
############################################################################### 

        
@requires_auth
class Index:
    def GET(self):
        #posts
        totalPosts = post_service.count_all()
        totalPostsPublished = post_service.count_published()
        totalUnpublishedPosts = totalPosts - totalPostsPublished
        unpublishedPosts = None
        if totalUnpublishedPosts > 0:
            unpublishedPosts = post_service.get_unpublished(0, totalUnpublishedPosts)
        #pages
        totalPages = page_service.count_all()
        totalPagesPublished = page_service.count_published()
        totalUnpublishedPages = tag_service.count_unpublished()
        unpublishedPages = None
        if totalUnpublishedPages > 0:
            unpublishedPages = page_service.get_unpublished(0, totalUnpublishedPages)
            
        #Topics
        totalTopics = tag_service.count_all()
        totalTopicsPublished = tag_service.count_published()
        totalTopicsUnPublished = tag_service.count_unpublished()
        unpublishedTopics = None
        if totalTopicsUnPublished > 0:
            unpublishedTopics = tag_service.get_unpublished()          
        
        return render.index(totalPosts, totalPostsPublished, unpublishedPosts,
                            totalPages, totalPagesPublished, unpublishedPages,
                             totalTopics, totalTopicsPublished, totalTopicsUnPublished, unpublishedTopics)

@requires_auth
class NewPost:
    def GET(self):
        post = Post("", "", "", datetime.now(), "", [])
        return render.post(post)
    
    def POST(self): 
        form = web.input()
        title = form.title
        tags = form.tags
        excerpt = form.excerpt
        content = form.content
        published_at = form.published_at
        slug = form.slug
        
        try:
            assert shared_helper.IsNotNull(title), "Post Title must be present"
            assert shared_helper.IsNotNull(content), "Post Content must be present"
            assert shared_helper.IsNotNull(published_at), "Published At date must be present!"
        except AssertionError, e:             
            raise web.notfound("Error while updating  post. \n error:[ %s ]" % e)
        
        publish_date = datetime.strptime(published_at, "%B %d, %Y")
        post_tags = [tag.strip() for tag in tags.split(",")]
        
        p = post_service.create(title, slug, content, publish_date, excerpt, post_tags)
        
        web.seeother('/admin/posts')

@requires_auth    
class EditPost:
    def GET(self, postId):
        post = post_service.get_by_id(postId)
        return render.post(post)
    
    def POST(self, postId):        
        form = web.input()
        id = postId
        title = form.title
        tags = form.tags
        excerpt = form.excerpt
        content = form.content
        published_at = form.published_at
        slug = form.slug
        
        try:
            assert shared_helper.IsNotNull(id), "Post Id must be present"
            assert shared_helper.IsNotNull(title), "Post Title must be present"
            assert shared_helper.IsNotNull(content), "Post Content must be present"
            assert shared_helper.IsNotNull(published_at), "Published At date must be present!"
        except AssertionError, e:             
            raise web.notfound("Error while updating  post. \n error:[ %s ]" % e)
        
        publish_date = datetime.strptime(published_at, "%B %d, %Y")
        post_tags = [tag.strip() for tag in tags.split(",")]
        
        p = post_service.update(id, title, slug, content, publish_date, excerpt, post_tags)
        
        web.seeother('/admin/posts')

@requires_auth    
class DeletePost:
    def POST(self, postId):
        if postId:
            post_service.destroy(postId)
        else:
            raise web.notfound("post id must be valid.")
            
        web.seeother('/admin/posts')
        
@requires_auth    
class Posts:
    def GET(self, page=1):
        p = safe_number(page) 
        limit = blog_settings.items_per_page
        offset = start_index(p, limit)
        totalPosts = post_service.count_all()
        totalPostsPublished = post_service.count_published()
        pageCount = total_page(totalPostsPublished, limit) 
        posts = post_service.get_published(offset, limit)
        nextLink = str(p + 1) if p < pageCount else None
        previousLink = str(p - 1) if p > 1 else None 
        return render.posts(totalPosts, totalPostsPublished, posts, nextLink, previousLink)
    
@requires_auth    
class NewPage:
    def GET(self):
        page = Page("", "", "", datetime.now())                
        return render.page(page)
    
    def POST(self):
         
        form = web.input()
        title = form.title
        content = form.content
        published_at = form.published_at
        slug = form.slug
        
        try:
            assert shared_helper.IsNotNull(title), "Page Title must be present"
            assert shared_helper.IsNotNull(content), "Page Content must be present"
            assert shared_helper.IsNotNull(published_at), "Published at date must be present!"
        except AssertionError, e:             
            raise web.notfound("Error while updating  page. \n error:[ %s ]" % e)
        
        publish_date = datetime.strptime(published_at, "%B %d, %Y")        
        
        p = page_service.create(title, slug, content, publish_date)
        
        web.seeother('/admin/pages')
        
@requires_auth    
class EditPage:
    def GET(self, pageId):
        page = page_service.get_by_id(pageId) 
        return render.page(page)
   
    def POST(self, pageId):
        id = pageId
        form = web.input()
        title = form.title
        content = form.content
        published_at = form.published_at
        slug = form.slug
        
        try:
            assert shared_helper.IsNotNull(title), "Page Title must be present"
            assert shared_helper.IsNotNull(content), "Page Content must be present"
            assert shared_helper.IsNotNull(published_at), "Published at date must be present!"
        except AssertionError, e:             
            raise web.notfound("Error while updating  page. \n error:[ %s ]" % e)
        
        publish_date = datetime.strptime(published_at, "%B %d, %Y")        
        
        p = page_service.update(id, title, slug, content, publish_date)
        
        web.seeother('/admin/pages')
        
@requires_auth    
class DeletePage:
    def POST(self, pageId):
        if pageId:
            page_service.destroy(pageId)
        else:
            raise web.notfound("page id must be valid.")
            
        web.seeother('/admin/pages')
        
@requires_auth    
class Pages:
    def GET(self, page=1):
        p = safe_number(page) 
        limit = blog_settings.items_per_page
        offset = start_index(p, limit)
        totalPages = page_service.count_all()
        totalPagesPublished = page_service.count_published()
        pageCount = total_page(totalPagesPublished, limit) 
        pages = page_service.get_published(offset, limit)
        nextLink = "/" + str(p + 1) if p < pageCount else None
        previousLink = "/" + str(p - 1) if p > 1 else None 
        return render.pages(totalPages, totalPagesPublished, pages, nextLink, previousLink)

@requires_auth
class DeleteTopic:
    def GET(self):
        return render.page()
    
@requires_auth    
class Topics:
    def GET(self):
        topics = tag_service.get_published()
        totalTopics = tag_service.count_all()
        totalTopicsPublished = len(topics)
        totaltopicsUnpublished = tag_service.count_unpublished()
        return render.topics(totalTopics, totalTopicsPublished, totaltopicsUnpublished, topics)
    
@requires_auth    
class Settings:
    def GET(self):
        settings = settings_service.Settings().get_settings()
        return render.settings(settings, False)
    
    def POST(self):
        form = web.input()
        settings = {}
        try:
            settings['bing_app_id'] = assertLength(form.bing_app_id, 'bing_app_id', 64, True)   
            settings['blog_title'] = assertLength(form.blog_title, 'blog_title', 256, False)#not null
            settings['cache_duration_in_seconds'] = safe_number(form.cache_duration_in_seconds)
            settings['disqus_short_name'] = assertLength(form.disqus_short_name, 'cache_duration_in_seconds', 512, True)
            settings['disqus_url'] = assertLength(form.disqus_url, 'disqus_url', 1028, True)
            settings['feed_burner_url'] = assertLength(form.feed_burner_url, 'feed_burner_url', 1024, True)
            settings['google_analytics_code'] = assertLength(form.google_analytics_code, 'google_analytics_code', 24, True)  
            settings['items_per_page'] = safe_number(form.items_per_page)  
            settings['login'] = assertLength(form.login, 'login', 128, False)#not null
            settings['password'] = assertLength(form.password, 'password', 128, False)#not null  
            settings['meta_description'] = assertLength(form.meta_description, 'meta_description', 512, True)
            settings['meta_keywords'] = assertLength(form.meta_keywords, 'meta_keywords', 512, True)
            settings['posts_in_home'] = safe_number(form.posts_in_home)#not null
            if settings['posts_in_home'] < 1:
                settings['posts_in_home'] = 10 # default to 10
            settings['root'] = assertLength(form.root, 'root', 1028, False)#not null                
            settings['tag_line'] = assertLength(form.tag_line, 'tag_line', 256, True)           
            settings['user_bio'] = assertLength(form.user_bio, 'user_bio', 2048, True)
            settings['user_email'] = assertLength(form.user_email, 'user_email', 256, True)
            settings['user_short_name'] = assertLength(form.user_short_name, 'user_short_name', 256, False)#not null 
            settings['user_full_name'] = assertLength(form.user_full_name, 'user_full_name', 256, True)
           
            updated_settings = settings_service.update_settings(settings)
            if updated_settings is None:
                return render.settings(form, "There was an error saving modified settings")
            return render.settings(updated_settings, True)
        except Exception, e:            
            return render.settings(form, e)
         
    

        
    

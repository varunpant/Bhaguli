import web,re,base64
from functools import wraps
from datetime import datetime
from services import shared_helper, settings_service, post_service, page_service, tag_service
from models import Post, Page

###############################################################################
# General Housekeeping ########################################################
############################################################################### 

blog_settings = settings_service.get_settings()
start_index = shared_helper.start_index
safe_number = shared_helper.safe_number
total_page = shared_helper.total_page

global_settings = {'settings': blog_settings }
render = web.template.render('views/admin', base='layout', globals=global_settings)



def check_auth(username, password): 
    print blog_settings.user_short_name   
    return username == blog_settings.login and password == blog_settings.password

  
def requires_auth(f):
    @wraps(f)     
    def decorated(*args, **kwargs):        
        auth = web.ctx.env['HTTP_AUTHORIZATION'] if 'HTTP_AUTHORIZATION' in  web.ctx.env else None
        if auth:
            auth = re.sub('^Basic ','',auth)
            username,password = base64.decodestring(auth).split(':')
        if not auth or not check_auth(username, password):
            web.header('WWW-Authenticate','Basic realm="admin"')
            web.ctx.status = '401 Unauthorized'
            
        return f(*args, **kwargs)
    return decorated

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
            raise web.notfound("Error while updating  post. \n error:[ %s ]"%e)
        
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
            raise web.notfound("Error while updating  post. \n error:[ %s ]"%e)
        
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
            raise web.notfound("Error while updating  page. \n error:[ %s ]"%e)
        
        publish_date = datetime.strptime(published_at, "%B %d, %Y")        
        
        p = page_service.create(title, slug, content, publish_date)
        
        web.seeother('/admin/pages')
        
@requires_auth    
class EditPage:
    def GET(self, pageId):
        page = page_service.get_by_id(pageId) 
        return render.page(page)
   
    def POST(self,pageId):
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
            raise web.notfound("Error while updating  page. \n error:[ %s ]"%e)
        
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
        settings = settings_service.get_settings()
        return render.settings(settings)
    
    

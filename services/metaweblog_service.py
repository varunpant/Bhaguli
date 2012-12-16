import  web , xmlrpclib, re, datetime, os, errno
from services import shared_helper, post_service, page_service, tag_service, settings_service
###############################################################################
# General Housekeeping ########################################################
############################################################################### 

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
before_dot = re.compile('(metaWeblog|blogger|mt|wp)\.')

blog_settings = settings_service.get_settings()
global_settings = {'settings': blog_settings}
safe_number = shared_helper.safe_number
render = web.template.render('views/api', globals=global_settings)


###############################################################################
# META WEB LOG API ############################################################
###############################################################################

def get_users_blogs(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
        
    blog = { "url" : blog_settings.root, "blogid" : "1000", "blogName":blog_settings.blog_title }
    blogs = [blog]
    return xmlrpclib.dumps(tuple([blogs]), None, "blogger.getUsersBlogs")
  
def get_categories(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
    
    tags = tag_service.get_all()
    categories = []
    if tags:
        categories = map(lambda tag:_map_tags(tag), tags)
       
    return xmlrpclib.dumps(tuple([categories]), None, "blogger.getCategories")

def get_recent_posts(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
    
    limit = safe_number(command[3])
    if limit == 0:
        limit = blog_settings.items_per_page 
    _posts = post_service.get_published(0, limit) 
   
    posts = []
    if _posts:
        posts = map(lambda post:_map_post(post), _posts)
    return xmlrpclib.dumps(tuple([posts]), None, "blogger.getRecentPosts")
    
def get_post(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
        
    id = command[0];
    post = _map_post(post_service.get_by_id(id)) or {};
    return xmlrpclib.dumps(tuple([post]), None, "blogger.getPost") 

def new_post(command):    
    post_info = command[3]
    published_at = get_published_at(post_info) if command[4] else None;
    title = post_info['title']
    wp_slug = post_info.get('wp_slug') or ""
    description = post_info['description']
    mt_excerpt = post_info.get('mt_excerpt') or ""
    categories = post_info['categories'] 
    post = post_service.create(title, wp_slug,description, published_at,mt_excerpt, categories)

    return xmlrpclib.dumps(tuple([post.id]), None, "blogger.newPost")

def edit_post(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
        
    updated = False;
    id = safe_number(command[0])
    if id > 0:
        post_info = command[3]
        published_at = get_published_at(post_info) if command[4] else None;
        post_service.update(str(id), post_info['title'], None, post_info['description'], published_at, post_info['mt_excerpt'], post_info['categories'])
        updated = True
    return xmlrpclib.dumps(tuple([updated]), None, "blogger.editPost")
    
def delete_post(command):
    if not valid_credential(command[2], command[3]):        
        return invalid_credential()
        
    deleted = False;
    id = safe_number(command[1])
    if id > 0:
        post_service.destroy(str(id))
        deleted = True
    
    return xmlrpclib.dumps(tuple([deleted]), None, "blogger.deletePost")

def get_pages(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
    
    limit = safe_number(command[3])
    if limit == 0:
        limit = blog_settings.items_per_page
    
    pages = []
    _pages = page_service.get_all(0, limit)
    
    if _pages:
        pages = map(lambda page:_map_page(page), _pages)
        
    return xmlrpclib.dumps(tuple([pages]), None, "blogger.getPages")
 
def get_page(command):
    if not valid_credential(command[2], command[3]):        
        return invalid_credential()
        
    id = command[1];
    page = _map_page(page_service.get_by_id(id)) or {}   
    
    return xmlrpclib.dumps(tuple([page]), None, "blogger.getPages")

def new_page(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()    
   
    page_info = command[3]
    published_at = get_published_at(page_info) if command[4] else None;

    page = page_service.create(page_info['title'], page_info['wp_slug'], page_info['description'], published_at)
    return xmlrpclib.dumps(tuple([page.id]), None, "blogger.newPage")

def edit_page(command):
    if not valid_credential(command[2], command[3]):        
        return invalid_credential()
        
    updated = False;
    id = safe_number(command[1])
    if id > 0:
        page_info = command[4]
        published_at = get_published_at(page_info) if command[5] else None;
        page_service.update(id, page_info['title'],None, page_info['description'], published_at)
        updated = True
        
    return xmlrpclib.dumps(tuple([updated]), None, "blogger.editPage")

def delete_page(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
    
    deleted = False;
    id = safe_number(command[3])
    if id > 0:
        page_service.destroy(str(id))
        deleted = True
    
    return xmlrpclib.dumps(tuple([deleted]), None, "blogger.deletePage")

def new_media_object(command):
    if not valid_credential(command[1], command[2]):        
        return invalid_credential()
        
    media_object = command[3]
    name = os.path.basename(media_object['name'])
    data = media_object['bits']
    
    dir = os.path.join(os.getcwd(), "static")
    dir = os.path.join(dir, "resources")    
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    
    filename = os.path.join(dir, name)
       
    
    fout = open(filename, "wb")
    fout.write(bytes(data))
    fout.close()
     
    result = {"file" : name, "url": blog_settings.root + "/static/resources/" + name }
        
    return xmlrpclib.dumps(tuple([result]), None, "blogger.newMediaObject")

def invalid_credential():
    fault_code = 2041
    fault_string = 'Invalid credential. Please specify correct UserName/Password and retry.'
    return render.fault(code=fault_code, msg=fault_string)
    
def valid_credential(user_name, password):
    return user_name == blog_settings.login and password == blog_settings.password
    
def _map_tags(tag):
    return{
            "categoryId" : tag.id,
            "title" : tag.title,
            "description" : tag.title,
            "htmlUrl" : blog_settings.root + "/topics/" + tag.slug + "/1" ,
            "rssUrl" : ''
           }
           
def _map_post(post):     
    return {
             "postid" : post.id,
             "userid" : "1000",
             "dateCreated" :post.published_at or post.created_at.strftime("%Y%m%dT%H:%M:%S"),
             "title" :post.title,
             "description" :post.content,
             "link" : blog_settings.root + "/posts/" + post.created_at.strftime("%Y%m%dT%H:%M:%S"),
             "wp_slug" :post.created_at,
             "mt_excerpt" :post.excerpt,
             "publish" :post.published_at is not None,
             "categories" :[[tag.title for tag in post.tags]]
            }
            
def _map_page(page):
    return {
             "postid": page.id,
             "userid": "1000",
             "dateCreated": page.published_at or page.created_at.strftime("%Y%m%dT%H:%M:%S"),
             "title": page.title,
             "description": page.content,
             "link": blog_settings.root + "/" + page.created_at.strftime("%Y%m%dT%H:%M:%S"),
             "wp_slug": page.created_at,
             "publish": page.published_at is not None
            }
           
def get_published_at(content_info):
    published_at = None
    if 'dateCreated' in content_info and content_info['dateCreated']:
        published_at = datetime.datetime.strptime(str(content_info['dateCreated']), "%Y%m%dT%H:%M:%S") 
    if not published_at and "pubDate" in content_info and content_info['pubDate']:
        published_at = datetime.datetime.strptime(str(content_info['pubDate']), "%Y%m%dT%H:%M:%S")
    if not published_at:
        published_at = datetime.datetime.utcnow()
   
    return published_at





###############################################################################
###############################  XXXXXXXXXXXXX  ###############################
###############################################################################

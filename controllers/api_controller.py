import  web , xmlrpclib, re, os
from services import shared_helper, post_service,page_service,tag_service, settings_service,metaweblog_service


###############################################################################
# General Housekeeping ########################################################
############################################################################### 

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
before_dot = re.compile('(metaWeblog|blogger|mt|wp)\.')

blog_settings = settings_service.Settings().get_settings()
global_settings = {'settings': blog_settings}
render = web.template.render('views/api', globals=global_settings)


   
###############################################################################
# Routes Handlers #############################################################
############################################################################### 


class Sitemap:
    def GET(self):
        web.header('Content-Type', 'text/xml;charset=utf-8')
        posts = post_service.get_all_published()
        pages = page_service.get_all_published()
        tags = tag_service.get_all()
        archives = post_service.get_archives()
        return render.sitemap(posts,pages,tags,archives)
    
class SitemapStyle:
    def GET(self):        
        return render.sitemapXsl() 
       
class Rsd:
    def GET(self):
        web.header('Content-Type', 'text/xml;charset=utf-8')       
        return render.rsd()
    
class Wlwmanifest:
    def GET(self):        
        return render.wlwmanifest()
    
class Metaweblog:
    def POST(self): 
        web.header('Content-Type', 'text/xml;charset=utf-8')
        xml = web.data()
        
        if xml:
            command = xmlrpclib.loads(xml)
            name = before_dot.sub("", command[1])
            method = all_cap_re.sub(r'\1_\2', first_cap_re.sub(r'\1_\2', name)).lower()
            return metaweblog_service.__dict__[method](command[0])
        else:
            raise web.notfound("Invalid Post content.")
    
class Feed:
    def GET(self):
        web.header('Content-Type', 'text/xml;charset=utf-8')
        posts = post_service.get_all(0, blog_settings.items_per_page)
        if posts:
            return render.atom(posts)
        else:
            raise render.notfound("This page was not found.")
        
class Opensearch:
    def GET(self):
        web.header('Content-Type', 'text/xml;charset=utf-8')
        return render.opensearch()
    
class Robots:  
    def GET(self):
        web.header('Content-Type', 'text/plain;charset=utf-8')
        return "user-agent: * \nsitemap: " + blog_settings.root + "/sitemap.xml \nallow: /"
    

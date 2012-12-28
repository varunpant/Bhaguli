###############################################################################
# Settings Querying Service #######################################################
###############################################################################
from models import getSession , Setting
 

class CacheFetcher:
    def __init__(self):
        self.cache = None
    def fetch(self):        
        if self.cache:
            return self.cache
        # Retrieve and cache
        session = getSession()   
        #print "############# cached #############"
        self.cache = session.query(Setting).scalar()        
        return self.cache
    
    def clear(self):
        self.cache = None   

def get_settings():     
    return CacheFetcher().fetch()

def reset():
    CacheFetcher().clear()

def update_settings(settings):
    session = getSession()
    current_settings = session.query(Setting).scalar()
    
    current_settings.blog_title = settings["blog_title"]
    current_settings.tag_line = settings["tag_line"]
    current_settings.meta_keywords = settings["meta_keywords"]
    current_settings.meta_description = settings["meta_description"]
    current_settings.items_per_page = settings["items_per_page"]
    current_settings.posts_in_home = settings["posts_in_home"]
    current_settings.cache_duration_in_seconds = settings["cache_duration_in_seconds"]
    current_settings.login = settings["login"]
    current_settings.password = settings["password"]
    current_settings.user_full_name = settings["user_full_name"]
    current_settings.user_email = settings["user_email"]
    current_settings.user_bio = settings["user_bio"]
    current_settings.user_short_name = settings["user_short_name"]
    current_settings.root = settings["root"]
    current_settings.google_analytics_code = settings["google_analytics_code"]
    current_settings.feed_burner_url = settings["feed_burner_url"]
    current_settings.bing_app_id = settings["bing_app_id"]
    current_settings.disqus_short_name = settings["disqus_short_name"]
    current_settings.disqus_url = settings["disqus_url"]
    try:        
        session.add(current_settings)
        session.commit()
        reset();
        return get_settings()  
    except  Exception, e:
        print e
        return None
        pass
        
    
    
    

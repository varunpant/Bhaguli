import time
from services import tag_service, page_service, post_service,settings_service

blog_settings =  settings_service.Settings().get_settings()

class Cache: 

    class __impl: 
        def __init__(self):
            self.cache = {}
        def fetch(self, key, max_age=5):            
            if self.cache.has_key(key):            
                if int(time.time()) - self.cache[key][0] < max_age:
                    return self.cache[key][1]
            # Retrieve and cache        
            data = []
            if key == '_tags':
                data = tag_service.get_popular(5)
            elif key == '_pages':
                data = page_service.get_published(0, 5)
            elif key == '_posts':
                data = post_service.get_published(0, 10)           
            self.cache[key] = (time.time(), data)
            return data
    
        def get_tags(self):        
            return self.fetch('_tags')        
            
        def get_pages(self):
            return self.fetch('_pages')
        
        def get_posts(self):
            return self.fetch('_posts')
            

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create Settings instance """
        # Check whether we already have an instance
        if Cache.__instance is None:
            # Create and remember instance
            Cache.__instance = Cache.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Cache.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)  
    

 
    

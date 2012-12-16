###############################################################################
# Settings Querying Service #######################################################
###############################################################################
from models import getSession,Setting
 

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
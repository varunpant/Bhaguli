import unittest, web
web.config.dbpath = "sqlite://"   

 
from services import settings_service
from models import createSchema, dropSchema, executeRaw

class SettingsServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema() 
        executeRaw("""INSERT INTO "settings"(blog_title ,
                                            tag_line,
                                            meta_keywords,
                                            meta_description ,
                                            items_per_page,
                                            posts_in_home,
                                            cache_duration_in_seconds ,
                                            login,
                                            password,
                                            user_full_name,
                                            user_email,
                                            user_bio,
                                            user_short_name ,
                                            root,
                                            google_analytics_code,
                                            feed_burner_url,
                                            bing_app_id,
                                            disqus_short_name,
                                            disqus_url) 
                                            VALUES(
                                            'Bhaguli Blog',
                                            'Blog Engine',
                                            'python',
                                            'Blog Engine written in Python'
                                            ,10,
                                            5,
                                            10,
                                            'admin',
                                            'admin',
                                            'Bhaguli',
                                            'a@a.com',
                                            'author bio',
                                            'author short',
                                            'http://localhost:3333',
                                            '',
                                            '/',
                                            '',
                                            '',
                                            ''
                                            )
                                            """) 
        self.service = settings_service         
        self.enteries = {
                        'blog_title':'Bhaguli Blog' ,
                        'tag_line':'Blog Engine',
                        'meta_keywords':'python',
                        'meta_description':'Blog Engine written in Python' ,
                        'items_per_page':10,
                        'posts_in_home':5,
                        'cache_duration_in_seconds' :10,
                        'login':'admin',
                        'password':'admin',
                        'user_full_name':'Bhaguli',
                        'user_email':'a@a.com',
                        'user_bio':'author bio',
                        'user_short_name':'author short' ,
                        'root':'http://localhost:3333',
                        'google_analytics_code':'',
                        'feed_burner_url':'/',
                        'bing_app_id':'',
                        'disqus_short_name':'',
                        'disqus_url':''}
    def tearDown(self):
        dropSchema()
        
    def test_get_settings(self):
        settings = self.service.get_settings()
        self.assertIsNotNone(settings, "Failed to retrive settings object")
        for k, v in vars(settings).items():
            if k in self.enteries:
                self.assertEqual(self.enteries[k], v, 'one of the entries did not match' + str(v))
    
    def test_update_settings(self):
        self.enteries["blog_title"] = "updated blog settings"
        settings = self.service.update_settings(self.enteries)
        self.assertIsNotNone(settings, "Failed to retrive settings object")
        for k, v in vars(settings).items():
            if k in self.enteries:
                self.assertEqual(self.enteries[k], v, 'one of the entries did not match' + str(v))
        
        
            
if __name__ == '__main__':
    unittest.main()
     

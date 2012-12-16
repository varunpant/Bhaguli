import unittest, web
from datetime import datetime
from xml.etree.ElementTree import XML, fromstring, tostring
web.config.dbpath = "sqlite://" 

from models import createSchema, dropSchema, executeRaw
from services import post_service ,page_service

class MetaWebLogServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema()
       
        executeRaw("INSERT INTO archives (year,month,posts_count) VALUES (2012,9,1)")             
        executeRaw("""INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) 
                      VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'post-slug', 'Post Title')""")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag', 'tag',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (1,1)")           
        executeRaw(""" INSERT INTO pages ( content,created_at,published_at,slug,title) 
                       VALUES ('test','2012-09-10 19:20:01.413000','2012-09-10 19:20:01.410000','page-slug','Page Title') """)
        executeRaw("INSERT INTO pages (content, created_at, published_at, slug, title) VALUES ('test page', '2012-09-10 19:20:01.413000','2012-09-10 19:20:01.410000','slug', 'Page Title')")
        
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
                                            'Bhaguli Blog','
                                             Blog Engine','
                                             python','
                                             Blog Engine written in Python'
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
        from services import metaweblog_service
       
        self.service = metaweblog_service         
    
    def tearDown(self):
        dropSchema()
        
    def __getStruct(self, root):
        return root[0][0][0][0][0][0][0]
    
    def __getMemberVal(self, member):
        return member[0].text, member[1][0].text
            
    def test_get_users_blogs(self):        
        actual = fromstring(self.service.get_users_blogs(('0123456789ABCDEF', 'admin', 'admin')))
        struct = self.__getStruct(actual) 
        #for member in struct:
             #print self.__getMemberVal(member)
        self.assertEqual(('url', 'http://localhost:3333'), self.__getMemberVal(struct[0]))
        self.assertEqual(('blogid', '1000'), self.__getMemberVal(struct[1]))
        self.assertEqual(('blogName', 'Bhaguli Blog'), self.__getMemberVal(struct[2]))
    
    def test_get_categories(self):
        actual = fromstring(self.service.get_categories(('http://localhost:3333/', 'admin', 'admin')))
        struct = self.__getStruct(actual) 
        self.assertEqual(('htmlUrl', 'http://localhost:3333/topics/tag/1'), self.__getMemberVal(struct[0]))
        self.assertEqual(('rssUrl', None), self.__getMemberVal(struct[1]))
        self.assertEqual(('description', 'tag'), self.__getMemberVal(struct[2]))
        self.assertEqual(('categoryId', '1'), self.__getMemberVal(struct[3]))
        self.assertEqual(('title', 'tag'), self.__getMemberVal(struct[4]))
       
    
    def test_get_recent_posts(self):
        actual = fromstring(self.service.get_recent_posts(('http://localhost:3333/', 'admin', 'admin', 1)))
        struct = self.__getStruct(actual)
        self.assertEqual(('categories', None), self.__getMemberVal(struct[0]))    
        self.assertEqual(('link', 'http://localhost:3333/posts/20120910T19:20:01'), self.__getMemberVal(struct[1]))
        self.assertEqual(('description', 'test'), self.__getMemberVal(struct[2]))
        self.assertEqual(('title', 'Post Title'), self.__getMemberVal(struct[3]))
        self.assertEqual(('publish', '1'), self.__getMemberVal(struct[4]))
        self.assertEqual(('mt_excerpt', 'test excerpt'), self.__getMemberVal(struct[5]))
        self.assertEqual(('postid', '1'), self.__getMemberVal(struct[6])) 
        self.assertEqual(('userid', '1000'), self.__getMemberVal(struct[7]))
        self.assertEqual(('wp_slug', '20120910T19:20:01'), self.__getMemberVal(struct[8]))
        self.assertEqual(('dateCreated', '20120910T19:20:01'), self.__getMemberVal(struct[9]))  
       
        
    def test_get_post(self):
        actual = fromstring(self.service.get_post(('1', 'admin', 'admin', 1)))
        struct = actual[0][0][0][0]
        self.assertEqual(('categories', None), self.__getMemberVal(struct[0]))
        self.assertEqual(('link', 'http://localhost:3333/posts/20120910T19:20:01'), self.__getMemberVal(struct[1])) 
        self.assertEqual(('description', 'test'), self.__getMemberVal(struct[2])) 
        self.assertEqual(('title', 'Post Title'), self.__getMemberVal(struct[3]))
        self.assertEqual(('publish', '1'), self.__getMemberVal(struct[4]))
        self.assertEqual(('mt_excerpt', 'test excerpt'), self.__getMemberVal(struct[5]))
        self.assertEqual(('postid', '1'), self.__getMemberVal(struct[6]))
        self.assertEqual(('userid', '1000'), self.__getMemberVal(struct[7]))
        self.assertEqual(('wp_slug', '20120910T19:20:01'), self.__getMemberVal(struct[8]))  
        self.assertEqual(('dateCreated', '20120910T19:20:01'), self.__getMemberVal(struct[9])) 
        
    
    def test_new_post(self):
        actual = fromstring(self.service.new_post(('http://localhost:3333/', 'admin', 'admin',
                                                   {'description': '<p>This is a temporary post that was not deleted. Please delete this manually. (6fdaec14-3bab-4988-921f-fc78c48f341f - 3bfe001a-32de-4114-a6b4-4005b770f6d7)</p>',
                                                    'title': 'Temporary Post Used For Theme Detection (a5d74376-abfc-409e-b745-b295d1756540 - 3bfe001a-32de-4114-a6b4-4005b770f6d7)',
                                                    'mt_excerpt': '',
                                                    'wp_slug': '',
                                                    'mt_basename': '',
                                                    'categories': []}, True)))
        
        methodResponse = actual[0][0][0][0]        
        self.assertEqual('2', methodResponse.text)
    
    def test_edit_post(self):
        actual = fromstring(self.service.edit_post(('1', 'admin',
                                                    'admin',
                                                    { 'description': '<p>Lorem ipsum dolor sit amet</p>',
                                                      'title': 'stuff title',
                                                      'mt_excerpt': 'blaaah',
                                                      'date_created_gmt': '20121201T19:17:00',
                                                      'dateCreated': '20121201T19:17:00',
                                                      'wp_slug': '20121117T12:02:14',
                                                      'mt_basename': '20121117T12:02:14',
                                                      'mt_basename': '20121125T11:03:41',
                                                      'categories': ['test1', 'test2']},
                                                      True)))
        methodResponse = actual[0][0][0][0]
        self.assertEqual('1', methodResponse.text)
        post = post_service.get_by_id(1)
        self.assertEqual('stuff title', post.title)
        self.assertEqual('stuff-title', post.slug)
        self.assertEqual('<p>Lorem ipsum dolor sit amet</p>', post.content)
        self.assertEqual(datetime(2012, 9, 10, 19, 20, 1, 413000), post.created_at)
        self.assertEqual(datetime(2012, 12, 1, 19, 17), post.published_at)
        self.assertEqual('blaaah', post.excerpt)
        self.assertEqual(2, len(post.tags))
    
    def test_delete_post(self):
        actual = fromstring(self.service.delete_post(('0123456789ABCDEF', '1', 'admin', 'admin', True)))
        methodResponse = actual[0][0][0][0]
        self.assertEqual('1', methodResponse.text)
    
    def test_get_pages(self):
        actual = fromstring(self.service.get_pages(('http://localhost:3333/', 'admin', 'admin', 50)))
        struct = self.__getStruct(actual)
        self.assertEqual(('link', 'http://localhost:3333/20120910T19:20:01'), self.__getMemberVal(struct[0]))    
        self.assertEqual(('description', 'test'), self.__getMemberVal(struct[1])) 
        self.assertEqual(('title', 'Page Title'), self.__getMemberVal(struct[2]))
        self.assertEqual(('publish', '1'), self.__getMemberVal(struct[3]))
        self.assertEqual(('postid', '1'), self.__getMemberVal(struct[4]))
        self.assertEqual(('userid', '1000'), self.__getMemberVal(struct[5]))
        self.assertEqual(('wp_slug', '20120910T19:20:01'), self.__getMemberVal(struct[6]))
        self.assertEqual(('dateCreated', '20120910T19:20:01'), self.__getMemberVal(struct[7]))
        
    
    def test_get_page(self):
        actual = fromstring(self.service.get_page(('http://localhost:3333/', '1', 'admin', 'admin')))
        struct = actual[0][0][0][0]
        self.assertEqual(('link', 'http://localhost:3333/20120910T19:20:01'), self.__getMemberVal(struct[0]))
        self.assertEqual(('description', 'test'), self.__getMemberVal(struct[1]))
        self.assertEqual(('title', 'Page Title'), self.__getMemberVal(struct[2]))
        self.assertEqual(('publish', '1'), self.__getMemberVal(struct[3]))
        self.assertEqual(('postid', '1'), self.__getMemberVal(struct[4]))
        self.assertEqual(('userid', '1000'), self.__getMemberVal(struct[5]))
        self.assertEqual(('wp_slug', '20120910T19:20:01'), self.__getMemberVal(struct[6]))
        self.assertEqual(('dateCreated', '20120910T19:20:01'), self.__getMemberVal(struct[7]))
        
    
    
    def test_new_page(self):
        actual = fromstring(self.service.new_page((('http://localhost:3333/', 
                                                    'admin', 'admin', 
        { 'mt_basename': '',
          'description': '<p>this is a test page</p>', 
          'wp_slug': '', 
          'title': 'test page'},True))))
        struct = actual[0][0][0][0]
        self.assertEqual('3', struct.text)
        page = page_service.get_by_id(3)
        self.assertEqual('test page', page.title)
        self.assertEqual('test-page', page.slug)
        self.assertEqual('<p>this is a test page</p>', page.content)
               
    
    def test_edit_page(self):
        actual = fromstring(self.service.edit_page(('http://localhost:3333/',
                                                     '1',
                                                     'admin',
                                                     'admin',
     {'mt_basename': '20120315T20:40:59', 
      'description': '<P>edited</p>', 
      'wp_slug': '20120315T20:40:59',                                                                                                       
      'title': 'Android Experiments'},  True)))
        
        struct = actual[0][0][0][0]
        self.assertEqual('1', struct.text)
        page = page_service.get_by_id(1)
        self.assertEqual('Android Experiments', page.title)
        self.assertEqual('android-experiments', page.slug)
        self.assertEqual('<P>edited</p>', page.content)
        self.assertEqual(datetime(2012, 9, 10, 19, 20, 1, 413000), page.created_at)
    
    def test_delete_page(self):
        actual = fromstring(self.service.delete_page(('http://localhost:3333/', 'admin', 'admin', '1')))
        methodResponse = actual[0][0][0][0]
        self.assertEqual('1', methodResponse.text)
        
    
if __name__ == '__main__':    
    unittest.main()

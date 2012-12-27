import unittest, web
web.config.dbpath = "sqlite://"

from services import search_service
from models import createSchema, dropSchema, executeRaw


class SearchServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        
        self.service = search_service  
        db = web.database(dbn='sqlite', db=web.config.dbpath)
        executeRaw("CREATE VIRTUAL TABLE search using FTS4(title, slug, content, published_at,ispost);")
        executeRaw("INSERT INTO SEARCH(title,slug, content, published_at, isPost) VALUES ('Hello World','Hello World', 'hello world this is my first post','2010-10-03 11:15:52.000000', '1')")
        executeRaw("INSERT INTO SEARCH(title,slug, content, published_at, isPost) VALUES ('Hi World','Hi World', 'hello world this is my second post','2010-10-04 11:15:52.000000','1')")
        executeRaw("INSERT INTO SEARCH(title,slug, content, published_at, isPost) VALUES('Hello World','Hello World', 'Sup world this is another post','2010-10-05 11:15:52.000000','1')")
        executeRaw("INSERT INTO SEARCH(title,slug, content, published_at, isPost) VALUES('o World', 'o World', 'namste world this is my first post','2010-10-06 11:15:52.000000','1')")
        
               
    
    def tearDown(self):
        executeRaw("DROP TABLE search;")
               
        
    def test_search(self):
        results = self.service.search('hello', 0, 5) 
        self.assertEqual(len(results), 3)        
        results = self.service.search('sup', 0, 5)        
        self.assertEqual(len(results), 1)
        results = self.service.search('World', 0, 5)        
        self.assertEqual(len(results), 4)
        results = self.service.search('post', 0, 5)        
        self.assertEqual(len(results), 4)
     
    def test_search_count(self):         
        results = self.service.getCount('hello')        
        self.assertEqual(results[0], 3)        
        results = self.service.getCount('sup')        
        self.assertEqual(results[0], 1)
        results = self.service.getCount('World')        
        self.assertEqual(results[0], 4)
        results = self.service.getCount('post')        
        self.assertEqual(results[0], 4)
        
if __name__ == '__main__':    
    unittest.main()
        

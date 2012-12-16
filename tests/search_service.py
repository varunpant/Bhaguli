import unittest, web
web.config.dbpath = "sqlite://"

from services import search_service
from models import createSchema, dropSchema, executeRaw


class TagServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        
        self.service = search_service  
        db = web.database(dbn='sqlite', db = web.config.dbpath)
        executeRaw("CREATE VIRTUAL TABLE search using FTS4(title, slug, content,  isPost);")
        executeRaw("INSERT INTO SEARCH(title,slug, content,  isPost) VALUES ('Hello World','Hello World', 'hello world this is my first post', '1')")
        executeRaw("INSERT INTO SEARCH(title,slug, content,  isPost) VALUES ('Hi World','Hi World', 'hello world this is my second post',   '1')")
        executeRaw("INSERT INTO SEARCH(title,slug, content,  isPost) VALUES('Hello World','Hello World', 'Sup world this is another post',  '1')")
        executeRaw("INSERT INTO SEARCH(title,slug, content,  isPost) VALUES('o World', 'o World', 'namste world this is my first post', '1')")
        
               
    
    def tearDown(self):
        executeRaw("DROP TABLE search;")
               
        
    def test_search(self):
        results = self.service.search('hello') 
        self.assertEqual(len(results), 3)        
        results = self.service.search('sup')        
        self.assertEqual(len(results), 1)
        results = self.service.search('World')        
        self.assertEqual(len(results), 4)
        results = self.service.search('post')        
        self.assertEqual(len(results), 4)
        
if __name__ == '__main__':    
    unittest.main()
        

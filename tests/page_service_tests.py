import unittest, web
from datetime import datetime
web.config.dbpath = "sqlite://" 

from services import page_service
from models import createSchema, dropSchema, executeRaw, Page


class PageServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema()
                   
        executeRaw("INSERT INTO pages (content, created_at, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','2012-09-10 19:20:01.410000','slug', 'Page Title')")
        
        self.service = page_service         
    
    def tearDown(self):
        dropSchema()
    
    def test_get_by_id(self):
        page = self.service.get_by_id(1)         
        self.assertIsInstance(page, Page, "obj is not an instance of Post")
        self.assertEqual(page.title, "Page Title")
    
    def test_get_published_by_slug(self):
        page = self.service.get_published_by_slug("slug")         
        self.assertIsInstance(page, Page, "obj is not an instance of Post")
        self.assertEqual(page.title, "Page Title")
        
    def test_get_all(self):
        executeRaw("INSERT INTO pages (content, created_at, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', '2012-08-10 19:20:01.410000', 'slug-2', 'Another Title')")
        pages = self.service.get_all(0, 2)
        self.assertEqual(len(pages), 2) 
        
        pages = self.service.get_all(0, 3)
        self.assertEqual(len(pages), 2) 
        
        pages = self.service.get_all(0, 1)
        self.assertEqual(len(pages), 1) 
        
        page = self.service.get_all(1, 2)[0]
        self.assertIsInstance(page, Page, "obj is not an instance of Page")
        self.assertEqual(page.title, "Another Title")
    
    def test_get_all_published(self):
        executeRaw("INSERT INTO pages (content, created_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','slug-2', 'Another Title')")
        pages = self.service.get_all_published()
        self.assertEqual(len(pages), 1) 
        
    def test_get_published(self):
        executeRaw("INSERT INTO pages (content, created_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','slug-2', 'Another Title')")
        pages = self.service.get_published(0, 1)
        page = pages[0]
        self.assertEqual(len(pages), 1)
        self.assertEqual(page.title, "Page Title")  
    
    def test_get_unpublished(self):
        executeRaw("INSERT INTO pages (content, created_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','slug-2', 'UnPublished Title')")
        pages = self.service.get_unpublished(0, 1)
        page = pages[0]
        self.assertEqual(len(pages), 1)
        self.assertEqual(page.title, "UnPublished Title")
        
    def test_count_all(self):
        executeRaw("INSERT INTO pages (content, created_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','slug-2', 'Another Title')")
        executeRaw("INSERT INTO pages (content, created_at, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', '2012-08-10 19:20:01.410000', 'slug-2', 'Another Title')")
        
        count = self.service.count_all()
        self.assertEqual(count, 3)
    
    def test_count_published(self):
        executeRaw("INSERT INTO pages (content, created_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','slug-2', 'Another Title')")
        executeRaw("INSERT INTO pages (content, created_at, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', '2012-08-10 19:20:01.410000', 'slug-2', 'Another Title')")
        
        count = self.service.count_published()
        self.assertEqual(count, 2)
    
    def test_count_unpublished(self):
        executeRaw("INSERT INTO pages (content, created_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','slug-2', 'Another Title')")
        
        count = self.service.count_unpublished()
        self.assertEqual(count, 1)
        
class PageServicePublishingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema() 
        self.service = page_service         
    
    def tearDown(self):
        dropSchema()
        
    def test_create(self):
        t = datetime.now()
        page = self.service.create("page title", "page-slug", "<p>page content</p>", datetime.now())
        self.assertEqual(page.title, "page title")
        self.assertEqual(page.slug,  "page-slug")
        self.assertEqual(page.content, "<p>page content</p>")
        self.assertEqual(page.published_at, t) 
      
    def test_update(self):
        t = datetime.now()
        page = self.service.create("updated page title", "updated-page-slug", "<p>updated page content</p>", datetime.now())
        self.assertEqual(page.title, "updated page title")
        self.assertEqual(page.slug,  "updated-page-slug")
        self.assertEqual(page.content, "<p>updated page content</p>")
        self.assertEqual(page.published_at, t) 
    
    def test_destroy(self):
        executeRaw("INSERT INTO pages (content, created_at, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000','2012-09-10 19:20:01.410000','slug', 'Page Title')")
        self.service.destroy(1)
        self.assertEqual(self.service.count_all(), 0) 
        
    
if __name__ == '__main__':    
    suite = unittest.TestLoader().loadTestsFromTestCase(PageServicePublishingTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

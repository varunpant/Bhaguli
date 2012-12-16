import unittest, web
web.config.dbpath = "sqlite://"   

from datetime import date, datetime
from services import post_service
from models import createSchema, dropSchema, executeRaw, Post

class PostServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema() 

        executeRaw("INSERT INTO archives (year,month,posts_count) VALUES (2012,9,1)")             
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'slug', 'Post Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('slug', 'Post Title',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (1,1)")
        
        self.service = post_service         
    
    def tearDown(self):
        dropSchema()
    
    def test_get_by_id(self):
        post = self.service.get_by_id(1)         
        self.assertIsInstance(post, Post, "obj is not an instance of Post")
        self.assertEqual(post.title, "Post Title")
        
    def test_get_published_by_slug(self):
        post = self.service.get_published_by_slug("slug")         
        self.assertIsInstance(post, Post, "obj is not an instance of Post")
        self.assertEqual(post.title, "Post Title")
        
    def test_get_all(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-08-10 19:20:01.410000', 'slug-2', 'Another Title')")
        posts = self.service.get_all(0, 2)
        self.assertEqual(len(posts), 2) 
        
        posts = self.service.get_all(0, 3)
        self.assertEqual(len(posts), 2) 
        
        posts = self.service.get_all(0, 1)
        self.assertEqual(len(posts), 1) 
        
        post = self.service.get_all(1, 2)[0]
        self.assertIsInstance(post, Post, "obj is not an instance of Post")
        self.assertEqual(post.title, "Another Title")

    def test_get_all_published(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt',  'slug-2', 'Another Title')")
        posts = self.service.get_all_published()
        self.assertEqual(len(posts), 1) 
      
    def test_get_published(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt',  'slug-2', 'Another Title')")
        posts = self.service.get_published(0, 2)
        self.assertEqual(len(posts), 1) 
    
    def test_get_unpublished(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt',  'slug-2', 'UnPublished Title')")
        posts = self.service.get_unpublished(0, 2)
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.title, "UnPublished Title")          
    
    def test_find_recent(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-10-10 19:20:01.410000', 'slug-2', 'Recent Title')")
        post = self.service.find_recent(1)[0]
        self.assertEqual(post.title, "Recent Title") 
    
    def test_find_published_by_tag(self):
        post = self.service.find_published_by_tag('slug', 0, 1)[0]
        self.assertEqual(post.title, "Post Title")
    
    def test_find_published_by_date_range(self):
        post = self.service.find_published_by_date_range("2012-09-1", "2012-09-30")[0]
        self.assertEqual(post.title, "Post Title")
        d1 = date(2012, 9, 1)
        d2 = date(2012, 9, 30)
        post = self.service.find_published_by_date_range(d1, d2)[0]
        self.assertEqual(post.title, "Post Title")
    
    def test_find_published_by_year(self):     
        post = self.service.find_published_by_year(2012, 0, 1)[0]
        self.assertEqual(post.title, "Post Title")
        
    def test_find_published_by_year_and_month(self):    
        post = self.service.find_published_by_year_and_month(2012, 9, 0, 1)[0]
        self.assertEqual(post.title, "Post Title")
            
    def test_find_published_by_year_month_and_day(self):
        post = self.service.find_published_by_year_month_and_day(2012, 9, 10, 0, 1)[0]
        self.assertEqual(post.title, "Post Title")
    
    def test_count_all(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt',  'slug-2', 'Another Title')")
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-08-10 19:20:01.410000', 'slug-2', 'Another Title')")
        count = self.service.count_all()
        self.assertEqual(count, 3)
    
    def test_count_published(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt',  'slug-2', 'Another Title')")
        count = self.service.count_published()
        self.assertEqual(count, 1)
        
    def test_count_unpublished(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt',  'slug-2', 'Another Title')")
        count = self.service.count_unpublished()
        self.assertEqual(count, 1)
    
    def test_count_published_by_tag(self):
        count = self.service.count_published_by_tag("slug")
        self.assertEqual(count, 1)
    
    def test_get_archives(self):
        archive = self.service.get_archives()[0]
        self.assertEqual(archive.year, 2012)
        self.assertEqual(archive.month, 9)
        self.assertEqual(archive.posts_count, 1)
        
class PostServicePublishingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema() 
 
        self.service = post_service         
    
    def tearDown(self):
        dropSchema()
    
    def test_post_create(self):
        t = datetime.now()
        post = self.service.create("title", "slug", "<p>content</p>", t, "excerpt", ["tag1", "tag2"])
        self.assertEqual(post.title, "title")
        self.assertEqual(post.slug, "slug")
        self.assertEqual(post.content, "<p>content</p>")
        self.assertEqual(post.published_at, t) 
        self.assertEqual(post.excerpt, "excerpt")
        self.assertEqual(len(post.tags), 2)
        
        count = self.service.count_published_by_tag("tag1")
        self.assertEqual(count, 1)
        
        archive = self.service.get_archives()[0]
        self.assertEqual(archive.year, t.year)
        self.assertEqual(archive.month, t.month)
        self.assertEqual(archive.posts_count, 1)
        
    def test_post_update(self):
        executeRaw("INSERT INTO archives (year,month,posts_count) VALUES (2012,9,1)")             
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'slug', 'Post Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('slug', 'tag',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (1,1)")
        
        t = datetime.now()
        post = self.service.update(1, "updated title", "updated-title", "<p>updated-content</p>", t, "updated-excerpt", ["tag3"])
        self.assertEqual(post.title, "updated title")
        self.assertEqual(post.slug, "updated-title")
        self.assertEqual(post.content, "<p>updated-content</p>")
        self.assertEqual(post.published_at, t) 
        self.assertEqual(post.excerpt, "updated-excerpt")
        self.assertEqual(len(post.tags), 1)
        self.assertEqual(post.tags[0].title, "tag3") 
        row = list(executeRaw("select * from taggings"))[0]
        self.assertEqual(row.post_id, 1) 
        self.assertEqual(row.tag_id, 2) 
        
        tags = list(executeRaw("select * from tags"))
        self.assertEqual(tags[0].title, "tag")
        self.assertEqual(tags[1].title, "tag3")
        
    def test_post_delete(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'slug', 'Post Title')")    
        self.service.destroy(1)
        self.assertEqual(self.service.count_all(), 0)
  
if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(PostServicePublishingTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

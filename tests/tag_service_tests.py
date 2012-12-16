import unittest, web
web.config.dbpath = "sqlite://"   

from services import tag_service
from models import createSchema, dropSchema, executeRaw, Tag

class TagServiceQueryingTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema() 
        
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'slug', 'Post Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug', 'Tag Title',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (1,1)")
        
        self.service = tag_service         
    
    def tearDown(self):
        dropSchema()
        
    def test_get_by_title(self):
        tag = self.service.get_by_title('Tag Title')         
        self.assertIsInstance(tag, Tag, "obj is not an instance of Tag")
        self.assertEqual(tag.title, "Tag Title")

    def test_get_by_slug(self):
        tag = self.service.get_by_slug('tag-slug')         
        self.assertIsInstance(tag, Tag, "obj is not an instance of Tag")
        self.assertEqual(tag.title, "Tag Title")
    
    def test_get_all(self):
        tags = self.service.get_all()
        self.assertEqual(len(tags), 1)
    
    def test_get_published(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', 'slug', 'UnPublished Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug', 'Un Published Tag Title',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (2,2)")
        tags = self.service.get_published()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].title, "Tag Title")
       
        
    def test_get_unpublished(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', 'slug', 'UnPublished Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug', 'Un Published Tag Title',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (2,2)")
        tags = self.service.get_unpublished()
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].title, "Un Published Tag Title")
    
    def test_count_all(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', 'slug-2', 'UnPublished Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug-2', 'Tag Title 2',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (2,2)")
        count = self.service.count_all()
        self.assertEqual(count, 2)
    
    def test_count_published(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', 'slug-2', 'UnPublished Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug-2', 'Tag Title 2',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (2,2)")
        count = self.service.count_published()
        self.assertEqual(count, 1)
        
    def test_count_unpublished(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, slug, title) VALUES ('test', '2012-09-10 19:20:01.413000', 'test excerpt', 'slug-2', 'UnPublished Title')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug-2', 'Tag Title 2',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (2,2)")
        count = self.service.count_unpublished()
        self.assertEqual(count, 1)
        
    def test_get_popular(self):
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test - 2', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'slug - 2', 'Post Title - 2')")
        executeRaw("INSERT INTO tags (slug, title,posts_count) VALUES ('tag-slug-2', 'Tag Title 2',1)")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (2,2)")
        
        executeRaw("INSERT INTO posts (content, created_at, excerpt, published_at, slug, title) VALUES ('test - 2', '2012-09-10 19:20:01.413000', 'test excerpt', '2012-09-10 19:20:01.410000', 'slug - 3', 'Post Title - 3')")
        executeRaw("Update tags set posts_count = 2 where slug ='tag-slug-2'")
        executeRaw("INSERT INTO taggings (post_id, tag_id) VALUES (3,2)")
        
        tags = self.service.get_popular(2)
         
        tag = tags[0]
        self.assertEqual(tag.title, 'Tag Title 2')
        self.assertEqual(tag.slug, 'tag-slug-2')
    
if __name__ == '__main__':    
    unittest.main()

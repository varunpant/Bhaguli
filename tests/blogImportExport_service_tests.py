import unittest, web
web.config.dbpath = "sqlite://"   

from services import blogImportExport_service
from models import createSchema, dropSchema, executeRaw

class BlogImportTestCase(unittest.TestCase):
    
    def setUp(self): 
        createSchema()  
        self.service = blogImportExport_service         
    
    def tearDown(self):
        dropSchema()
        
    def test_import(self):
        self.service.import_blog("BlogML.xml") 
        print list(executeRaw("select count(*) from posts"))[0]  
        
if __name__ == '__main__':    
    unittest.main()

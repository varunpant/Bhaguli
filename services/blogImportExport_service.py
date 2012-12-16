from xml.dom import minidom
import sqlite3, datetime
from services import post_service 

###############################################################################
# Blog ML #####################################################################
###############################################################################
BLOGML_NS = "http://www.blogml.com/2006/09/BlogML"
def import_blog(blogMlPath):
    xml = open(blogMlPath)
    doc = minidom.parseString(xml.read())
    xml.close()
    
    blog_categories = {}
    categories = doc.getElementsByTagNameNS(BLOGML_NS, 'categories')[0].getElementsByTagNameNS(BLOGML_NS, 'category')
    for cat in categories:
        blog_categories[cat.getAttribute("id")] = cat.getElementsByTagName('title')[0].firstChild.data
    
    blog_posts = []
    posts = doc.getElementsByTagNameNS(BLOGML_NS, 'posts')[0].getElementsByTagNameNS(BLOGML_NS, 'post')
    for post in posts:
        title = post.getElementsByTagName('title')[0].firstChild.data
        slug = post.getElementsByTagName('post-name')[0].firstChild.data
        content = post.getElementsByTagName('content')[0].firstChild.data
        published_at = post.getAttribute("date-modified")
        created_at = post.getAttribute("date-created")
        post_categories = []
        categories = post.getElementsByTagNameNS(BLOGML_NS, 'categories')[0].getElementsByTagNameNS(BLOGML_NS, 'category')
        for cat in categories:
            category_id = cat.getAttribute("ref")
            category_name = blog_categories[category_id]
            post_categories.append(category_name)
        tags = post.getElementsByTagNameNS(BLOGML_NS, 'tags')[0].getElementsByTagNameNS(BLOGML_NS, 'tag')
        for tag in tags:
            tag_name = tag.getAttribute("ref")        
            post_categories.append(tag_name)
        blog_posts.append({"title":title, "slug":slug, "content":content, "published_at":published_at, "created_at":created_at, "categories":post_categories})
       
        for post in blog_posts:
            published_at = datetime.datetime.strptime(post["created_at"], "%Y-%m-%dT%H:%M:%S")
            post_service.create(post["title"], post["slug"], post["content"], published_at, "", post["categories"])

def export_blog():
    return ""
    

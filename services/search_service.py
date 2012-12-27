from models import getSession

def search(q, offset, items_per_page):    
    session = getSession()
    connection = session.connection()
    resp = connection.execute("SELECT * from(SELECT * FROM search where title LIKE '%" + str(q) + "%' UNION SELECT * FROM search where content LIKE '%" + str(q) + "%' ) ORDER BY title LIMIT " + str(items_per_page) + " OFFSET " + str(offset))
    return resp.fetchall() 
    
def getCount(q):    
    session = getSession()
    connection = session.connection()
    resp = connection.execute("SELECT count(*) from(SELECT * FROM search where title LIKE '%" + q + "%' UNION  SELECT * FROM search where content LIKE '%" + q + "%' )")
    return resp.fetchone() 
    

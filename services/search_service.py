from models import getSession

def search(q):    
    session = getSession()
    connection = session.connection()
    resp = connection.execute("SELECT * FROM search where search MATCH '%s'"%q)
    return resp.fetchall() 
    

from sqlite3 import connect

def connected(func):

    def wrapper(*args, **kwargs):
        #print(args, kwargs)
        connection = connect("Vocaloid.db")
        cursor = connection.cursor()
        result = func(*args, cursor=cursor, **kwargs)
        cursor.close()
        connection.commit()
        connection.close()
        return result
    
    return wrapper
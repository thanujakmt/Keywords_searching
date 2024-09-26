
from database_connection import Database_Connection

def fetch_mysql_query_executer(query):
    db_connection,db_cursor = Database_Connection()
    try:
        db_cursor.execute(query)
        data = db_cursor.fetchall()
        db_cursor.close()
        return data
    except Exception as e:
        print(f"Database Fetch Exception : {e}")

def commit_mysql_query_executer(query):
    db_connection,db_cursor = Database_Connection()
    try:
        db_cursor.execute(query)
        db_connection.commit()
        db_cursor.close()
        # print('Data Inserted')
    except Exception as e:
        print(f"Database Fetch Exception : {e}")

def get_website_from_db():
    # query = f"select * from {location_table} order by rand() limit 1"
    query = f"SELECT gl_id,website FROM acupuncturists_websites order by rand() limit 1;"
    data = fetch_mysql_query_executer(query)
    return data[0][1]

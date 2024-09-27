
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
    except Exception as e:
        print(f"Database Fetch Exception : {e}")

def get_website_from_db(niche):
    query = f"SELECT gl_id,website FROM {niche}_websites where training_check_done_flag is null order by rand() limit 1;"
    data = fetch_mysql_query_executer(query)
    return data

def update_training_check_done_flag(gl_id,niche):
    query = f"update {niche}_websites set training_check_done_flag = 1 where gl_id = {gl_id}"
    commit_mysql_query_executer(query)
    print(f"Training_check_done_flag updated : {gl_id}")

def update_training_flag(gl_id,niche):
    query = f"update {niche}_websites set training_flag = 1 where gl_id = {gl_id}"
    commit_mysql_query_executer(query)
    print(f"Training_flag updated : {gl_id}")

def update_website_error_flag(gl_id,niche):
    query = f"update {niche}_websites set website_error_flag = 1 where gl_id = {gl_id}"
    commit_mysql_query_executer(query)
    print(f"Website_error_flag updated : {gl_id}")

def get_remaining_websites_counts(niche):
    query = f"SELECT count(*) FROM {niche}_websites where training_check_done_flag is null and training_flag is null and website_error_flag is null;"
    data = fetch_mysql_query_executer(query)
    return data[0][0]

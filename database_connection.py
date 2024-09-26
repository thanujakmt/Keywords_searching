
import mysql.connector
# from niche_details import *

def Database_Connection():
    db_connection = mysql.connector.connect(
        # host = host,
        # user = db_credential[NICHE]['user'],
        # password =db_credential[NICHE]['password'],
        # database = db_credential[NICHE]['database'],
        
        host = 'helenzys-mysql-dev.clyhoefsujtn.us-east-1.rds.amazonaws.com',
        user = 'htb_websites_db',
        password ='gol)Force72',
        database = 'htb_websites_db'

        # host = 'localhost',
        # user = 'root',
        # password ='Power1234',
        # database = 'google_scrapper_testing',
        # auth_plugin='mysql_native_password'
    )

    db_cursor = db_connection.cursor()

    return db_connection,db_cursor

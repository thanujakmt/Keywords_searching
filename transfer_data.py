
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from config import *

def get_mysql_connection(user, password, host, database):
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:3306/{database}"
    engine = create_engine(connection_string)
    return engine  

def fetch_data(engine, query):
    # Use pandas to execute the query and fetch data into a DataFrame
    with engine.connect() as connection:
        result = pd.read_sql(query, connection)
    return result

source_engine = get_mysql_connection(source_user, source_password, host, source_database)
target_engine = get_mysql_connection(target_user, target_password, host, target_database)

query = "SELECT gl_id as id,gl_website as website, country FROM homeopathy_business_db.uae_homeopathy_business_data where gl_website is not null and gl_website !='None' limit 1"  

def dump_data_to_new_db(source_engine, target_engine, table_name):
    # Step 1: Fetch data from the source database
    fetch_query = f"SELECT * FROM {table_name};"
    data = fetch_data(source_engine, fetch_query)
    
    # Step 2: Create the table in the new database if it doesn't exist
    with target_engine.connect() as connection:
        # Create table with the same schema as in source (adjust as needed)
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT PRIMARY KEY,
            websites VARCHAR(255),
            country VARCHAR(255),
            niche VARCHAR(50),
            website_error_flag TINYINT,
            training_flag TINYINT
        );
        """
        connection.execute(create_table_query)
    
    # Step 3: Insert data into the new database
    data.to_sql(table_name, target_engine, if_exists='append', index=False)
    
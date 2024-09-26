
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from config import *
from retry import retry

def get_mysql_connection(user, password, host, database):
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:3306/{database}"
    engine = create_engine(connection_string)
    return engine  

def fetch_data(engine, query):
    # Use pandas to execute the query and fetch data into a DataFrame
    with engine.connect() as connection:
        result = pd.read_sql(query, connection)
    return result

@retry(tries=3)
def dump_data_to_new_db(source_engine, target_engine, destination_table_name,source_table_name):
    print("Processing dumping...")
    query = f"""SELECT gl_id, gl_website as website, country,category as niche FROM {source_table_name} WHERE gl_website IS NOT NULL AND gl_website != 'None'"""  

    # Step 1: Fetch data from the source database
    data = fetch_data(source_engine, query)
    
    # Step 2: Create the table in the new database if it doesn't exist
    with target_engine.connect() as connection:
        # Create table with the same schema as in source (adjust as needed)
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {destination_table_name} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            gl_id INT,
            website Text,
            country VARCHAR(255),
            niche VARCHAR(255),
            website_error_flag TINYINT,
            training_flag TINYINT,
            training_check_done_flag TINYINT
        );
        """
        # Wrap the raw SQL in text()
        connection.execute(text(create_table_query))
    
    # Step 3: Insert data into the new database
    data.to_sql(destination_table_name, target_engine, if_exists='append', index=False)
    print("Data dumping done")

if __name__ == '__main__':

    source_engine = get_mysql_connection(source_user, source_password, host, source_database)
    target_engine = get_mysql_connection(target_user, target_password, host, target_database)

    for country in countries:
        print(country)
        source_table_name = f"{country}_{niche}_business_data"
        dump_data_to_new_db(source_engine=source_engine, target_engine=target_engine, destination_table_name=destination_table_name,source_table_name=source_table_name)

import os
import logging
from modulos import DataConn , DataRetriever
from dotenv import load_dotenv

logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s ::MainModule-> %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

load_dotenv()

def main():
    user_credentials = {
        "REDSHIFT_USERNAME" : os.getenv('REDSHIFT_USERNAME'),
        "REDSHIFT_PASSWORD" : os.getenv('c'),
        "REDSHIFT_HOST" : os.getenv('REDSHIFT_HOST'),
        "REDSHIFT_PORT" : os.getenv('REDSHIFT_PORT', '5439'),
        "REDSHIFT_DBNAME" : os.getenv('REDSHIFT_DBNAME')
    }

    schema:str = "robyrubirex_coderhouse"
    table:str = "stage_api_dolarucos"

    data_conn = DataConn(user_credentials, schema)
    data_retriever = DataRetriever()

    try:
        data = data_retriever.get_data() #data from api
        data_conn.upload_data(data, table)
        logging.info(f"Data uploaded to -> {schema}.{table}")

    except Exception as e:
        logging.error(f"Not able to upload data\n{e}")
        
    finally:
        data_conn.close_conn()

if __name__ == "__main__":
    main()
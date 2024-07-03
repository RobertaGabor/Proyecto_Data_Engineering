import os
import logging
from dotenv import load_dotenv
from airflow.operators.python_operator import PythonOperator
import pandas as pd
from sqlalchemy import create_engine
import requests
from io import StringIO
from airflow.operators.bash import BashOperator
from airflow import DAG
from datetime import timedelta,datetime
import psycopg2
from psycopg2.extras import execute_values



load_dotenv()  # take environment variables from .env.


# argumentos por defecto para el DAG
default_args = {
    'owner': 'gabor',
    'start_date': datetime(2024,7,3),
    'retries':5,
    'retry_delay': timedelta(minutes=5)
}

BC_dag = DAG(
    dag_id='Proyecto_Final_USD_ETL',
    default_args=default_args,
    description='Agrega data de Dolares cambiarios de forma diaria',
    schedule_interval="@daily",
    catchup=False
)

def process_data():

    schema:str = "robyrubirex_coderhouse"
    table:str = "stage_api_dolarucos"

    url = os.getenv("REDSHIFT_HOST")
    user = os.getenv("REDSHIFT_USERNAME")
    pwd = os.getenv("REDSHIFT_PASSWORD")
    data_base = os.getenv("REDSHIFT_DBNAME")
    port= os.getenv("REDSHIFT_PORT")

    try:
        conn_data = psycopg2.connect(
            host=url,
            dbname=data_base,
            user=user,
            password=pwd,
            port=port
        )
        print("Connected to Redshift successfully!")
    except Exception as e:
        print("Unable to connect to Redshift.")
        print(e)

    def get_data(url):
        response_json = requests.get(url).json()
        data_by_list_api:pd.DataFrame = pd.DataFrame(response_json)
        # columnas necesarias para la ingestan en las tablas
        cols:list[str] = ["moneda","casa","nombre","compra", "venta","fechaActualizacion"]
        data = data_by_list_api[cols]
        
        try:
            data = pd.DataFrame(data)
            data = data.fillna(0)
            buffer = StringIO()
            data.info(buf=buffer)
            s = buffer.getvalue()
            logging.info(s)
            logging.info(f"Data created")
            return data
        
        except Exception as e:
            print(f"Not able to import the data from the api")
    
    
    def upload_data(conn, data: pd.DataFrame, table: str):

        try:
            # Crear una columna compuesta 'id'
            data['id'] = data['nombre'] + '_' + data['fechaActualizacion'].astype(str)

            #eliminar filas con id duplicado

            redshift_ids_query = f"SELECT id FROM robyrubirex_coderhouse.{table}"
            redshift_ids = pd.read_sql(redshift_ids_query, con=conn)
            redshift_ids_set = set(redshift_ids['id'].tolist())

            data = data[~data['id'].isin(redshift_ids_set)]

            if data.empty:
                print("No new data to upload. All IDs are already in the table.")
                return

            dtypes= data.dtypes
            cols= list(dtypes.index)
            tipos= list(dtypes.values)

            cur = conn.cursor()
            # Define the table name
            table_name = table
            # Define the columns you want to insert data into
            columns = cols
            # Generate 
            values = [tuple(x) for x in data.to_numpy()]
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
            # Execute the INSERT statement using execute_values
            cur.execute("BEGIN")
            execute_values(cur, insert_sql, values)
            cur.execute("COMMIT")    

            print("Data from the DataFrame has been uploaded to the table in Redshift.")
        except Exception as e:
            print(f"Failed to upload data")
            raise


    #obtengo data          
    df=get_data("https://dolarapi.com/v1/dolares")

    # Carga de datos en RedShift
    upload_data(conn=conn_data, data=df, table="stage_api_dolarucos")
    conn_data.close()




task1 = BashOperator(task_id='primera_tarea',
    bash_command='echo Iniciando...'
)

task2 = PythonOperator(
    task_id='download_data',
    python_callable=process_data,
    dag=BC_dag,
)

task3 = BashOperator(
    task_id= 'tercera_tarea',
    bash_command='echo Proceso completado...'
)
task1 >> task2 >> task3

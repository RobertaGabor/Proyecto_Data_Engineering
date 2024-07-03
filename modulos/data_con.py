import pandas as pd
import logging
from sqlalchemy import create_engine

logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s ::DataConnectionModule-> %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
    
class DataConn:
    def __init__(self, config: dict,schema: str):
        self.config = config
        self.schema = schema
        self.db_engine = None


    def get_conn(self):
        username = self.config.get('username')
        password = self.config.get('pwd')
        host = self.config.get('host')
        port = self.config.get('port', '5439')
        dbname = self.config.get('database')

        # Construct the connection URL
        self.db_engine = create_engine(host)

        try:
            with self.db_engine.connect() as connection:
                result = connection.execute('SELECT 1;')
            if result:
                logging.info("Connection created")
                return
        except Exception as e:
            logging.error(f"Failed to create connection: {e}")
            raise
    
    def check_table_exists(self, table_name:str) -> bool:
        with self.db_engine.connect() as connection:
            cursor = connection.cursor
            query_checker = f"""
                SELECT 1 FROM information_schema.tables 
                WHERE  table_schema = f'{self.schema}'
                AND    table_name   = '{table_name}';              
            """
            cursor.execute(query_checker)
            
            if not cursor.fetchone():
                logging.error(f"No {table_name} has been created")
                raise ValueError(f"No {table_name} has been created")

            logging.info(f"{table_name} exists")
    
    def upload_data(self, data: pd.DataFrame, table: str):
        if self.db_engine is None:
            logging.warn("Execute it before")
            self.get_conn()

        try:
            # Crear una columna compuesta 'id'
            data['id'] = data['nombre'] + '_' + data['fechaActualizacion'].astype(str)

            #eliminar filas con id duplicado

            redshift_ids_query = f"SELECT id FROM {self.schema}.{table}"
            redshift_ids = pd.read_sql(redshift_ids_query, con=self.db_engine)
            redshift_ids_set = set(redshift_ids['id'].tolist())

            data = data[~data['id'].isin(redshift_ids_set)]

            if data.empty:
                logging.info("No new data to upload. All IDs are already in the table.")
                return
            
            data.to_sql(
                table,
                con=self.db_engine,
                schema=self.schema,
                if_exists='append',
                index=False
            )

            logging.info(f"Data from the DataFrame has been uploaded to the {self.schema}.{table} table in Redshift.")
        except Exception as e:
            logging.error(f"Failed to upload data to {self.schema}.{table}:\n{e}")
            raise

    def close_conn(self):
        if self.db_engine:
            self.db_engine.dispose()
            logging.info("Connection to Redshift closed.")
        else:
            logging.warning("No active connection to close.")
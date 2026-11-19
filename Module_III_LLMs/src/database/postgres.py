import psycopg2

from config import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def connect():
    """Establish connection with credentials

    Returns:
        connection: connection with database 
    """
    
    try:
        return psycopg2.connect(                    
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DBNAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
    except psycopg2.OperationalError:
        print('Error while connecting with database, check your credentials on .env file.')
    

def query(sql: str, *data):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, data) 
            return cur.fetchall()

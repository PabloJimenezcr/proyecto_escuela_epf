import os
import mysql.connector
from dotenv import load_dotenv

# Carga las variables del archivo .env local
load_dotenv()

def get_db_connection():
    """Establece y devuelve la conexión a la base de datos MySQL."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error crítico al conectar a MySQL: {err}")
        return None

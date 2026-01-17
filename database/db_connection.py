import mysql.connector
from mysql.connector import errorcode

# Konfiguracja połączenia MySQL
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '1364'
DB_NAME = 'finance_tracker'

def get_db_connection():
    """Tworzy połączenie z konkretną bazą danych aplikacji."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Błąd połączenia z bazą danych: {err}")
        return None
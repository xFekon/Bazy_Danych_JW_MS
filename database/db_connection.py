import mysql.connector
from database.db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Połączono z bazą danych!")
        conn.close()
    except Exception as e:
        print("❌ Błąd połączenia:", e)
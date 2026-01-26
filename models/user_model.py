import hashlib
from database.db_connection import get_db_connection

class UserModel:
    def login(self, username, password):
        conn = get_db_connection()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT user_id, username FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        return user

    def register(self, username, password):
        # Rejestracja przy użyciu Procedury Składowanej
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor()
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            # WYWOŁANIE PROCEDURY SQL
            # Procedura sama robi INSERT do users, accounts i categories w jednej transakcji
            cursor.callproc('register_user_complex', [username, hashed_pw])
            conn.commit()
            return True
        except Exception as e:
            print(f"Rejestracja error: {e}")
            return False
        finally:
            conn.close()
            
    def get_public_users(self):
        """Przykładowe użycie WIDOKU (bez haseł)"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Pobieramy dane z widoku, nie z tabeli
        cursor.execute("SELECT * FROM view_public_users")
        users = cursor.fetchall()
        conn.close()
        return users
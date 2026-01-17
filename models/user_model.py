import hashlib
from database.db_connection import get_db_connection

class UserModel:
    def login(self, username, password):
        conn = get_db_connection()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)
        
        # hashowanie SHA256
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT user_id, username FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        return user

    def register(self, username, password):
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor()
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, hashed_pw))
            conn.commit()
            return True
        except Exception as e:
            print(f"Rejestracja error: {e}")
            return False
        finally:
            conn.close()
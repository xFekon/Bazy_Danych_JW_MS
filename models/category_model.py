from database.db_connection import get_db_connection

class CategoryModel:
    def get_all(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Pobieramy systemowe (NULL) oraz użytkownika
        sql = "SELECT * FROM categories WHERE user_id IS NULL OR user_id = %s ORDER BY type, name"
        cursor.execute(sql, (user_id,))
        res = cursor.fetchall()
        conn.close()
        return res

    def add_category(self, user_id, name, c_type, parent_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO categories (user_id, name, type, parent_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, name, c_type, parent_id))
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            conn.close()
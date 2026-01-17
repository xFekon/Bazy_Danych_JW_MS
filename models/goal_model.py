from database.db_connection import get_db_connection

class GoalModel:
    def add_goal(self, user_id, name, target, deadline=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO savings_goals (user_id, name, target_amount, deadline_date) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, name, target, deadline))
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd celu: {e}")
            return False
        finally:
            conn.close()

    def get_goals(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM savings_goals WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        res = cursor.fetchall()
        conn.close()
        return res
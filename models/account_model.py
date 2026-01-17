from database.db_connection import get_db_connection

class AccountModel:
    def get_accounts_by_user(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    def create_account(self, user_id, name, acc_type, balance):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO accounts (user_id, name, type, current_balance) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (user_id, name, acc_type, balance))
        conn.commit()
        conn.close()

    def get_net_worth(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        # Sumowanie sald [cite: 120]
        cursor.execute("SELECT SUM(current_balance) FROM accounts WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0
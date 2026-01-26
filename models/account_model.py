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
        try:
            sql = "INSERT INTO accounts (user_id, name, type, current_balance, is_active) VALUES (%s, %s, %s, %s, TRUE)"
            cursor.execute(sql, (user_id, name, acc_type, balance))
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd tworzenia konta: {e}")
            return False
        finally:
            conn.close()

    def get_net_worth(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(current_balance) FROM accounts WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0

    def toggle_status(self, account_id, is_active):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            val = 1 if is_active else 0
            cursor.execute("UPDATE accounts SET is_active = %s WHERE account_id = %s", (val, account_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd aktualizacji statusu: {e}")
            return False
        finally:
            conn.close()

    def delete_account(self, account_id):
        """Trwale usuwa konto i wszystkie powiązane transakcje (dzięki ON DELETE CASCADE w bazie)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM accounts WHERE account_id = %s", (account_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd usuwania konta: {e}")
            return False
        finally:
            conn.close()
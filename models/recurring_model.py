from database.db_connection import get_db_connection
from datetime import date
from dateutil.relativedelta import relativedelta # Wymaga: pip install python-dateutil

class RecurringModel:
    def add_recurring(self, user_id, name, amount, account_id, category_id, t_type, frequency, start_date):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO recurring_payments 
                (user_id, name, amount, account_id, category_id, type, frequency, next_payment_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, name, amount, account_id, category_id, t_type, frequency, start_date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd dodawania cyklicznej: {e}")
            return False
        finally:
            conn.close()

    def get_all(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Pobierz z nazwami kategorii i kont
        sql = """
            SELECT r.*, c.name as category_name, a.name as account_name 
            FROM recurring_payments r
            LEFT JOIN categories c ON r.category_id = c.category_id
            JOIN accounts a ON r.account_id = a.account_id
            WHERE r.user_id = %s
        """
        cursor.execute(sql, (user_id,))
        res = cursor.fetchall()
        conn.close()
        return res

    def process_due_payments(self, user_id):
        # Automatyzacja: Sprawdza i generuje zaległe płatności
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Znajdź płatności, które są aktywne i mają datę <= dzisiaj
            sql_find = """
                SELECT * FROM recurring_payments 
                WHERE user_id = %s AND is_active = TRUE AND next_payment_date <= CURDATE()
            """
            cursor.execute(sql_find, (user_id,))
            due_payments = cursor.fetchall()

            for p in due_payments:
                print(f"Przetwarzam płatność cykliczną: {p['name']}")
                
                # 2. Utwórz transakcję
                cursor.execute("START TRANSACTION")
                
                sql_trx = """
                    INSERT INTO transactions (user_id, account_id, category_id, type, amount, transaction_date, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                desc = f"Płatność cykliczna: {p['name']}"
                cursor.execute(sql_trx, (p['user_id'], p['account_id'], p['category_id'], p['type'], p['amount'], p['next_payment_date'], desc))

                # Aktualizacja salda konta
                if p['type'] == 'expense':
                    cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (p['amount'], p['account_id']))
                elif p['type'] == 'income':
                    cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (p['amount'], p['account_id']))

                # 3. Oblicz nową datę (prosta logika miesięczna)
                current_date = p['next_payment_date']
                new_date = current_date + relativedelta(months=1)

                # 4. Zaktualizuj rekord recurring
                sql_update = "UPDATE recurring_payments SET next_payment_date = %s, last_generated_date = %s WHERE recurring_id = %s"
                cursor.execute(sql_update, (new_date, date.today(), p['recurring_id']))
                
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            print(f"Błąd automatyzacji: {e}")
        finally:
            conn.close()
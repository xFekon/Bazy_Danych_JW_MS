from database.db_connection import get_db_connection

class TransactionModel:
    def add_transaction(self, user_id, account_id, category_id, t_type, amount, date_val, desc, transfer_to_id=None, goal_id=None):
        # ... (Ta metoda pozostaje bez zmian, wklej ją z poprzednich wersji) ...
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor()

        try:
            cursor.execute("START TRANSACTION")

            sql_insert = """
                INSERT INTO transactions 
                (user_id, account_id, category_id, type, amount, transaction_date, description, transfer_to_account_id, goal_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (user_id, account_id, category_id, t_type, amount, date_val, desc, transfer_to_id, goal_id))

            # Aktualizacja sald
            if t_type == 'expense':
                cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (amount, account_id))
            elif t_type == 'income':
                cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (amount, account_id))
            elif t_type == 'transfer' and transfer_to_id:
                cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (amount, account_id))
                cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (amount, transfer_to_id))

            if goal_id:
                cursor.execute("UPDATE savings_goals SET saved_amount = saved_amount + %s WHERE goal_id = %s", (amount, goal_id))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Transaction error: {e}")
            return False
        finally:
            conn.close()

    def get_recent(self, user_id, limit=20):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT t.*, a.name as account_name, c.name as category_name, g.name as goal_name
            FROM transactions t
            LEFT JOIN accounts a ON t.account_id = a.account_id
            LEFT JOIN categories c ON t.category_id = c.category_id
            LEFT JOIN savings_goals g ON t.goal_id = g.goal_id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT %s
        """
        cursor.execute(sql, (user_id, limit))
        res = cursor.fetchall()
        conn.close()
        return res

    def get_monthly_expenses(self, user_id, category_id=None):
        # ... (Bez zmian, skopiuj z poprzedniej wersji) ...
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT DATE_FORMAT(transaction_date, '%Y-%m') as month_str, SUM(amount) as total
            FROM transactions 
            WHERE user_id = %s AND type = 'expense'
        """
        params = [user_id]
        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)
        query += " GROUP BY month_str ORDER BY month_str ASC LIMIT 12"
        try:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Exception: return []
        finally: conn.close()

    # --- NOWA METODA ---
    def delete_transaction(self, transaction_id):
        conn = get_db_connection()
        if not conn: return False
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("START TRANSACTION")

            # 1. Pobierz dane o usuwanej transakcji, aby cofnąć saldo
            cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
            trx = cursor.fetchone()
            
            if not trx:
                conn.rollback()
                return False

            amount = trx['amount']
            acc_id = trx['account_id']
            t_type = trx['type']
            transfer_to = trx['transfer_to_account_id']
            goal_id = trx['goal_id']

            # 2. Cofnij zmiany salda (Rewers)
            if t_type == 'expense':
                # Był wydatek (minus), więc przy usuwaniu dodajemy z powrotem
                cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (amount, acc_id))
            
            elif t_type == 'income':
                # Był przychód (plus), więc przy usuwaniu odejmujemy
                cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (amount, acc_id))
            
            elif t_type == 'transfer' and transfer_to:
                # Był transfer (zródło minus, cel plus), więc odwracamy
                cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (amount, acc_id))
                cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (amount, transfer_to))

            # Cofnij cel oszczędnościowy (jeśli dotyczy)
            if goal_id:
                cursor.execute("UPDATE savings_goals SET saved_amount = saved_amount - %s WHERE goal_id = %s", (amount, goal_id))

            # 3. Usuń właściwy rekord
            cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Delete error: {e}")
            return False
        finally:
            conn.close()
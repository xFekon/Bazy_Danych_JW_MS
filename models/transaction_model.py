from database.db_connection import get_db_connection

class TransactionModel:
    def add_transaction(self, user_id, account_id, category_id, t_type, amount, date_val, desc, transfer_to_id=None, goal_id=None):
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

            # Aktualizacja sald kont
            if t_type == 'expense':
                cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (amount, account_id))
            elif t_type == 'income':
                cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (amount, account_id))
            elif t_type == 'transfer' and transfer_to_id:
                cursor.execute("UPDATE accounts SET current_balance = current_balance - %s WHERE account_id = %s", (amount, account_id))
                cursor.execute("UPDATE accounts SET current_balance = current_balance + %s WHERE account_id = %s", (amount, transfer_to_id))

            # Aktualizacja Celu Oszczędnościowego (jeśli dotyczy) 
            if goal_id:
                # Jeśli to wpłata na cel, zwiększamy saved_amount
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
        # ... (bez zmian z poprzedniej wersji, dodaj tylko ewentualnie goal_id do selecta) ...
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
        """Zwraca listę: [{'month': '2025-01', 'total': 1200.50}, ...]"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Filtrujemy tylko wydatki (expense)
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
        except Exception as e:
            print(f"Błąd raportu: {e}")
            return []
        finally:
            conn.close()
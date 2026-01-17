from database.db_connection import get_db_connection

class BudgetModel:
    def add_budget(self, user_id, category_id, limit, month, year):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO budgets (user_id, category_id, amount_limit, month, year)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE amount_limit = %s
            """
            cursor.execute(sql, (user_id, category_id, limit, month, year, limit))
            conn.commit()
            return True
        except Exception as e:
            print(f"Błąd budżetu: {e}")
            return False
        finally:
            conn.close()

    def get_budgets_status(self, user_id, month, year):
        # Zwraca listę budżetów wraz z informacją ile już wydano (UC 6)."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Zapytanie łączące budżety z sumą transakcji w danej kategorii
        sql = """
            SELECT 
                b.budget_id, b.amount_limit, c.name as category_name,
                COALESCE(SUM(t.amount), 0) as spent_amount
            FROM budgets b
            JOIN categories c ON b.category_id = c.category_id
            LEFT JOIN transactions t ON 
                t.category_id = b.category_id 
                AND t.user_id = b.user_id 
                AND MONTH(t.transaction_date) = b.month 
                AND YEAR(t.transaction_date) = b.year
                AND t.type = 'expense'
            WHERE b.user_id = %s AND b.month = %s AND b.year = %s
            GROUP BY b.budget_id, c.name, b.amount_limit
        """
        cursor.execute(sql, (user_id, month, year))
        res = cursor.fetchall()
        conn.close()
        return res
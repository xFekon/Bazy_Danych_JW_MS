import mysql.connector
from mysql.connector import errorcode
# Importujemy konfigurację z pliku obok
from database.db_connection import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# ENUM-y (dla definicji tabel)
ACCOUNT_TYPES = ['cash', 'bank_account', 'savings', 'credit_card', 'investment']
TRANSACTION_TYPES = ['income', 'expense', 'transfer']

def create_server_connection():
    """Łączy się z serwerem MySQL bez wybierania bazy danych (do jej utworzenia)."""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except mysql.connector.Error as err:
        print(f"Błąd połączenia z serwerem MySQL: {err}")
        return None

def create_db_connection():
    """Łączy się z konkretną bazą danych (do tworzenia tabel)."""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Błąd połączenia z bazą {DB_NAME}: {err}")
        return None

def init_database():
    print("=== Rozpoczynam inicjalizację bazy danych ===")
    
    # 1. Utworzenie bazy danych
    conn = create_server_connection()
    if conn is None: return
    
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f" -> Baza danych '{DB_NAME}' jest gotowa.")
    except mysql.connector.Error as err:
        print(f"Błąd tworzenia bazy: {err}")
        return
    finally:
        cursor.close()
        conn.close()

    # 2. Utworzenie tabel
    conn = create_db_connection()
    if conn is None: return
    cursor = conn.cursor()

    # Przygotowanie stringów do ENUM w SQL
    account_enum = ', '.join([f"'{t}'" for t in ACCOUNT_TYPES])
    trx_enum = ', '.join([f"'{t}'" for t in TRANSACTION_TYPES])

    TABLES = {}
    
    TABLES['users'] = """
        CREATE TABLE `users` (
          `user_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `username` VARCHAR(100) NOT NULL UNIQUE,
          `password` VARCHAR(255) NOT NULL,
          `main_currency` VARCHAR(3) DEFAULT 'PLN',
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
    """

    TABLES['accounts'] = f"""
        CREATE TABLE `accounts` (
          `account_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` INT NOT NULL,
          `name` VARCHAR(100) NOT NULL,
          `type` ENUM({account_enum}) NOT NULL,
          `currency` VARCHAR(3) DEFAULT 'PLN',
          `current_balance` DECIMAL(12,2) DEFAULT 0.00,
          `is_active` BOOLEAN DEFAULT TRUE,
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB
    """

    TABLES['categories'] = """
        CREATE TABLE `categories` (
          `category_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` INT NULL COMMENT 'NULL dla kategorii domyślnych',
          `name` VARCHAR(100) NOT NULL,
          `type` VARCHAR(20) COMMENT 'expense / income',
          `parent_id` INT DEFAULT NULL,
          FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
          FOREIGN KEY (`parent_id`) REFERENCES `categories` (`category_id`) ON DELETE SET NULL
        ) ENGINE=InnoDB
    """

    TABLES['savings_goals'] = """
        CREATE TABLE `savings_goals` (
          `goal_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` INT NOT NULL,
          `name` VARCHAR(100) NOT NULL,
          `target_amount` DECIMAL(12,2) NOT NULL,
          `currency` VARCHAR(3) NOT NULL DEFAULT 'PLN',
          `saved_amount` DECIMAL(12,2) DEFAULT 0.00,
          `deadline_date` DATE,
          `status` VARCHAR(20) DEFAULT 'active',
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB
    """

    TABLES['budgets'] = """
        CREATE TABLE `budgets` (
          `budget_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` INT NOT NULL,
          `category_id` INT NOT NULL,
          `amount_limit` DECIMAL(12,2) NOT NULL,
          `currency` VARCHAR(3) NOT NULL DEFAULT 'PLN',
          `month` INT NOT NULL,
          `year` INT NOT NULL,
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE KEY `unique_budget` (`user_id`, `category_id`, `month`, `year`),
          FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
          FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE CASCADE
        ) ENGINE=InnoDB
    """

    TABLES['transactions'] = f"""
        CREATE TABLE `transactions` (
          `transaction_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` INT NOT NULL,
          `account_id` INT NOT NULL,
          `category_id` INT NULL,
          `goal_id` INT DEFAULT NULL,
          `type` ENUM({trx_enum}) NOT NULL,
          `amount` DECIMAL(12,2) NOT NULL,
          `transfer_to_account_id` INT DEFAULT NULL,
          `transfer_amount` DECIMAL(12,2) DEFAULT NULL,
          `exchange_rate` DECIMAL(10,4) DEFAULT NULL,
          `transaction_date` DATE NOT NULL,
          `description` TEXT,
          `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
          FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`) ON DELETE CASCADE,
          FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE SET NULL,
          FOREIGN KEY (`transfer_to_account_id`) REFERENCES `accounts` (`account_id`) ON DELETE SET NULL,
          FOREIGN KEY (`goal_id`) REFERENCES `savings_goals` (`goal_id`) ON DELETE SET NULL
        ) ENGINE=InnoDB
    """

    TABLES['recurring_payments'] = f"""
        CREATE TABLE `recurring_payments` (
          `recurring_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          `user_id` INT NOT NULL,
          `account_id` INT NOT NULL,
          `category_id` INT NULL,
          `type` ENUM({trx_enum}) NOT NULL,
          `amount` DECIMAL(12,2) NOT NULL,
          `transfer_to_account_id` INT DEFAULT NULL,
          `name` VARCHAR(100),
          `frequency` VARCHAR(20) DEFAULT 'monthly',
          `next_payment_date` DATE NOT NULL,
          `last_generated_date` DATE,
          `is_active` BOOLEAN DEFAULT TRUE,
          FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
          FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`) ON DELETE CASCADE,
          FOREIGN KEY (`transfer_to_account_id`) REFERENCES `accounts` (`account_id`) ON DELETE SET NULL,
          FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`) ON DELETE SET NULL
        ) ENGINE=InnoDB
    """

    # Kolejność tworzenia (ważna ze względu na klucze obce!)
    order = ['users', 'accounts', 'categories', 'savings_goals', 'budgets', 'transactions', 'recurring_payments']

    for name in order:
        try:
            print(f" -> Tworzę tabelę: {name}")
            cursor.execute(TABLES[name])
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"    [INFO] Tabela {name} już istnieje.")
            else:
                print(f"    [BŁĄD] Nie można utworzyć tabeli {name}: {err}")

    # 3. Seedowanie (Dodanie domyślnych kategorii, jeśli ich brak)
    try:
        cursor.execute("SELECT count(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            print(" -> Dodaję domyślne kategorie...")
            default_cats = [
                ('Jedzenie', 'expense'), 
                ('Transport', 'expense'), 
                ('Mieszkanie', 'expense'), 
                ('Rozrywka', 'expense'),
                ('Zdrowie', 'expense'),
                ('Edukacja', 'expense'),
                ('Zakupy', 'expense'),
                ('Wypłata', 'income'), 
                ('Prezent', 'income'),
                ('Inne', 'expense')
            ]
            sql = "INSERT INTO categories (name, type, user_id) VALUES (%s, %s, NULL)"
            cursor.executemany(sql, default_cats)
            conn.commit()
            print(" -> Kategorie dodane.")
    except Exception as e:
        print(f"Błąd podczas dodawania danych startowych: {e}")

    cursor.close()
    conn.close()
    print("=== Inicjalizacja zakończona pomyślnie ===")

if __name__ == "__main__":
    init_database()
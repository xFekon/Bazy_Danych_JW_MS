import mysql.connector
from mysql.connector import errorcode
from database.db_connection import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# ENUM-y
ACCOUNT_TYPES = ['cash', 'bank_account', 'savings', 'credit_card', 'investment']
TRANSACTION_TYPES = ['income', 'expense', 'transfer']

def create_server_connection():
    try:
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    except mysql.connector.Error as err:
        print(f"Błąd połączenia z serwerem: {err}")
        return None

def create_db_connection():
    try:
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    except mysql.connector.Error as err:
        print(f"Błąd połączenia z bazą: {err}")
        return None

def init_database():
    print("=== Inicjalizacja Bazy Danych (Advanced) ===")
    
    # 1. Tworzenie bazy
    conn = create_server_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.close()
    conn.close()

    # 2. Tworzenie tabel
    conn = create_db_connection()
    if not conn: return
    cursor = conn.cursor()

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
          `user_id` INT NULL,
          `name` VARCHAR(100) NOT NULL,
          `type` VARCHAR(20),
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

    for name, sql in TABLES.items():
        try:
            cursor.execute(sql)
            print(f" -> Tabela {name}: OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f" -> Tabela {name}: Już istnieje")
            else:
                print(f"Error {name}: {err}")

    # ==========================================
    # 1. WIDOK (VIEW): Użytkownicy bez haseł
    # ==========================================
    try:
        cursor.execute("DROP VIEW IF EXISTS view_public_users")
        sql_view = """
        CREATE VIEW view_public_users AS
        SELECT user_id, username, created_at, main_currency
        FROM users
        """
        cursor.execute(sql_view)
        print(" -> Widok 'view_public_users': UTWORZONO")
    except Exception as e:
        print(f"Błąd widoku: {e}")

    # ==========================================
    # 2. TRIGGER: Walidacja przed Insertem
    # ==========================================
    # Blokada dodawania transakcji dla nieaktywnych kont
    try:
        cursor.execute("DROP TRIGGER IF EXISTS before_transaction_insert")
        sql_trigger = """
        CREATE TRIGGER before_transaction_insert
        BEFORE INSERT ON transactions
        FOR EACH ROW
        BEGIN
            DECLARE acc_active BOOLEAN;
            SELECT is_active INTO acc_active FROM accounts WHERE account_id = NEW.account_id;
            
            IF acc_active = FALSE THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Nie można dodać transakcji do nieaktywnego konta!';
            END IF;
        END;
        """
        cursor.execute(sql_trigger)
        print(" -> Trigger 'before_transaction_insert': UTWORZONO")
    except Exception as e:
        print(f"Błąd triggera: {e}")

    # ==========================================
    # 3. PROCEDURA + TRANSAKCJA
    # Rejestracja usera + Domyślne Konto + Kategorie
    # ==========================================
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS register_user_complex")
        sql_proc = """
        CREATE PROCEDURE register_user_complex(
            IN p_username VARCHAR(100), 
            IN p_password VARCHAR(255)
        )
        BEGIN
            DECLARE new_user_id INT;
            
            -- Obsługa błędów SQL: w razie błędu ROLLBACK
            DECLARE EXIT HANDLER FOR SQLEXCEPTION
            BEGIN
                ROLLBACK;
                RESIGNAL;
            END;

            START TRANSACTION;
                -- 1. Dodaj Usera
                INSERT INTO users (username, password) VALUES (p_username, p_password);
                SET new_user_id = LAST_INSERT_ID();
                
                -- 2. Dodaj domyślne konto "Portfel"
                INSERT INTO accounts (user_id, name, type, current_balance) 
                VALUES (new_user_id, 'Portfel (Gotówka)', 'cash', 0.00);

                -- 3. Dodaj podstawowe kategorie
                INSERT INTO categories (user_id, name, type) VALUES 
                (new_user_id, 'Jedzenie', 'expense'),
                (new_user_id, 'Transport', 'expense'),
                (new_user_id, 'Rozrywka', 'expense'),
                (new_user_id, 'Wypłata', 'income');
                
            COMMIT;
            
            -- Zwróć ID nowego użytkownika
            SELECT new_user_id;
        END;
        """
        cursor.execute(sql_proc)
        print(" -> Procedura 'register_user_complex': UTWORZONO")
    except Exception as e:
        print(f"Błąd procedury: {e}")

    cursor.close()
    conn.close()
    print("=== Inicjalizacja zakończona ===")

if __name__ == "__main__":
    init_database()
# Bazy_Danych_JW_MS
manager finansów

Wykorzystujemy Python 3.14.2

MySQL 9.5 community serwer
MySQL Workbench
Trzeba stworzyć baze danych na swoim komputerze. Podczas konfiguracji upewnić sie że port to 3306, nadać hasło które się zapamięta np.1234 i potem uzupełnić db_config u siebie bo jest w .gitignore:

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "wydatki"
DB_PORT = 3306


w SQL
CREATE DATABASE IF NOT EXISTS wydatki;
USE wydatki;
-- tutaj wklejasz wszystkie CREATE TABLE ... z Twojego projektu

CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'silne_haslo';
GRANT SELECT, INSERT, UPDATE, DELETE ON wydatki.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;

póki co wszystko co ja robiłem, może do zmiany

Rutyna pracy:
--- start ---
git pull
--- praca ---
git add .
git commit -m "opis_zmian"
git push


żeby rozpocząć na nowo:
git clone https://...
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
--- praca ---
git add .
git commit -m "opis_zmian"
git push

test:
z głównego folderu wykonujemy:

python -m database.db_connection
powinno pokazać połączoono jeśli działa
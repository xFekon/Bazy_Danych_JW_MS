import customtkinter as ctk
from database.init_db import init_database
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from models.recurring_model import RecurringModel
from utils.session import Session

# Konfiguracja globalna
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Tracker")
        self.geometry("1100x750")
        self.minsize(800, 600)
        
        # Zmienna przechowująca aktualny widok (ramkę)
        self.current_frame = None
        
        # Inicjalizacja bazy
        init_database()
        
        # Start aplikacji od ekranu logowania
        self.show_login()

    def switch_frame(self, frame_class, **kwargs):
        """Uniwersalna funkcja do podmiany widoków"""
        # Usuń poprzedni widok, jeśli istnieje
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        # Utwórz i wyświetl nowy widok
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        # Przekazujemy self.on_login_success jako callback
        self.switch_frame(LoginWindow, on_login_success=self.on_login_success)

    def on_login_success(self):
        # Uruchom zadania w tle
        self.run_background_tasks()
        # Przełącz na główny ekran aplikacji
        self.switch_frame(MainWindow)

    def run_background_tasks(self):
        try:
            print("System: Sprawdzanie płatności cyklicznych...")
            rec_model = RecurringModel()
            rec_model.process_due_payments(Session.current_user_id)
        except Exception as e:
            print(f"Błąd zadań w tle: {e}")

    # Obsługa wylogowania (wywoływana z MainWindow)
    def show_login_logout(self):
        Session.logout()
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()
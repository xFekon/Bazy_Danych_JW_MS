import customtkinter as ctk
from tkinter import messagebox
from models.user_model import UserModel
from utils.session import Session

class LoginWindow(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.user_model = UserModel()
        
        # Tło całego ekranu logowania
        self.configure(fg_color="transparent")

        # Kontener na środku (karta logowania)
        self.card = ctk.CTkFrame(self, width=400, height=450, corner_radius=20)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Elementy wewnątrz karty
        self.setup_ui()

    def setup_ui(self):
        # Tytuł
        ctk.CTkLabel(self.card, text="Witaj!", font=("Roboto Medium", 24)).pack(pady=(40, 10))
        ctk.CTkLabel(self.card, text="Zaloguj się do Finance AI", font=("Roboto", 12), text_color="gray").pack(pady=(0, 30))

        # Pola
        self.entry_user = ctk.CTkEntry(self.card, placeholder_text="Nazwa użytkownika", width=250, height=40)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self.card, placeholder_text="Hasło", show="*", width=250, height=40)
        self.entry_pass.pack(pady=10)

        # Przyciski
        ctk.CTkButton(self.card, text="Zaloguj się", command=self.handle_login, width=250, height=40, fg_color="#2CC985", hover_color="#26AD73").pack(pady=(20, 10))
        ctk.CTkButton(self.card, text="Utwórz konto", command=self.handle_register, width=250, fg_color="transparent", border_width=1, text_color=("gray10", "gray90")).pack(pady=5)

    def handle_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        user = self.user_model.login(username, password)
        
        if user:
            Session.login(user['user_id'], user['username'])
            # Wywołujemy callback w main.py, który podmieni ten widok na Dashboard
            self.on_login_success()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowe dane logowania")

    def handle_register(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        if not username or not password:
            messagebox.showwarning("Uwaga", "Wypełnij pola")
            return
            
        if self.user_model.register(username, password):
            messagebox.showinfo("Sukces", "Konto utworzone! Możesz się zalogować.")
        else:
            messagebox.showerror("Błąd", "Użytkownik już istnieje.")
import customtkinter as ctk
from tkinter import messagebox
from models.account_model import AccountModel
from utils.session import Session

class ManageAccountsWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.title("Zarządzaj Kontami")
        self.geometry("450x600")
        self.on_close_callback = on_close_callback
        
        self.acc_model = AccountModel()
        
        # Nagłówek i przycisk dodawania
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(top_frame, text="Twoje Konta", font=("Roboto Medium", 20)).pack(side="left")
        
        ctk.CTkButton(top_frame, text="+ Dodaj", command=self.add_account_dialog, width=80, fg_color="#2CC985", hover_color="#26AD73").pack(side="right")
        
        # Scrollowalna lista
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Blokada okna głównego
        self.grab_set()
        
        self.load_accounts()

    def load_accounts(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        accounts = self.acc_model.get_accounts_by_user(Session.current_user_id)
        
        if not accounts:
            ctk.CTkLabel(self.scroll, text="Brak kont.").pack(pady=20)
            return

        for acc in accounts:
            self.create_account_row(acc)

    def create_account_row(self, acc):
        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.pack(fill="x", pady=10)
        
        # Sekcja Lewa: Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(info_frame, text=acc['name'], font=("Roboto Medium", 14)).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{acc['current_balance']:.2f} {acc['currency']}", font=("Roboto", 12), text_color="gray").pack(anchor="w")
        
        # Sekcja Prawa: Akcje
        actions_frame = ctk.CTkFrame(row, fg_color="transparent")
        actions_frame.pack(side="right", padx=5)

        # Switch Aktywne/Nieaktywne
        switch_var = ctk.BooleanVar(value=bool(acc['is_active']))
        ctk.CTkSwitch(
            actions_frame, 
            text="", 
            width=40,
            variable=switch_var, 
            progress_color="#2CC985",
            command=lambda id=acc['account_id'], var=switch_var: self.on_toggle(id, var)
        ).pack(side="left", padx=5)
        
        # Przycisk Usuń (X)
        ctk.CTkButton(
            actions_frame,
            text="Usuń",
            width=50,
            fg_color="#C0392B",
            hover_color="#A93226",
            command=lambda id=acc['account_id']: self.on_delete(id)
        ).pack(side="left", padx=5)

    def add_account_dialog(self):
        # Dialog do wprowadzania nazwy
        dialog_name = ctk.CTkInputDialog(text="Nazwa nowego konta:", title="Dodaj Konto")
        name = dialog_name.get_input()
        
        if name:
            # Dialog do wprowadzania salda
            try:
                dialog_bal = ctk.CTkInputDialog(text="Saldo początkowe (PLN):", title="Saldo")
                bal_str = dialog_bal.get_input()
                if bal_str is not None:
                    bal = float(bal_str)
                    # Domyślnie typ 'cash', można rozbudować o wybór typu
                    if self.acc_model.create_account(Session.current_user_id, name, 'cash', bal):
                        self.load_accounts()
                    else:
                        messagebox.showerror("Błąd", "Nie udało się utworzyć konta.")
            except ValueError:
                messagebox.showerror("Błąd", "Niepoprawna kwota.")

    def on_delete(self, account_id):
        confirm = messagebox.askyesno(
            "Potwierdzenie", 
            "Czy na pewno chcesz usunąć to konto?\nUWAGA: Zostaną usunięte WSZYSTKIE transakcje powiązane z tym kontem!"
        )
        if confirm:
            if self.acc_model.delete_account(account_id):
                self.load_accounts()
            else:
                messagebox.showerror("Błąd", "Nie udało się usunąć konta.")

    def on_toggle(self, account_id, var):
        new_status = var.get()
        success = self.acc_model.toggle_status(account_id, new_status)
        if not success:
            var.set(not new_status)
            messagebox.showerror("Błąd", "Nie udało się zmienić statusu.")

    def destroy(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().destroy()
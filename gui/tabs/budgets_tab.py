import customtkinter as ctk
import tkinter as tk
from datetime import date
from models.budget_model import BudgetModel
from models.category_model import CategoryModel
from utils.session import Session

class BudgetsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.budget_model = BudgetModel()
        self.cat_model = CategoryModel()
        
        self.current_month = date.today().month
        self.current_year = date.today().year
        
        # Nawigacja daty
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(nav_frame, text="<", width=40, command=self.prev_month, fg_color="gray").pack(side="left")
        self.lbl_date = ctk.CTkLabel(nav_frame, text="...", font=("Arial", 16, "bold"))
        self.lbl_date.pack(side="left", padx=20)
        ctk.CTkButton(nav_frame, text=">", width=40, command=self.next_month, fg_color="gray").pack(side="left")
        
        ctk.CTkButton(nav_frame, text="+ Nowy Budżet", command=self.add_budget_dialog).pack(side="right")

        # Scrollowalna lista budżetów
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

    def refresh(self):
        self.lbl_date.configure(text=f"{self.current_month}/{self.current_year}")
        for w in self.scroll.winfo_children(): w.destroy()
        
        data = self.budget_model.get_budgets_status(Session.current_user_id, self.current_month, self.current_year)
        if not data:
            ctk.CTkLabel(self.scroll, text="Brak budżetów na ten miesiąc.").pack(pady=20)
            return

        for b in data:
            self.create_budget_card(b)

    def create_budget_card(self, b):
        card = ctk.CTkFrame(self.scroll, corner_radius=10)
        card.pack(fill="x", pady=5)
        
        limit = float(b['amount_limit'])
        spent = float(b['spent_amount'])
        percent = (spent / limit) if limit > 0 else 0
        
        # Header
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(top, text=b['category_name'], font=("Arial", 14, "bold")).pack(side="left")
        
        # Kolor paska: Zielony -> Żółty -> Czerwony
        color = "#2CC985"
        if percent > 0.8: color = "#F1C40F"
        if percent > 1.0: color = "#C0392B"
        
        ctk.CTkLabel(top, text=f"{spent:.2f} / {limit:.2f} PLN", text_color=color).pack(side="right")
        
        # Pasek
        # CustomTkinter ProgressBar przyjmuje wartości 0.0 do 1.0
        pbar = ctk.CTkProgressBar(card, progress_color=color)
        pbar.set(min(percent, 1.0))
        pbar.pack(fill="x", padx=10, pady=(0, 15))

    def add_budget_dialog(self):
        cats = self.cat_model.get_all(Session.current_user_id)
        expense_cats = [c['name'] for c in cats if c['type'] == 'expense']
        
        dialog = ctk.CTkInputDialog(text="Podaj limit budżetu:", title="Kwota")
        limit_str = dialog.get_input()
        
        if limit_str:
            # Uproszczenie: Wybór kategorii w osobnym oknie lub input dialogu jest trudny w standardowym CTk
            # Tutaj używam prostego obejścia, w pełnej apce lepiej zrobić osobne okno Toplevel jak przy transakcjach
            # Dla demonstracji zakładam pierwszą kategorię lub proszę użytkownika w konsoli (co jest słabe w GUI).
            # Zróbmy mini okno Toplevel:
            self.open_budget_window(expense_cats, float(limit_str))

    def open_budget_window(self, cat_names, limit):
        win = ctk.CTkToplevel(self)
        win.title("Wybierz kategorię")
        win.geometry("300x200")
        
        lbl = ctk.CTkLabel(win, text="Kategoria:")
        lbl.pack(pady=10)
        
        cb = ctk.CTkComboBox(win, values=cat_names)
        cb.pack(pady=10)
        
        def save():
            cat_name = cb.get()
            # Znajdź ID (wymaga dostępu do pełnej listy obiektów, pobieram znów)
            all_cats = self.cat_model.get_all(Session.current_user_id)
            cat_id = next(c['category_id'] for c in all_cats if c['name'] == cat_name)
            self.budget_model.add_budget(Session.current_user_id, cat_id, limit, self.current_month, self.current_year)
            win.destroy()
            self.refresh()
            
        ctk.CTkButton(win, text="Zapisz", command=save).pack(pady=20)

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12; self.current_year -= 1
        else: self.current_month -= 1
        self.refresh()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1; self.current_year += 1
        else: self.current_month += 1
        self.refresh()
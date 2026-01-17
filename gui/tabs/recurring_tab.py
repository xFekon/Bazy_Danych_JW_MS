import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from models.recurring_model import RecurringModel
from models.account_model import AccountModel
from utils.session import Session

class RecurringTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.rec_model = RecurringModel()
        self.acc_model = AccountModel()
        
        # Przycisk
        self.btn_add = ctk.CTkButton(self, text="+ Nowa Płatność Cykliczna", command=self.add_dialog, fg_color="#8E44AD", hover_color="#732D91")
        self.btn_add.pack(pady=10, anchor="e", padx=20)
        
        # Stylizacja Treeview (Większa czcionka)
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        fieldbackground="#2b2b2b", 
                        foreground="white", 
                        font=("Arial", 14),   # <--- WIĘKSZA CZCIONKA
                        rowheight=40,         # <--- WYŻSZY WIERSZ
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        relief="flat", 
                        font=('Arial', 15, 'bold')) # <--- NAGŁÓWEK
        
        style.map("Treeview", background=[('selected', '#8E44AD')])

        # Tabela
        cols = ("Nazwa", "Kwota", "Konto", "Następna data", "Typ")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140) # Nieco szersze kolumny
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        data = self.rec_model.get_all(Session.current_user_id)
        for r in data:
            values = (
                r['name'], 
                f"{r['amount']:.2f} PLN", 
                r['account_name'], 
                r['next_payment_date'], 
                r['type']
            )
            self.tree.insert("", "end", values=values)

    def add_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Dodaj Płatność Cykliczną")
        win.geometry("400x450")
        win.grab_set()
        
        # Kontener formularza
        f = ctk.CTkFrame(win, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=20, pady=20)

        # Nazwa
        ctk.CTkLabel(f, text="Nazwa płatności:").pack(anchor="w")
        e_name = ctk.CTkEntry(f)
        e_name.pack(fill="x", pady=(0, 10))
        
        # Typ
        ctk.CTkLabel(f, text="Typ:").pack(anchor="w")
        type_var = ctk.StringVar(value="expense")
        seg = ctk.CTkSegmentedButton(f, values=["expense", "income"], variable=type_var)
        seg.pack(fill="x", pady=(0, 10))
        
        # Kwota
        ctk.CTkLabel(f, text="Kwota (PLN):").pack(anchor="w")
        e_amount = ctk.CTkEntry(f, placeholder_text="0.00")
        e_amount.pack(fill="x", pady=(0, 10))
        
        # Data
        ctk.CTkLabel(f, text="Data startu:").pack(anchor="w")
        # TkCalendar nie ma wersji native ctk, więc stylujemy go ciemniej
        e_date = DateEntry(f, width=12, background='darkblue', foreground='white', borderwidth=2)
        e_date.pack(pady=(0, 10))
        
        # Konto
        ctk.CTkLabel(f, text="Konto:").pack(anchor="w")
        accs = self.acc_model.get_accounts_by_user(Session.current_user_id)
        acc_names = [a['name'] for a in accs]
        cb_acc = ctk.CTkComboBox(f, values=acc_names)
        cb_acc.pack(fill="x", pady=(0, 20))
        
        def save():
            try:
                name = e_name.get()
                amt = float(e_amount.get())
                dt = e_date.get_date()
                t_type = type_var.get()
                
                sel_acc_name = cb_acc.get()
                acc_id = next((a['account_id'] for a in accs if a['name'] == sel_acc_name), None)
                
                if not acc_id: return
                
                # Uproszczenie: kategoria NULL, częstotliwość monthly
                self.rec_model.add_recurring(
                    Session.current_user_id, name, amt, acc_id, 
                    None, t_type, 'monthly', dt
                )
                win.destroy()
                self.refresh()
            except ValueError:
                pass
            
        ctk.CTkButton(f, text="Zapisz", command=save, fg_color="#8E44AD", hover_color="#732D91").pack(fill="x")
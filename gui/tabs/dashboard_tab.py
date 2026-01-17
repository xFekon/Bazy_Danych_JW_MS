import customtkinter as ctk
from tkinter import ttk
from models.account_model import AccountModel
from models.transaction_model import TransactionModel
from utils.session import Session

class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.acc_model = AccountModel()
        self.trx_model = TransactionModel()
        
        # Sekcja Net Worth (jako karta)
        self.card_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#EBEBEB", "#2B2B2B"))
        self.card_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.card_frame, text="TWÓJ MAJĄTEK", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(15, 5))
        self.lbl_nw = ctk.CTkLabel(self.card_frame, text="0.00 PLN", font=("Arial", 32, "bold"), text_color="#2CC985")
        self.lbl_nw.pack(pady=(0, 20))

        # Tabela
        ctk.CTkLabel(self, text="Ostatnie Transakcje", font=("Arial", 18, "bold")).pack(anchor="w", pady=(20, 10))
        
        # Stylizacja Treeview (Większa czcionka)
        style = ttk.Style()
        style.theme_use("clam")
        
        # Konfiguracja wierszy
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        fieldbackground="#2b2b2b", 
                        foreground="white", 
                        font=("Arial", 14),   # <--- WIĘKSZA CZCIONKA WPISÓW
                        rowheight=40,         # <--- WYŻSZY WIERSZ
                        borderwidth=0)
        
        # Konfiguracja nagłówków
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        relief="flat", 
                        font=('Arial', 15, 'bold')) # <--- WIĘKSZA CZCIONKA NAGŁÓWKÓW
        
        style.map("Treeview", background=[('selected', '#2CC985')])

        cols = ("Data", "Typ", "Kategoria", "Konto", "Kwota", "Opis")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=12)
        
        for c in cols:
            self.tree.heading(c, text=c)
            # Zwiększamy nieco szerokość kolumn
            self.tree.column(c, width=120)
            
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        nw = self.acc_model.get_net_worth(Session.current_user_id)
        self.lbl_nw.configure(text=f"{nw:,.2f} PLN")

        for i in self.tree.get_children(): self.tree.delete(i)
        for t in self.trx_model.get_recent(Session.current_user_id):
            cat = t['category_name'] if t['category_name'] else "-"
            if t['goal_name']: cat += f" (Cel: {t['goal_name']})"
            values = (t['transaction_date'], t['type'], cat, t['account_name'], f"{t['amount']:.2f}", t['description'])
            self.tree.insert("", "end", values=values)
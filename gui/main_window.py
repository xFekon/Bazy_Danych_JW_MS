import customtkinter as ctk
from tkinter import messagebox
from utils.session import Session
from models.category_model import CategoryModel
from models.account_model import AccountModel
from gui.add_transaction import AddTransactionWindow

# Import zakładek
from gui.tabs.dashboard_tab import DashboardTab
from gui.tabs.budgets_tab import BudgetsTab
from gui.tabs.goals_tab import GoalsTab
from gui.tabs.recurring_tab import RecurringTab
from gui.tabs.reports_tab import ReportsTab

class MainWindow(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill="both", expand=True)
        
        self.cat_model = CategoryModel()
        self.acc_model = AccountModel()
        
        # Konfiguracja layoutu (Grid)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()

    def setup_sidebar(self):
        # Lewy pasek
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="Finance AI", font=("Roboto Medium", 20, "bold"))
        self.lbl_logo.pack(pady=30)

        # Info o użytkowniku
        self.lbl_user = ctk.CTkButton(self.sidebar, text=f"👤 {Session.current_username}", fg_color="transparent", state="disabled", text_color=("gray10", "gray90"))
        self.lbl_user.pack(pady=(0, 20))

        # Przyciski akcji
        ctk.CTkButton(self.sidebar, text="+ Transakcja", command=self.open_trx, fg_color="#2CC985", hover_color="#26AD73").pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Nowe Konto", command=self.add_account_action, fg_color="#3B8ED0").pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Nowa Kategoria", command=self.add_category_action, fg_color="transparent", border_width=1).pack(pady=5, padx=20, fill="x")

        # Spacer
        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        # Wyloguj
        ctk.CTkButton(self.sidebar, text="Wyloguj", command=self.logout, fg_color="#C0392B", hover_color="#A93226").pack(pady=20, padx=20, fill="x")

    def setup_main_area(self):
        # Główny kontener z zakładkami
        self.tabview = ctk.CTkTabview(self, anchor="nw", command=self.on_tab_change)
        self.tabview.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # Definicja zakładek
        self.tabview.add("Pulpit")
        self.tabview.add("Raporty")
        self.tabview.add("Budżety")
        self.tabview.add("Cele")
        self.tabview.add("Cykliczne")

        # Inicjalizacja widoków wewnątrz zakładek
        self.tab_dashboard = DashboardTab(self.tabview.tab("Pulpit"))
        self.tab_dashboard.pack(fill="both", expand=True)

        self.tab_reports = ReportsTab(self.tabview.tab("Raporty"))
        self.tab_reports.pack(fill="both", expand=True)

        self.tab_budgets = BudgetsTab(self.tabview.tab("Budżety"))
        self.tab_budgets.pack(fill="both", expand=True)
        
        self.tab_goals = GoalsTab(self.tabview.tab("Cele"))
        self.tab_goals.pack(fill="both", expand=True)

        self.tab_recurring = RecurringTab(self.tabview.tab("Cykliczne"))
        self.tab_recurring.pack(fill="both", expand=True)

        # --- FIX: Wymuszenie odświeżenia pulpitu przy starcie aplikacji ---
        self.tab_dashboard.refresh()

    def on_tab_change(self):
        value = self.tabview.get()
        
        if value == "Pulpit": self.tab_dashboard.refresh()
        elif value == "Raporty": self.tab_reports.refresh()
        elif value == "Budżety": self.tab_budgets.refresh()
        elif value == "Cele": self.tab_goals.refresh()
        elif value == "Cykliczne": self.tab_recurring.refresh()

    def open_trx(self):
        if not self.acc_model.get_accounts_by_user(Session.current_user_id):
            messagebox.showwarning("Brak kont", "Najpierw dodaj konto!")
            return
        AddTransactionWindow(self, self.refresh_all)

    def refresh_all(self):
        # Odśwież aktywną zakładkę
        self.on_tab_change()

    def add_category_action(self):
        dialog = ctk.CTkInputDialog(text="Nazwa nowej kategorii:", title="Nowa Kategoria")
        name = dialog.get_input()
        if name:
            self.cat_model.add_category(Session.current_user_id, name, 'expense')
            messagebox.showinfo("OK", "Kategoria dodana")

    def add_account_action(self):
        dialog = ctk.CTkInputDialog(text="Nazwa konta:", title="Nowe Konto")
        name = dialog.get_input()
        if name:
            try:
                bal_str = ctk.CTkInputDialog(text="Saldo początkowe (PLN):", title="Saldo").get_input()
                if bal_str:
                    bal = float(bal_str)
                    self.acc_model.create_account(Session.current_user_id, name, 'cash', bal)
                    self.refresh_all()
            except ValueError:
                messagebox.showerror("Błąd", "Niepoprawna kwota")

    def logout(self):
        Session.logout()
        if hasattr(self.root, 'show_login'):
            self.root.show_login()
        else:
            self.root.quit()
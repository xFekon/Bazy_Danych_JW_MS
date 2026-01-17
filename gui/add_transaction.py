import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from models.transaction_model import TransactionModel
from models.account_model import AccountModel
from models.category_model import CategoryModel
from models.goal_model import GoalModel
from utils.session import Session

class AddTransactionWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Dodaj Transakcję")
        self.geometry("450x650")
        self.refresh_callback = refresh_callback
        
        # Modele
        self.trx_model = TransactionModel()
        self.acc_model = AccountModel()
        self.cat_model = CategoryModel()
        self.goal_model = GoalModel()
        
        self.accounts = self.acc_model.get_accounts_by_user(Session.current_user_id)
        self.categories = self.cat_model.get_all(Session.current_user_id)
        self.goals = self.goal_model.get_goals(Session.current_user_id)
        
        self.create_widgets()
        self.grab_set() # Blokada okna głównego

    def create_widgets(self):
        # Kontener
        main_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        main_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="Szczegóły Transakcji", font=("Roboto Medium", 20)).pack(pady=15)

        # Typ transakcji (Segmented Button zamiast Radio)
        self.type_var = ctk.StringVar(value="expense")
        self.seg_type = ctk.CTkSegmentedButton(
            main_frame, values=["expense", "income", "transfer"], 
            variable=self.type_var, command=self.update_ui
        )
        self.seg_type.pack(pady=10)
        self.seg_type.set("expense")

        # Konto Źródłowe
        ctk.CTkLabel(main_frame, text="Konto źródłowe:").pack(anchor="w", padx=20)
        self.cb_acc = ctk.CTkComboBox(main_frame, values=[a['name'] for a in self.accounts])
        self.cb_acc.pack(fill="x", padx=20, pady=5)

        # Kwota
        ctk.CTkLabel(main_frame, text="Kwota (PLN):").pack(anchor="w", padx=20)
        self.e_amt = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.e_amt.pack(fill="x", padx=20, pady=5)

        # Data (Zostawiamy tkcalendar bo ciężko o lepszy widget daty, ale opakowujemy)
        ctk.CTkLabel(main_frame, text="Data:").pack(anchor="w", padx=20)
        self.e_date = DateEntry(main_frame, background='darkblue', foreground='white', borderwidth=2)
        self.e_date.pack(pady=5)

        # --- Dynamiczne Pola ---
        self.frame_dynamic = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.frame_dynamic.pack(fill="x", padx=20, pady=5)
        
        self.lbl_cat = ctk.CTkLabel(self.frame_dynamic, text="Kategoria:")
        self.cb_cat = ctk.CTkComboBox(self.frame_dynamic, values=[c['name'] for c in self.categories])
        
        self.lbl_to = ctk.CTkLabel(self.frame_dynamic, text="Na konto:")
        self.cb_to = ctk.CTkComboBox(self.frame_dynamic, values=[a['name'] for a in self.accounts])
        
        self.lbl_goal = ctk.CTkLabel(self.frame_dynamic, text="Cel (Opcjonalne):")
        self.cb_goal = ctk.CTkComboBox(self.frame_dynamic, values=["- Brak -"] + [g['name'] for g in self.goals])

        # Opis
        ctk.CTkLabel(main_frame, text="Opis:").pack(anchor="w", padx=20)
        self.e_desc = ctk.CTkEntry(main_frame)
        self.e_desc.pack(fill="x", padx=20, pady=5)

        # Przycisk
        ctk.CTkButton(main_frame, text="Zapisz Transakcję", command=self.save, fg_color="#2CC985", height=40).pack(pady=30, padx=20, fill="x")

        self.update_ui(None)

    def update_ui(self, _):
        t = self.type_var.get()
        # Wyczyść widok dynamiczny
        for widget in self.frame_dynamic.winfo_children():
            widget.pack_forget()

        if t in ['expense', 'income']:
            self.lbl_cat.pack(anchor="w")
            self.cb_cat.pack(fill="x", pady=(0, 10))
            if t == 'income':
                self.lbl_goal.pack(anchor="w")
                self.cb_goal.pack(fill="x", pady=(0, 10))
        elif t == 'transfer':
            self.lbl_to.pack(anchor="w")
            self.cb_to.pack(fill="x", pady=(0, 10))
            self.lbl_goal.pack(anchor="w")
            self.cb_goal.pack(fill="x", pady=(0, 10))

    def save(self):
        try:
            amt = float(self.e_amt.get())
            acc_name = self.cb_acc.get()
            # Znajdź ID konta na podstawie nazwy (proste wyszukiwanie)
            acc_id = next((a['account_id'] for a in self.accounts if a['name'] == acc_name), None)
            
            t_type = self.type_var.get()
            cat_id, to_id, goal_id = None, None, None

            if t_type != 'transfer':
                cat_name = self.cb_cat.get()
                cat_id = next((c['category_id'] for c in self.categories if c['name'] == cat_name), None)
            else:
                to_name = self.cb_to.get()
                to_id = next((a['account_id'] for a in self.accounts if a['name'] == to_name), None)

            goal_name = self.cb_goal.get()
            if goal_name and goal_name != "- Brak -":
                goal_id = next((g['goal_id'] for g in self.goals if g['name'] == goal_name), None)

            if not acc_id: raise ValueError("Wybierz konto")

            success = self.trx_model.add_transaction(
                Session.current_user_id, acc_id, cat_id, t_type, amt, 
                self.e_date.get_date(), self.e_desc.get(), to_id, goal_id
            )
            
            if success:
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Błąd", "Błąd zapisu w bazie")
        except ValueError:
            messagebox.showerror("Błąd", "Sprawdź poprawność danych (kwota liczbowo).")
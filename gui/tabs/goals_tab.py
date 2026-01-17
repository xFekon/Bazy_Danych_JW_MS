import customtkinter as ctk
import tkinter as tk
from models.goal_model import GoalModel
from utils.session import Session

class GoalsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.model = GoalModel()
        
        # Przycisk dodawania
        self.btn_add = ctk.CTkButton(self, text="+ Nowy Cel", command=self.add_goal_dialog, fg_color="#F39C12", hover_color="#D68910")
        self.btn_add.pack(pady=10, anchor="e", padx=20)
        
        # Kontener na listę celów
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

    def refresh(self):
        # Wyczyść widok
        for w in self.scroll.winfo_children():
            w.destroy()
        
        goals = self.model.get_goals(Session.current_user_id)
        
        if not goals:
            ctk.CTkLabel(self.scroll, text="Brak zdefiniowanych celów.").pack(pady=20)
            return

        for g in goals:
            self.create_goal_card(g)

    def create_goal_card(self, goal):
        card = ctk.CTkFrame(self.scroll, corner_radius=10)
        card.pack(fill="x", pady=5, padx=10)
        
        # Obliczenia
        saved = float(goal['saved_amount'])
        target = float(goal['target_amount'])
        percent = (saved / target) if target > 0 else 0
        
        # Nagłówek karty
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(header, text=goal['name'], font=("Roboto Medium", 16)).pack(side="left")
        ctk.CTkLabel(header, text=f"{saved:,.2f} / {target:,.2f} PLN", font=("Roboto", 14), text_color="#F39C12").pack(side="right")
        
        # Pasek postępu
        pbar = ctk.CTkProgressBar(card, progress_color="#F39C12", height=12)
        pbar.set(min(percent, 1.0))
        pbar.pack(fill="x", padx=15, pady=(5, 5))
        
        # Stopka z procentem
        ctk.CTkLabel(card, text=f"Ukończono: {percent*100:.1f}%", font=("Roboto", 10), text_color="gray").pack(anchor="w", padx=15, pady=(0, 15))

    def add_goal_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Nowy Cel Oszczędnościowy")
        win.geometry("350x250")
        win.grab_set() # Blokada głównego okna
        
        ctk.CTkLabel(win, text="Nazwa celu:").pack(pady=(20, 5))
        e_name = ctk.CTkEntry(win, width=200)
        e_name.pack(pady=5)
        
        ctk.CTkLabel(win, text="Kwota docelowa (PLN):").pack(pady=(10, 5))
        e_target = ctk.CTkEntry(win, width=200, placeholder_text="0.00")
        e_target.pack(pady=5)
        
        def save():
            name = e_name.get()
            target_str = e_target.get()
            
            if name and target_str:
                try:
                    target = float(target_str)
                    self.model.add_goal(Session.current_user_id, name, target)
                    win.destroy()
                    self.refresh()
                except ValueError:
                    pass # Ignoruj błędy parsowania w prostym przykładzie
        
        ctk.CTkButton(win, text="Utwórz Cel", command=save, fg_color="#F39C12", hover_color="#D68910").pack(pady=20)
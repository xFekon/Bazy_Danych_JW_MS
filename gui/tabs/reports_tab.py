import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from models.transaction_model import TransactionModel
from models.category_model import CategoryModel
from utils.session import Session

class ReportsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.trx_model = TransactionModel()
        self.cat_model = CategoryModel()
        
        # --- Pasek filtrów (Góra) ---
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.filter_frame, text="Filtruj kategorię:", font=("Arial", 14)).pack(side="left", padx=10)
        
        self.cb_cat = ctk.CTkComboBox(self.filter_frame, command=self.on_filter_change)
        self.cb_cat.pack(side="left")
        
        # --- Wykres (Środek) ---
        self.chart_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Inicjalizacja Matplotlib
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#2b2b2b') # Tło zewnętrzne
        
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Cache kategorii
        self.categories = []

    def refresh(self):
        """Odświeża listę kategorii i domyślnie ładuje wykres wszystkich wydatków"""
        raw_cats = self.cat_model.get_all(Session.current_user_id)
        self.categories = [c for c in raw_cats if c['type'] == 'expense']
        
        cat_names = ["Wszystkie"] + [c['name'] for c in self.categories]
        self.cb_cat.configure(values=cat_names)
        self.cb_cat.set("Wszystkie")
        
        self.update_chart()

    def on_filter_change(self, choice):
        self.update_chart()

    def update_chart(self):
        # 1. Pobierz dane
        selected_name = self.cb_cat.get()
        cat_id = None
        if selected_name != "Wszystkie":
            cat_id = next((c['category_id'] for c in self.categories if c['name'] == selected_name), None)
            
        data = self.trx_model.get_monthly_expenses(Session.current_user_id, cat_id)
        
        months = [row['month_str'] for row in data]
        amounts = [float(row['total']) for row in data]
        
        # 2. Wyczyść wykres (to resetuje style!)
        self.ax.clear()
        
        # 3. [WAŻNE] Ponownie ustaw style dla Dark Mode
        self.ax.set_facecolor('#2b2b2b')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white') 
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # 4. Rysuj dane
        if not data:
            self.ax.text(0.5, 0.5, "Brak danych dla wybranych kryteriów", 
                         horizontalalignment='center', verticalalignment='center', 
                         transform=self.ax.transAxes, color='gray')
        else:
            bars = self.ax.bar(months, amounts, color='#2CC985', width=0.5)
            
            # Wartości nad słupkami
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                             f'{height:.0f}',
                             ha='center', va='bottom', color='white', fontsize=9)

            # Tytuły osi i wykresu z jawnym kolorem 'white'
            self.ax.set_ylabel("Kwota (PLN)", color='white')
            self.ax.set_title(f"Wydatki: {selected_name}", color='white')
            
            if len(months) > 3:
                self.ax.set_xticks(range(len(months)))
                self.ax.set_xticklabels(months, rotation=30, ha='right')

        self.canvas.draw()
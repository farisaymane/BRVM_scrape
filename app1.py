"""
Application GUI pour extraire les données historiques BRVM
Utilise la classe SikaSeleniumExtractor avec une interface moderne
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import threading
import os
import sys
from pathlib import Path

# Import de votre classe (assurez-vous que le fichier est dans le même répertoire)
try:
    from sika2_selenium import SikaSeleniumExtractor
except ImportError:
    print("❌ Erreur: Le fichier 'sika2_selenium.py' est requis dans le même répertoire")
    sys.exit(1)

class BRVMExtractorGUI:
    """Interface graphique pour l'extracteur de données BRVM"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("BRVM Data Extractor")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.current_data = None
        self.extraction_thread = None
        self.extractor = None
        self.is_extracting = False
        
        # Créer le dossier de téléchargement
        self.download_folder = self.create_download_folder()
        
        # Configuration du style
        self.setup_styles()
        
        # Création de l'interface
        self.create_widgets()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Données par défaut
        self.load_default_dates()
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_download_folder(self):
        """Crée le dossier de téléchargement dans le répertoire de l'application"""
        app_dir = Path(__file__).parent
        download_folder = app_dir / "BRVM_Downloads"
        
        try:
            download_folder.mkdir(exist_ok=True)
            print(f"✅ Dossier de téléchargement créé: {download_folder}")
            return download_folder
        except Exception as e:
            print(f"❌ Erreur lors de la création du dossier: {e}")
            # Utiliser le répertoire courant en cas d'erreur
            return app_dir
        
    def setup_styles(self):
        """Configuration des styles pour une interface moderne"""
        style = ttk.Style()
        
        # Thème moderne
        style.theme_use('clam')
        
        # Couleurs personnalisées
        style.configure('Title.TLabel', 
                       font=('Helvetica', 16, 'bold'),
                       foreground='#2c3e50')
        
        style.configure('Header.TLabel', 
                       font=('Helvetica', 11, 'bold'),
                       foreground='#34495e')
        
        style.configure('Success.TLabel', 
                       font=('Helvetica', 10),
                       foreground='#27ae60')
        
        style.configure('Error.TLabel', 
                       font=('Helvetica', 10),
                       foreground='#e74c3c')
        
        style.configure('Extract.TButton',
                       font=('Helvetica', 11, 'bold'))
        
        # Style pour la barre de progression
        style.configure('Success.Horizontal.TProgressbar',
                       background='#27ae60')
        
    def create_widgets(self):
        """Création de tous les widgets de l'interface"""
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === TITRE ===
        title_label = ttk.Label(main_frame, 
                               text="📊 BRVM Data Extractor", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="Extraction des données historiques des marchés financiers",
                                  font=('Helvetica', 10, 'italic'),
                                  foreground='#7f8c8d')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Affichage du dossier de téléchargement
        download_info_label = ttk.Label(main_frame, 
                                       text=f"📁 Dossier de téléchargement: {self.download_folder}",
                                       font=('Helvetica', 9),
                                       foreground='#34495e')
        download_info_label.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # === SECTION CONFIGURATION ===
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Ticker
        ttk.Label(config_frame, text="Ticker:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ticker_var = tk.StringVar()
        self.ticker_combo = ttk.Combobox(config_frame, textvariable=self.ticker_var, width=20)
        self.ticker_combo['values'] = self.get_ticker_list()
        self.ticker_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.ticker_combo.set("BOABF.bf")  # Valeur par défaut
        
        # Date de début
        ttk.Label(config_frame, text="Date de début:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(config_frame, textvariable=self.start_date_var, width=20)
        self.start_date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Date de fin
        ttk.Label(config_frame, text="Date de fin:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(config_frame, textvariable=self.end_date_var, width=20)
        self.end_date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Mode visible
        self.visible_mode_var = tk.BooleanVar()
        self.visible_mode_check = ttk.Checkbutton(config_frame, 
                                                 text="Mode visible (pour développeurs)", 
                                                 variable=self.visible_mode_var)
        self.visible_mode_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # === SECTION ACTIONS ===
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Bouton Extract
        self.extract_button = ttk.Button(actions_frame, 
                                        text="🚀 Extraire les données", 
                                        command=self.start_extraction,
                                        style='Extract.TButton')
        self.extract_button.grid(row=0, column=0, padx=(0, 10))
        
        # Bouton Save
        self.save_button = ttk.Button(actions_frame, 
                                     text="💾 Sauvegarder", 
                                     command=self.save_data,
                                     state='disabled')
        self.save_button.grid(row=0, column=1, padx=(0, 10))
        
        # Bouton Clear
        self.clear_button = ttk.Button(actions_frame, 
                                      text="🗑️ Effacer", 
                                      command=self.clear_data)
        self.clear_button.grid(row=0, column=2, padx=(0, 10))
        
        # Bouton Ouvrir dossier
        self.open_folder_button = ttk.Button(actions_frame, 
                                            text="📂 Ouvrir dossier", 
                                            command=self.open_download_folder)
        self.open_folder_button.grid(row=0, column=3, padx=(0, 10))
        
        # Bouton Arrêter
        self.stop_button = ttk.Button(actions_frame, 
                                     text="⏹️ Arrêter", 
                                     command=self.stop_extraction,
                                     state='disabled')
        self.stop_button.grid(row=0, column=4)
        
        # === SECTION PROGRESSION ===
        progress_frame = ttk.LabelFrame(main_frame, text="Progression", padding="15")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var, 
                                           maximum=100,
                                           style='Success.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Label de statut
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt à extraire")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # === SECTION RÉSULTATS ===
        results_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="15")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Info résultats
        self.results_info_var = tk.StringVar()
        self.results_info_var.set("Aucune donnée extraite")
        self.results_info_label = ttk.Label(results_frame, textvariable=self.results_info_var)
        self.results_info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Tableau des résultats
        self.create_results_table(results_frame)
        
    def create_results_table(self, parent):
        """Création du tableau des résultats avec scrollbars"""
        
        # Frame pour le tableau avec scrollbars
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview pour afficher les données
        columns = ('Date', 'Open', 'High', 'Low', 'Close', 'Volume_Titres', 'Volume_FCFA', 'Variation_Pct')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configuration des colonnes
        column_widths = {
            'Date': 100,
            'Open': 80,
            'High': 80,
            'Low': 80,
            'Close': 80,
            'Volume_Titres': 100,
            'Volume_FCFA': 120,
            'Variation_Pct': 100
        }
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths[col], anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def get_ticker_list(self):
        """Retourne la liste des tickers disponibles"""
        return [
            "BOABF.bf",    # Bank of Africa Burkina Faso
            "ECOC.bf",     # Ecobank Côte d'Ivoire
            "SDSC.bf",     # Société de Distribution de Côte d'Ivoire
            "SICC.CI",     # SICOR Côte d'Ivoire
            "BOAB.bj",     # Bank of Africa Bénin
            "CIEC.ci",     # CIE Côte d'Ivoire
            "SPHC.ci",     # SAPH Côte d'Ivoire
            "SAFC.ci",     # SAFCA Côte d'Ivoire
            "SOGC.ci",     # SOGB Côte d'Ivoire
            "TTLC.ci",     # Total Côte d'Ivoire
            "PALM.ci",     # PALMCI
            "ONTBF.bf",    # ONATEL Burkina Faso
            "BOAM.ml",     # Bank of Africa Mali
            "CBIBF.bf",    # Coris Bank Burkina Faso
            "PRSC.ci",     # PROSUMA Côte d'Ivoire
            "FTSC.ci",     # Filtisac Côte d'Ivoire
            "CABC.ci",     # CABCAO Côte d'Ivoire
            "UNXC.ci",     # UNIWAX Côte d'Ivoire
            "BICC.ci",     # BICICI Côte d'Ivoire
            "SEMC.ci",     # SEMIC Côte d'Ivoire
            "BOAN.sn",     # Bank of Africa Sénégal
            "SGBC.ci",     # SGB Côte d'Ivoire
            "NEIC.ci",     # NEI-CEDA Côte d'Ivoire
            "SLBC.ci",     # SOLIBRA Côte d'Ivoire
            "SMBC.ci",     # SMB Côte d'Ivoire
            "STBC.ci",     # SETAO Côte d'Ivoire
            "CFAC.ci",     # CFAO Côte d'Ivoire
            "SNTS.sn",     # SONATEL Sénégal
            "ORAC.ci",     # ORAGROUP Côte d'Ivoire
            "ETIT.ci",     # ETI Togo
            "BOAS.sn",     # Bank of Africa Sénégal
            "BOAC.ci",     # Bank of Africa Côte d'Ivoire
            "BOAG.gh",     # Bank of Africa Ghana
            "BOAM.ml",     # Bank of Africa Mali
            "BOAN.ne",     # Bank of Africa Niger
            "BOAT.tg",     # Bank of Africa Togo
        ]
        
    def load_default_dates(self):
        """Charge les dates par défaut"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 mois par défaut
        
        self.start_date_var.set(start_date.strftime("%Y-%m-%d"))
        self.end_date_var.set(end_date.strftime("%Y-%m-%d"))
        
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def open_download_folder(self):
        """Ouvre le dossier de téléchargement"""
        try:
            if sys.platform == "win32":
                os.startfile(self.download_folder)
            elif sys.platform == "darwin":  # macOS
                os.system(f"open '{self.download_folder}'")
            else:  # Linux
                os.system(f"xdg-open '{self.download_folder}'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier:\n{str(e)}")
        
    def validate_inputs(self):
        """Valide les entrées utilisateur"""
        ticker = self.ticker_var.get().strip()
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        
        if not ticker:
            messagebox.showerror("Erreur", "Veuillez sélectionner un ticker")
            return False
            
        if not start_date or not end_date:
            messagebox.showerror("Erreur", "Veuillez saisir les dates de début et de fin")
            return False
            
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start_dt >= end_dt:
                messagebox.showerror("Erreur", "La date de début doit être antérieure à la date de fin")
                return False
                
            if end_dt > datetime.now():
                messagebox.showerror("Erreur", "La date de fin ne peut pas être dans le futur")
                return False
                
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide. Utilisez YYYY-MM-DD")
            return False
            
        return True
        
    def start_extraction(self):
        """Démarre l'extraction dans un thread séparé"""
        if not self.validate_inputs():
            return
            
        # Désactiver les boutons pendant l'extraction
        self.extract_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_extracting = True
        
        # Réinitialiser la progression
        self.progress_var.set(0)
        self.status_var.set("Initialisation...")
        
        # Lancer l'extraction dans un thread séparé
        self.extraction_thread = threading.Thread(target=self.extract_data_thread)
        self.extraction_thread.daemon = True
        self.extraction_thread.start()
        
    def stop_extraction(self):
        """Arrête l'extraction en cours"""
        if self.is_extracting:
            self.is_extracting = False
            self.root.after(0, lambda: self.update_status("Arrêt en cours...", 0))
            
            # Fermer le navigateur si nécessaire
            if self.extractor:
                try:
                    self.extractor.close_driver()
                except:
                    pass
                    
            # Réactiver les boutons
            self.root.after(0, self.reset_buttons)
            
    def reset_buttons(self):
        """Remet les boutons dans leur état initial"""
        self.extract_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Extraction arrêtée")
        
    def extract_data_thread(self):
        """Thread d'extraction des données avec gestion automatique des périodes"""
        try:
            ticker = self.ticker_var.get().strip()
            start_date = self.start_date_var.get().strip()
            end_date = self.end_date_var.get().strip()
            headless = not self.visible_mode_var.get()
            
            if not self.is_extracting:
                return
                
            # Calculer la durée de la période
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            duration = relativedelta(end_dt, start_dt)
            
            # Calculer le nombre total de mois
            total_months = duration.years * 12 + duration.months
            
            # Créer l'extracteur
            self.extractor = SikaSeleniumExtractor(headless=headless)
            
            # Mise à jour du statut
            self.root.after(0, lambda: self.update_status("Configuration du navigateur...", 10))
            
            # Choisir la méthode d'extraction selon la durée
            if total_months <= 3:
                # Période courte : extraction directe
                self.root.after(0, lambda: self.update_status("Extraction directe en cours...", 30))
                print(f"📅 Période courte détectée ({total_months} mois) - Extraction directe")
                
                if self.is_extracting:
                    df = self.extractor.extract_data(ticker, start_date, end_date)
                else:
                    return
                    
            else:
                # Période longue : extraction par trimestres
                self.root.after(0, lambda: self.update_status(f"Extraction par périodes de 3 mois ({total_months} mois)...", 30))
                print(f"📅 Période longue détectée ({total_months} mois) - Extraction par trimestres")
                
                if self.is_extracting:
                    df = self.extractor.extract_data_by_quarters(ticker, start_date, end_date)
                else:
                    return
            
            if not self.is_extracting:
                return
                
            # Mise à jour du statut
            self.root.after(0, lambda: self.update_status("Traitement terminé", 100))
            
            # Traitement des résultats
            if not df.empty:
                self.current_data = df
                self.root.after(0, lambda: self.display_results(df))
                
                # Message de succès avec info sur la méthode utilisée
                method_used = "directe" if total_months <= 3 else "par trimestres"
                success_message = f"✅ Extraction {method_used} réussie: {len(df)} lignes"
                self.root.after(0, lambda: self.update_status_success(success_message))
            else:
                self.root.after(0, lambda: self.update_status_error("❌ Aucune donnée extraite"))
                
        except Exception as e:
            if self.is_extracting:
                self.root.after(0, lambda: self.update_status_error(f"❌ Erreur: {str(e)}"))
            
        finally:
            # Réactiver les boutons
            self.is_extracting = False
            self.root.after(0, lambda: self.extract_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            
    def update_status(self, message, progress):
        """Met à jour le statut et la progression"""
        self.status_var.set(message)
        self.progress_var.set(progress)
        
    def update_status_success(self, message):
        """Met à jour le statut avec succès"""
        self.status_var.set(message)
        self.progress_var.set(100)
        self.save_button.config(state='normal')
        
    def update_status_error(self, message):
        """Met à jour le statut avec erreur"""
        self.status_var.set(message)
        self.progress_var.set(0)
        
    def display_results(self, df):
        """Affiche les résultats dans le tableau"""
        # Effacer les résultats précédents
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Afficher les informations
        self.results_info_var.set(f"Données extraites: {len(df)} lignes | "
                                 f"Période: {df['Date'].min()} à {df['Date'].max()} | "
                                 f"Volume FCFA total: {df['Volume_FCFA'].sum():,}")
        
        # Afficher les premières 100 lignes dans le tableau
        display_df = df.head(100)  # Limiter l'affichage pour les performances
        
        for index, row in display_df.iterrows():
            values = [
                row['Date'].strftime('%Y-%m-%d') if pd.notna(row['Date']) else '',
                f"{row['Open']:.2f}" if pd.notna(row['Open']) else '',
                f"{row['High']:.2f}" if pd.notna(row['High']) else '',
                f"{row['Low']:.2f}" if pd.notna(row['Low']) else '',
                f"{row['Close']:.2f}" if pd.notna(row['Close']) else '',
                f"{row['Volume_Titres']:,}" if pd.notna(row['Volume_Titres']) else '',
                f"{row['Volume_FCFA']:,}" if pd.notna(row['Volume_FCFA']) else '',
                f"{row['Variation_Pct']:.2f}%" if pd.notna(row['Variation_Pct']) else ''
            ]
            
            self.results_tree.insert('', 'end', values=values)
            
        # Afficher un message si trop de données
        if len(df) > 100:
            messagebox.showinfo("Information", 
                              f"Seules les 100 premières lignes sont affichées.\n"
                              f"Total: {len(df)} lignes.\n"
                              f"Utilisez la sauvegarde pour obtenir toutes les données.")
            
    def save_data(self):
        """Sauvegarde les données dans le dossier de téléchargement"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Avertissement", "Aucune donnée à sauvegarder")
            return
            
        # Choisir le format de sauvegarde
        choice = messagebox.askyesnocancel("Format de sauvegarde", 
                                          "Voulez-vous sauvegarder en Excel?\n\n"
                                          "Oui = Excel (.xlsx)\n"
                                          "Non = CSV (.csv)\n"
                                          "Annuler = Annuler l'opération")
        
        if choice is None:  # Annuler
            return
            
        # Nom de fichier par défaut
        ticker = self.ticker_var.get().replace('.', '_')
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if choice:  # Excel
            filename = f"{ticker}_historique_{start_date}_{end_date}_{timestamp}.xlsx"
            file_path = self.download_folder / filename
            
            try:
                # Utiliser la méthode de sauvegarde Excel de votre classe
                if hasattr(self.extractor, 'save_to_excel'):
                    self.extractor.save_to_excel(self.current_data, ticker, str(file_path))
                else:
                    # Sauvegarde simple si la méthode n'existe pas
                    self.current_data.to_excel(str(file_path), index=False)
                
                messagebox.showinfo("Succès", f"Données sauvegardées avec succès:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
        else:  # CSV
            filename = f"{ticker}_historique_{start_date}_{end_date}_{timestamp}.csv"
            file_path = self.download_folder / filename
            
            try:
                self.current_data.to_csv(str(file_path), index=False)
                messagebox.showinfo("Succès", f"Données sauvegardées avec succès:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
    def clear_data(self):
        """Efface toutes les données et réinitialise l'interface"""
        # Effacer les résultats du tableau
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Réinitialiser les variables
        self.current_data = None
        self.results_info_var.set("Aucune donnée extraite")
        self.progress_var.set(0)
        self.status_var.set("Prêt à extraire")
        
        # Désactiver le bouton de sauvegarde
        self.save_button.config(state='disabled')
        
        print("🗑️ Données effacées")
        
    def on_closing(self):
        """Gestion de la fermeture de l'application"""
        if self.is_extracting:
            if messagebox.askokcancel("Fermeture", "Une extraction est en cours. Voulez-vous vraiment quitter ?"):
                self.stop_extraction()
                self.root.after(100, self.force_close)
        else:
            self.root.quit()
            self.root.destroy()
            
    def force_close(self):
        """Force la fermeture de l'application"""
        try:
            if self.extractor:
                self.extractor.close_driver()
        except:
            pass
        finally:
            self.root.quit()
            self.root.destroy()
            
    def show_extraction_summary(self, df):
        """Affiche un résumé détaillé de l'extraction"""
        if df.empty:
            return
            
        summary = f"""
📊 RÉSUMÉ DE L'EXTRACTION
{'='*50}
📅 Période: {df['Date'].min()} à {df['Date'].max()}
📈 Nombre de jours: {len(df)}
💰 Prix de clôture:
   • Minimum: {df['Close'].min():.2f} FCFA
   • Maximum: {df['Close'].max():.2f} FCFA
   • Moyenne: {df['Close'].mean():.2f} FCFA
   • Dernier: {df['Close'].iloc[-1]:.2f} FCFA

📊 Volumes:
   • Total FCFA: {df['Volume_FCFA'].sum():,} FCFA
   • Moyenne titres: {df['Volume_Titres'].mean():.0f}
   • Max titres: {df['Volume_Titres'].max():,}

📈 Variations:
   • Variation % moyenne: {df['Variation_Pct'].mean():.2f}%
   • Plus forte hausse: {df['Variation_Pct'].max():.2f}%
   • Plus forte baisse: {df['Variation_Pct'].min():.2f}%

🎯 Données prêtes pour analyse !
"""
        
        # Afficher dans une fenêtre popup
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Résumé de l'extraction")
        summary_window.geometry("600x500")
        summary_window.resizable(False, False)
        
        # Centrer la fenêtre
        summary_window.transient(self.root)
        summary_window.grab_set()
        
        # Texte avec scrollbar
        text_frame = ttk.Frame(summary_window, padding="20")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, summary)
        text_widget.config(state=tk.DISABLED)
        
        # Bouton fermer
        close_button = ttk.Button(summary_window, text="Fermer", 
                                 command=summary_window.destroy)
        close_button.pack(pady=10)
        
    def export_advanced_formats(self):
        """Export avancé avec plusieurs formats"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Avertissement", "Aucune donnée à exporter")
            return
        
        # Fenêtre d'export avancé
        export_window = tk.Toplevel(self.root)
        export_window.title("Export avancé")
        export_window.geometry("500x400")
        export_window.resizable(False, False)
        export_window.transient(self.root)
        export_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(export_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="📊 Export avancé des données", 
                 font=('Helvetica', 14, 'bold')).pack(pady=(0, 20))
        
        # Formats d'export
        formats_frame = ttk.LabelFrame(main_frame, text="Formats disponibles", padding="10")
        formats_frame.pack(fill=tk.X, pady=(0, 10))
        
        format_var = tk.StringVar(value="excel")
        
        ttk.Radiobutton(formats_frame, text="📊 Excel (.xlsx) - Recommandé", 
                       variable=format_var, value="excel").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(formats_frame, text="📄 CSV (.csv) - Universel", 
                       variable=format_var, value="csv").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(formats_frame, text="📋 JSON (.json) - Données brutes", 
                       variable=format_var, value="json").pack(anchor=tk.W, pady=2)
        
        # Options d'export
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        include_charts_var = tk.BooleanVar(value=True)
        include_stats_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Inclure les graphiques (Excel uniquement)", 
                       variable=include_charts_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Inclure les statistiques", 
                       variable=include_stats_var).pack(anchor=tk.W, pady=2)
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        def do_export():
            try:
                ticker = self.ticker_var.get().replace('.', '_')
                start_date = self.start_date_var.get()
                end_date = self.end_date_var.get()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                format_selected = format_var.get()
                
                if format_selected == "excel":
                    filename = f"{ticker}_complet_{start_date}_{end_date}_{timestamp}.xlsx"
                    file_path = self.download_folder / filename
                    
                    # Export Excel avancé avec graphiques et stats
                    self.export_excel_advanced(str(file_path), include_charts_var.get(), include_stats_var.get())
                    
                elif format_selected == "csv":
                    filename = f"{ticker}_data_{start_date}_{end_date}_{timestamp}.csv"
                    file_path = self.download_folder / filename
                    self.current_data.to_csv(str(file_path), index=False)
                    
                elif format_selected == "json":
                    filename = f"{ticker}_data_{start_date}_{end_date}_{timestamp}.json"
                    file_path = self.download_folder / filename
                    self.current_data.to_json(str(file_path), orient='records', date_format='iso')
                
                messagebox.showinfo("Succès", f"Export terminé:\n{file_path}")
                export_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")
        
        ttk.Button(buttons_frame, text="📤 Exporter", command=do_export).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="❌ Annuler", command=export_window.destroy).pack(side=tk.LEFT, padx=5)
        
    def export_excel_advanced(self, file_path, include_charts=True, include_stats=True):
        """Export Excel avancé avec graphiques et statistiques"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Feuille principale avec les données
                self.current_data.to_excel(writer, sheet_name='Données', index=False)
                
                if include_stats:
                    # Feuille avec les statistiques
                    stats_df = self.calculate_statistics()
                    stats_df.to_excel(writer, sheet_name='Statistiques', index=True)
                
                # Feuille avec les informations de l'extraction
                info_df = pd.DataFrame({
                    'Paramètre': ['Ticker', 'Date début', 'Date fin', 'Nombre de lignes', 
                                 'Date extraction', 'Méthode extraction'],
                    'Valeur': [self.ticker_var.get(), self.start_date_var.get(), 
                              self.end_date_var.get(), len(self.current_data),
                              datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              'Par périodes' if len(self.current_data) > 100 else 'Directe']
                })
                info_df.to_excel(writer, sheet_name='Informations', index=False)
                
        except Exception as e:
            # Fallback : sauvegarde simple si l'export avancé échoue
            self.current_data.to_excel(file_path, index=False)
            print(f"⚠️ Export simple effectué (erreur export avancé): {e}")
    
    def calculate_statistics(self):
        """Calcule les statistiques détaillées des données"""
        if self.current_data is None or self.current_data.empty:
            return pd.DataFrame()
        
        stats = {
            'Nombre de jours': len(self.current_data),
            'Prix de clôture moyen': self.current_data['Close'].mean(),
            'Prix de clôture médian': self.current_data['Close'].median(),
            'Prix minimum': self.current_data['Close'].min(),
            'Prix maximum': self.current_data['Close'].max(),
            'Écart-type prix': self.current_data['Close'].std(),
            'Volume FCFA total': self.current_data['Volume_FCFA'].sum(),
            'Volume FCFA moyen': self.current_data['Volume_FCFA'].mean(),
            'Volume titres moyen': self.current_data['Volume_Titres'].mean(),
            'Variation % moyenne': self.current_data['Variation_Pct'].mean(),
            'Variation % écart-type': self.current_data['Variation_Pct'].std(),
            'Plus forte hausse %': self.current_data['Variation_Pct'].max(),
            'Plus forte baisse %': self.current_data['Variation_Pct'].min(),
        }
        
        return pd.DataFrame(list(stats.items()), columns=['Statistique', 'Valeur'])
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.clear_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export avancé...", command=self.export_advanced_formats)
        file_menu.add_command(label="Ouvrir dossier", command=self.open_download_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Statistiques", command=self.show_statistics_window)
        tools_menu.add_command(label="Graphiques", command=self.show_charts_window)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
        
    def show_statistics_window(self):
        """Affiche une fenêtre avec les statistiques détaillées"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Avertissement", "Aucune donnée disponible")
            return
        
        # Fenêtre des statistiques
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistiques détaillées")
        stats_window.geometry("700x500")
        stats_window.resizable(True, True)
        
        # Frame avec notebook pour les onglets
        notebook = ttk.Notebook(stats_window, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Statistiques générales
        stats_frame = ttk.Frame(notebook, padding="10")
        notebook.add(stats_frame, text="Statistiques générales")
        
        stats_df = self.calculate_statistics()
        
        # Tableau des statistiques
        stats_tree = ttk.Treeview(stats_frame, columns=('Valeur',), show='tree headings')
        stats_tree.heading('#0', text='Statistique')
        stats_tree.heading('Valeur', text='Valeur')
        
        for index, row in stats_df.iterrows():
            stats_tree.insert('', 'end', text=row['Statistique'], values=(f"{row['Valeur']:.2f}",))
        
        stats_tree.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Analyse technique
        tech_frame = ttk.Frame(notebook, padding="10")
        notebook.add(tech_frame, text="Analyse technique")
        
        # Calculer des indicateurs techniques simples
        self.show_technical_analysis(tech_frame)
        
    def show_technical_analysis(self, parent):
        """Affiche une analyse technique basique"""
        try:
            # Moyennes mobiles
            ma_5 = self.current_data['Close'].rolling(window=5).mean()
            ma_20 = self.current_data['Close'].rolling(window=20).mean()
            
            # Volatilité
            volatility = self.current_data['Close'].rolling(window=20).std()
            
            # RSI simplifié (approximation)
            delta = self.current_data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # Affichage
            analysis_text = f"""
ANALYSE TECHNIQUE - {self.ticker_var.get()}
{'='*50}

📊 MOYENNES MOBILES
• MM5 actuelle: {ma_5.iloc[-1]:.2f} FCFA
• MM20 actuelle: {ma_20.iloc[-1]:.2f} FCFA
• Tendance: {'Haussière' if ma_5.iloc[-1] > ma_20.iloc[-1] else 'Baissière'}

📈 VOLATILITÉ
• Volatilité 20j: {volatility.iloc[-1]:.2f} FCFA
• Volatilité %: {(volatility.iloc[-1] / self.current_data['Close'].iloc[-1] * 100):.2f}%

⚡ RSI (14 périodes)
• RSI actuel: {rsi.iloc[-1]:.2f}
• Signal: {'Survente' if rsi.iloc[-1] < 30 else 'Surachat' if rsi.iloc[-1] > 70 else 'Neutre'}

💰 NIVEAUX CLÉS
• Support: {self.current_data['Close'].min():.2f} FCFA
• Résistance: {self.current_data['Close'].max():.2f} FCFA
• Cours actuel: {self.current_data['Close'].iloc[-1]:.2f} FCFA
"""
            
            text_widget = tk.Text(parent, wrap=tk.WORD, font=('Courier', 10))
            scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget.insert(tk.END, analysis_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            error_label = ttk.Label(parent, text=f"Erreur dans l'analyse: {str(e)}")
            error_label.pack(pady=20)
    
    def show_charts_window(self):
        """Affiche une fenêtre avec des graphiques (version simplifiée)"""
        if self.current_data is None or self.current_data.empty:
            messagebox.showwarning("Avertissement", "Aucune donnée disponible")
            return
        
        messagebox.showinfo("Graphiques", 
                           "Fonctionnalité de graphiques disponible dans la version complète.\n"
                           "Les données peuvent être exportées vers Excel pour créer des graphiques.")
    
    def show_about(self):
        """Affiche la fenêtre À propos"""
        about_text = """
🏢 BRVM Data Extractor v2.0
╔════════════════════════════════════════╗
║                                        ║
║   Extracteur de données historiques    ║
║   pour la Bourse Régionale des         ║
║   Valeurs Mobilières (BRVM)            ║
║                                        ║
║   Fonctionnalités:                     ║
║   • Extraction par périodes            ║
║   • Export multi-formats               ║
║   • Analyse statistique                ║
║   • Interface moderne                  ║
║                                        ║
║   Compatible avec tous les             ║
║   titres cotés sur la BRVM             ║
║                                        ║
╚════════════════════════════════════════╝

© 2024 - Développé avec Python & Selenium
"""
        messagebox.showinfo("À propos", about_text)


def main():
    """Fonction principale pour lancer l'application"""
    print("🚀 Lancement de BRVM Data Extractor...")
    
    # Créer la fenêtre principale
    root = tk.Tk()
    
    # Créer l'application
    app = BRVMExtractorGUI(root)
    
    # Créer la barre de menu
    app.create_menu_bar()
    
    # Lancer l'application
    print("✅ Interface graphique prête !")
    root.mainloop()


if __name__ == "__main__":
    main()
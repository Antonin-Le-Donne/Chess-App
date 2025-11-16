import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
import random
from theme_ihm import setup_theme, BASE_BG, FONT_TITLE
from selectionTemps import TimeSelectionWindow
from RulesWindow import RulesWindow
from ChessHMI import ChessHMI
from chessIHMIA import ChessHMIAI
from stockfish import Stockfish

CONFIG_FILE = "config.json"

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        setup_theme(self)
        self.configure(bg=BASE_BG)
        self.title("Chess Game - Accueil")
        self.resizable(False, False)

        # Charger les préférences sauvegardées
        self.input_mode, self.selected_skin = self.load_preferences()

        # Initialiser Stockfish
        stockfish_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")
        self.stockfish = Stockfish(path=stockfish_path)


        self.show_menu()

    def show_menu(self):
        for w in self.winfo_children():
            w.destroy()
        self.geometry("400x450")
        self.create_widgets()

    def create_widgets(self):
        container = ttk.Frame(self, padding=20)
        container.grid(sticky="nsew")
        container.columnconfigure(0, weight=1)

        ttk.Label(container, text="Bienvenue dans Chess Game",
                  font=FONT_TITLE, anchor="center")\
            .grid(row=0, column=0, pady=(0,30))

        btns = [
            ("Créer une partie", self.open_time_selection, "Accent.TButton"),
            ("Jouer contre l'IA", self.open_ai_difficulty_menu, "Accent.TButton"),
            ("Paramètres", self.open_settings, "TButton"),
            ("Règles détaillées", self.show_rules, "TButton"),
            ("Quitter", self.quit, "TButton"),
        ]
        for i, (txt, cmd, sty) in enumerate(btns, start=1):
            ttk.Button(container, text=txt, command=cmd, style=sty)\
                .grid(row=i, column=0, sticky="ew", pady=8)

    def open_time_selection(self):
        TimeSelectionWindow(self, self.launch_game)

    def launch_game(self, time_control):
        for w in self.winfo_children():
            w.destroy()

        hmi = ChessHMI(
            self,
            time_control=time_control,
            input_mode=self.input_mode,
            skin=self.selected_skin,
            on_exit_callback=self.show_menu
        )
        hmi.pack(fill="both", expand=True)

        self.update_idletasks()
        largeur = self.winfo_reqwidth()
        hauteur = self.winfo_reqheight()
        self.geometry(f"{largeur}x{hauteur}")

    def open_settings(self):
        win = tk.Toplevel(self)
        setup_theme(win)
        win.title("Paramètres")
        win.geometry("360x400")

        content = ttk.Frame(win, padding=20)
        content.pack(fill="both", expand=True)

        fields = ttk.Frame(content)
        fields.pack(fill="both", expand=True, pady=(0,20))

        # Partie: Mode de contrôle
        ttk.Label(fields, text="Mode de contrôle :", font=FONT_TITLE).pack(anchor="w", pady=(0,10))
        mode_var = tk.StringVar(value=self.input_mode)
        for txt, val in [("Click Only", "click only"),
                        ("Drag Only", "drag only"),
                        ("Click + Drag", "click and drag")]:
            ttk.Radiobutton(fields, text=txt, value=val, variable=mode_var)\
                .pack(anchor="w", pady=5)

        # Partie: Choix du skin
        ttk.Label(fields, text="Skin :", font=FONT_TITLE).pack(anchor="w", pady=(20,10))
        skin_var = tk.StringVar(value=self.selected_skin)
        for sk in ["Classique", "Coloré", "Bois"]:
            ttk.Radiobutton(fields, text=sk, value=sk, variable=skin_var)\
                .pack(anchor="w", pady=5)

        # Bouton Valider
        ttk.Button(content, text="Valider", style="Accent.TButton",
                command=lambda: self.save_settings(mode_var.get(), skin_var.get(), win))\
            .pack(pady=(10,0))

    def save_settings(self, mode_choice, skin_choice, window):
        self.input_mode = mode_choice
        self.selected_skin = skin_choice
        self.save_preferences()
        messagebox.showinfo("Paramètres", "Paramètres sauvegardés avec succès ! ")
        window.destroy()

    def show_rules(self):
        RulesWindow(self)

    def save_preferences(self):
        data = {
            "input_mode": self.input_mode,
            "selected_skin": self.selected_skin
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

    def load_preferences(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("input_mode", "click only"), data.get("selected_skin", "Classique")
        else:
            return "click only", "Classique"

    def open_ai_difficulty_menu(self):
        win = tk.Toplevel(self)
        setup_theme(win)
        win.title("Difficulté IA")
        win.geometry("320x475")

        content = ttk.Frame(win, padding=20)
        content.pack(fill="both", expand=True)

        ttk.Label(content, text="Choisissez la difficulté de l'IA :", font=FONT_TITLE).pack(pady=(0,20))

        difficulties = [
            ("Débutant (1000 Elo)", "debutant"),
            ("Facile (1500 Elo)", "facile"),
            ("Intermédiaire (1800 Elo)", "intermediaire"),
            ("Fort (2000 Elo)", "fort"),
            ("Maître (2200 Elo)", "maitre"),
            ("Grand Maître (2500 Elo)", "gmaitre"),
        ]
        diff_var = tk.StringVar(value="debutant")
        for txt, val in difficulties:
            ttk.Radiobutton(content, text=txt, value=val, variable=diff_var).pack(anchor="w", pady=5)

        # Choix de la couleur
        ttk.Label(content, text="Votre couleur :", font=FONT_TITLE).pack(pady=(20,10))
        color_var = tk.StringVar(value="blanc")
        for txt, val in [("Blancs", "blanc"), ("Noirs", "noir"), ("Aléatoire", "random")]:
            ttk.Radiobutton(content, text=txt, value=val, variable=color_var).pack(anchor="w", pady=3)

        ttk.Button(content, text="Valider", style="Accent.TButton",
                   command=lambda: self.open_time_selection_vs_ai(diff_var.get(), color_var.get(), win)).pack(pady=(20,0))

    def open_time_selection_vs_ai(self, ai_level, player_color, win):
        win.destroy()
        TimeSelectionWindow(self, lambda time_control: self.launch_game_vs_ai(time_control, ai_level, player_color))

    def launch_game_vs_ai(self, time_control, ai_level, player_color):
        for w in self.winfo_children():
            w.destroy()

        # Gestion du choix aléatoire
        if player_color == "random":
            player_color = random.choice(["blanc", "noir"])

        # Use ChessHMIAI instead of ChessHMI for AI games
        hmi = ChessHMIAI(
            self,
            time_control=time_control,
            input_mode=self.input_mode,
            skin=self.selected_skin,
            on_exit_callback=self.show_menu,
            ai_level=ai_level,
            player_color=player_color
        )
        hmi.pack(fill="both", expand=True)

        self.update_idletasks()
        largeur = self.winfo_reqwidth()
        hauteur = self.winfo_reqheight()
        self.geometry(f"{largeur}x{hauteur}")


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
from theme_ihm import setup_theme, BASE_BG, FONT_TITLE
from selectionTemps import TimeSelectionWindow
from RulesWindow import RulesWindow
from ChessHMI import ChessHMI

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
            ("Créer une partie", self.open_time_selection,   "Accent.TButton"),
            ("Paramètres",       self.open_settings,         "TButton"),
            ("Règles détaillées",self.show_rules,            "TButton"),
            ("Quitter",          self.quit,                  "TButton"),
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
        win.geometry("360x400")  # ✅ Plus grand et plus aéré

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
        messagebox.showinfo("Paramètres", "Paramètres sauvegardés avec succès ! ✅")  # ✅ Message de confirmation
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

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()

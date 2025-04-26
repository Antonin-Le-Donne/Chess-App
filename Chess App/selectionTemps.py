# selectionTemps.py

import tkinter as tk
from tkinter import ttk
from theme_ihm import setup_theme, FONT_BODY

class TimeSelectionWindow(tk.Toplevel):
    def __init__(self, parent, launch_game_callback):
        super().__init__(parent)
        setup_theme(self)
        self.title("Choix du temps de la partie")
        self.launch_game_callback = launch_game_callback
        self.selected_time_str = None

        # Titre
        ttk.Label(self, text="Choisissez un contrôle de temps prédéfini :", font=FONT_BODY).pack(pady=5)

        # Frames de choix prédéfinis
        bullet_frame = ttk.LabelFrame(self, text="Bullet")
        bullet_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(bullet_frame, text="30 sec", command=lambda: self.on_validate("Bullet - 30 sec")).pack(side="left", padx=5, pady=5)
        ttk.Button(bullet_frame, text="1 min", command=lambda: self.on_validate("Bullet - 1 min")).pack(side="left", padx=5, pady=5)
        ttk.Button(bullet_frame, text="2 min + 1", command=lambda: self.on_validate("Bullet - 2 min + 1")).pack(side="left", padx=5, pady=5)

        blitz_frame = ttk.LabelFrame(self, text="Blitz")
        blitz_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(blitz_frame, text="3 min", command=lambda: self.on_validate("Blitz - 3 min")).pack(side="left", padx=5, pady=5)
        ttk.Button(blitz_frame, text="3 min + 3", command=lambda: self.on_validate("Blitz - 3 min + 3")).pack(side="left", padx=5, pady=5)
        ttk.Button(blitz_frame, text="5 min", command=lambda: self.on_validate("Blitz - 5 min")).pack(side="left", padx=5, pady=5)

        rapide_frame = ttk.LabelFrame(self, text="Rapide")
        rapide_frame.pack(padx=10, pady=5, fill="x")
        ttk.Button(rapide_frame, text="10 min", command=lambda: self.on_validate("Rapide - 10 min")).pack(side="left", padx=5, pady=5)
        ttk.Button(rapide_frame, text="15 min + 15", command=lambda: self.on_validate("Rapide - 15 min + 15")).pack(side="left", padx=5, pady=5)
        ttk.Button(rapide_frame, text="20 min", command=lambda: self.on_validate("Rapide - 20 min")).pack(side="left", padx=5, pady=5)

        # Section personnalisée
        ttk.Label(self, text="OU bien personnalisez votre temps :", font=FONT_BODY).pack(pady=5)
        custom_frame = ttk.LabelFrame(self, text="Personnalisation")
        custom_frame.pack(padx=10, pady=5, fill="x")

        self.minutes_var = tk.DoubleVar(value=0.5)
        ttk.Label(custom_frame, text="Minutes par joueur :", font=FONT_BODY).pack()
        self.minutes_scale = ttk.Scale(
            custom_frame, from_=0.5, to=60,
            orient="horizontal", variable=self.minutes_var,
            command=self.update_custom_label
        )
        self.minutes_scale.pack(fill="x", padx=5)

        self.increment_var = tk.IntVar(value=0)
        ttk.Label(custom_frame, text="Incrément en secondes :", font=FONT_BODY).pack()
        self.increment_scale = ttk.Scale(
            custom_frame, from_=0, to=60,
            orient="horizontal", variable=self.increment_var,
            command=self.update_custom_label
        )
        self.increment_scale.pack(fill="x", padx=5)

        self.custom_time_label = ttk.Label(custom_frame, text="0.5 min + 0 s", font=FONT_BODY)
        self.custom_time_label.pack(pady=5)

        # Bouton valider
        ttk.Button(self, text="Valider", command=self.validate_custom_time).pack(pady=10)

    def update_custom_label(self, event=None):
        minutes = self.minutes_var.get()
        increment = self.increment_var.get()
        self.custom_time_label.config(text=f"{minutes} min + {increment}s")

    def validate_custom_time(self):
        minutes = self.minutes_var.get()
        increment = self.increment_var.get()
        time_control = f"Personnalisé - {minutes} min + {increment}s"
        self.on_validate(time_control)

    def on_validate(self, time_control):
        self.destroy()
        self.launch_game_callback(time_control)

# RulesWindow.py

import tkinter as tk
from tkinter import ttk
from theme_ihm import setup_theme, FONT_TITLE, BASE_BG

class RulesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        setup_theme(self)
        self.configure(bg=BASE_BG)
        self.title("Règles détaillées")
        self.geometry("1000x450")

        # Contenu des sections
        self.sections = {
            "Les mouvements des pièces": [
                "Chaque pièce se déplace selon ses propres règles :",
                "Pion : avance d'une case, ou deux cases au premier coup, capture en diagonale.",
                "Tour : se déplace en ligne droite (horizontale ou verticale) tant que le chemin est libre.",
                "Fou : se déplace en diagonale tant qu’il n’y a pas d’obstacle.",
                "Cavalier : forme en “L” (2 cases + 1 case), et peut sauter par-dessus les pièces.",
                "Reine : combine les déplacements de la tour et du fou.",
                "Roi : une case dans toutes les directions ; roque est un cas spécial."
            ],
            "Le roque": [
                "Le roque est un mouvement spécial qui implique le roi et une tour :",
                "1. Ni le roi ni la tour ne doivent avoir bougé auparavant.",
                "2. Aucune case traversée ou d’arrivée ne doit être sous attaque.",
                "3. Le roi ne doit pas être en échec sur sa case de départ.",
                "→ Le roi se déplace de deux cases vers la tour, puis la tour passe de l’autre côté."
            ],
            "En passant": [
                "La prise en passant permet à un pion de capturer un pion adverse qui, depuis sa case de départ, s’est déplacé de deux cases et se trouve à côté du pion capturant.",
                "La capture doit être effectuée immédiatement au coup suivant, sinon le droit est perdu."
            ],
            "Promotion": [
                "Lorsqu’un pion atteint la dernière rangée, il peut être promu en une autre pièce (sauf roi).",
                "Le joueur choisit entre reine, tour, fou ou cavalier selon la stratégie."
            ],
            "Échec au roi": [
                "Un roi est en échec si une pièce adverse menace directement sa case.",
                "Le joueur en échec doit immédiatement :",
                "- Déplacer le roi en dehors de la menace,",
                "- Capturer la pièce menaçante,",
                "- Ou interposer une autre pièce entre l’attaquant et le roi."
            ],
            "Échec et mat": [
                "Un roi est en échec et mat si, en plus d’être en échec, il n’existe aucun coup légal pour sortir de cet échec.",
                "La partie se termine immédiatement."
            ],
            "Les nulles": [
                "Plusieurs façons de déclarer la partie nulle :",
                "- Pat : joueur non en échec sans aucun coup légal.",
                "- Règle des 50 coups : 50 demi-coups sans déplacement de pion ni capture.",
                "- Répétition triple : même position sur l’échiquier trois fois.",
                "- Accord mutuel entre les deux joueurs.",
                "- Matériel insuffisant : impossibilité de mater l’adversaire."
            ],
            "Ouverture simple": [
                "Principes de base pour bien débuter :",
                "1. Contrôler le centre (d4, d5, e4, e5).",
                "2. Développer rapidement cavaliers et fous.",
                "3. Roquer pour sécuriser le roi.",
                "4. Ne pas déplacer plusieurs fois la même pièce en début de partie."
            ],
        }

        # Layout principal
        main = ttk.Frame(self, padding=20)
        main.grid(sticky="nsew")
        main.columnconfigure(1, weight=1)

        # Menu gauche
        menu = ttk.Frame(main, style="Menu.TFrame", width=260, padding=(10,10))
        menu.grid(row=0, column=0, sticky="ns", padx=(0,15))
        menu.grid_propagate(False)

        # Contenu droit
        self.content = ttk.Frame(main, padding=10)
        self.content.grid(row=0, column=1, sticky="nsew")

        # Boutons menu
        self.btns = {}
        for sec in self.sections:
            b = ttk.Button(menu, text=sec, style="Menu.TButton",
                           command=lambda s=sec: self.show(s))
            b.pack(fill="x", pady=6)
            self.btns[sec] = b

        # Afficher la première section
        self.show(next(iter(self.sections)))

    def show(self, section):
        # Highlight
        for s,b in self.btns.items():
            b.state(["!pressed"])
        self.btns[section].state(["pressed"])

        # Contenu
        for w in self.content.winfo_children():
            w.destroy()

        ttk.Label(self.content, text=section, font=FONT_TITLE).pack(anchor="w", pady=(0,10))
        ttk.Separator(self.content, orient="horizontal").pack(fill="x", pady=(0,15))

        for line in self.sections[section]:
            ttk.Label(self.content, text=line, wraplength=850, justify="left").pack(anchor="w", pady=4)

# game_actions.py
from __future__ import annotations
from typing import Callable, Optional, Any, Type
import tkinter as tk
from tkinter import messagebox

class GameActions:
    def __init__(
        self,
        *,
        rules: Any,
        show_message: Callable[[str, str], None],
        # Contexte UI pour les dialogues
        parent: tk.Widget,
        setup_theme_fn: Callable[[tk.Widget], None],
        base_bg: str,
        font_body,
        # Boutons pour MAJ d'état nulle
        white_draw_btn: Optional[tk.Widget] = None,
        black_draw_btn: Optional[tk.Widget] = None,
        # Dépendances pièces (pour créer les promotions sans import circulaire)
        Reine: Type[Any],
        Tour: Type[Any],
        Fou: Type[Any],
        Cavalier: Type[Any],
    ) -> None:
        self.rules = rules
        self.show_message = show_message
        self.parent = parent
        self.setup_theme_fn = setup_theme_fn
        self.base_bg = base_bg
        self.font_body = font_body
        self.white_draw_btn = white_draw_btn
        self.black_draw_btn = black_draw_btn
        self.draw_offer: Optional[str] = None

        # pièces
        self._Reine = Reine
        self._Tour = Tour
        self._Fou = Fou
        self._Cavalier = Cavalier

    # ---------- Promotion (ex-ask_promotion_choice dans l’IHM) ----------
    def ask_promotion_choice(self, couleur: str):
        win = tk.Toplevel(self.parent)
        self.setup_theme_fn(win)
        win.configure(bg=self.base_bg)
        win.title("Promotion")

        tk.Label(win, text="Choisissez une pièce :", font=self.font_body, bg=self.base_bg)\
            .pack(pady=10)

        opts = {
            "Reine":    self._Reine(couleur),
            "Tour":     self._Tour(couleur),
            "Fou":      self._Fou(couleur),
            "Cavalier": self._Cavalier(couleur),
        }

        choice = tk.StringVar(value="Reine")

        def set_choice(n):
            choice.set(n)
            win.destroy()

        frm = tk.Frame(win, bg=self.base_bg)
        frm.pack(pady=5)
        for n in opts:
            b = tk.Button(frm, text=n, command=lambda x=n: set_choice(x))
            b.pack(side="left", padx=6)

        win.wait_window()
        return opts[choice.get()]

    # ---------- Nulle ----------
    def propose_draw(self, couleur: str) -> None:
        if self.draw_offer:
            return
        self.draw_offer = couleur
        who = "Blanc" if couleur == "blanc" else "Noir"
        self.show_message(f"Nulle proposée par {who}", "blue")
        if self.white_draw_btn and self.black_draw_btn:
            if couleur == "blanc":
                self.white_draw_btn.config(state=tk.DISABLED)
                self.black_draw_btn.config(text="Accepter Nulle", state=tk.NORMAL,
                                           command=lambda: self.accept_draw("blanc"))
            else:
                self.black_draw_btn.config(state=tk.DISABLED)
                self.white_draw_btn.config(text="Accepter Nulle", state=tk.NORMAL,
                                           command=lambda: self.accept_draw("noir"))

    def accept_draw(self, proposer: str) -> None:
        if self.draw_offer == proposer:
            self.rules.game_over_callback("Match nul par accord !")

    def cancel_draw(self) -> None:
        if not self.draw_offer:
            return
        self.show_message("Proposition de nulle refusée", "red")
        self.draw_offer = None
        if self.white_draw_btn and self.black_draw_btn:
            self.white_draw_btn.config(text="Proposer Nulle", state=tk.NORMAL,
                                       command=lambda: self.propose_draw("blanc"))
            self.black_draw_btn.config(text="Proposer Nulle", state=tk.NORMAL,
                                       command=lambda: self.propose_draw("noir"))

    # ---------- Abandon ----------
    def confirm_resign(self, couleur: str) -> None:
        who = "Blanc" if couleur == "blanc" else "Noir"
        if messagebox.askyesno("Abandon", f"{who}, confirmez-vous l'abandon ?"):
            winner = "Noir" if couleur == "blanc" else "Blanc"
            self.rules.game_over_callback(f"Abandon: {winner}")

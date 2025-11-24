import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import threading
import time

from theme_ihm import setup_theme, BASE_BG, FONT_BODY
from ChessRules import ChessRules
from boardRenderer import BoardRenderer
from moveList import MoveListController
from mouvement import Movement
from analyse import AnalyseEngine


class AnalyseHMI(tk.Frame):
    """
    IHM d'analyse de positions avec Stockfish.
    Analyse en temps réel : met à jour automatiquement les évaluations
    et flèches moteur tant que la fenêtre est ouverte.
    """

    SKINS = {
        'Classique': {'light_color': 'white', 'dark_color': 'darkgray', 'piece_images_dir': 'skins/classique'},
        'Coloré': {'light_color': '#e0f7fa', 'dark_color': '#80deea', 'piece_images_dir': 'skins/colore'},
        'Bois': {'light_color': '#D2B48C', 'dark_color': '#8B5A2B', 'piece_images_dir': 'skins/bois'},
    }

    def __init__(
        self,
        parent,
        skin='Classique',
        input_mode="click only",
        analyse_engine: Optional[AnalyseEngine] = None,
        stockfish=None,
        stockfish_path: Optional[str] = None,
        on_exit_callback=None
    ):
        super().__init__(parent, bg=BASE_BG)
        self.parent = parent
        self.on_exit_callback = on_exit_callback
        setup_theme(self)

        self.rules = ChessRules()

        # Analyse Engine
        if analyse_engine is not None:
            self.analyse_engine = analyse_engine
        else:
            if stockfish is not None:
                self.analyse_engine = AnalyseEngine(stockfish_obj=stockfish)
            elif stockfish_path is not None:
                self.analyse_engine = AnalyseEngine(stockfish_path=stockfish_path)
            else:
                raise ValueError("AnalyseHMI : fournir analyse_engine, stockfish ou stockfish_path")

        self.input_mode = input_mode
        self.current_skin = self.SKINS[skin]
        self.square_size = 60
        self.margin = 20
        self.piece_images = {}
        self._load_piece_images(self.current_skin['piece_images_dir'])

        self.position_history = []
        self.history_index = -1
        self.current_analysis = None
        self.branches = []

        # Thread live analysis
        self._live_running = True
        self._live_thread = threading.Thread(target=self._live_loop, daemon=True)
        self._live_thread.start()

        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self._build_board()
        self._build_side_panel()

        self.status_label = ttk.Label(
            self,
            text="Mode analyse – position initiale",
            font=("Segoe UI", 14, "bold"),
            foreground="black",
        )
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Movement normal
        self.movement = Movement(
            rules=self.rules,
            canvas=self.board_canvas,
            square_size=self.square_size,
            margin=self.margin,
            input_mode=self.input_mode,
            update_board=self._on_user_move_board_update,
            record_move=self._on_user_move_record,
            add_increment=lambda c: None,
            show_message=self._show_message,
            on_game_over=self._on_pseudo_game_over,
            cancel_draw=lambda: None,
        )
        self.movement.bind()

        initial_fen = self._get_current_fen()
        if initial_fen:
            self._push_position(initial_fen)

    # ------------------- Chargement images -------------------
    def _load_piece_images(self, images_dir):
        self.piece_images.clear()
        base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        full = os.path.join(base, images_dir)
        for cls in ['Pion', 'Tour', 'Cavalier', 'Fou', 'Reine', 'Roi']:
            for col in ['blanc', 'noir']:
                fn = f"{col}_{cls.lower()}.png"
                path = os.path.join(full, fn)
                if os.path.exists(path):
                    img = tk.PhotoImage(file=path)
                    sw = max(1, img.width() // self.square_size)
                    sh = max(1, img.height() // self.square_size)
                    self.piece_images[(cls, col)] = img.subsample(sw, sh)

    # ------------------- Plateau -------------------
    def _build_board(self):
        self.board_frame = ttk.Frame(self, padding=10)
        self.board_frame.grid(row=0, column=0, sticky="nsew")

        self.board_canvas = tk.Canvas(self.board_frame)
        self.board_canvas.pack()

        self.renderer = BoardRenderer(
            canvas=self.board_canvas,
            rules=self.rules,
            piece_images=self.piece_images,
            skin=self.current_skin,
            square_size=self.square_size,
            margin=self.margin,
            coord_font=FONT_BODY,
            base_bg=BASE_BG,
        )
        self.renderer.build()

    # ------------------- Panneau latéral -------------------
    def _build_side_panel(self):
        self.side_frame = ttk.Frame(self, padding=10)
        self.side_frame.grid(row=0, column=1, sticky="n")

        self.moves_listbox = tk.Listbox(self.side_frame, width=24, height=15, font=FONT_BODY)
        self.moves_listbox.pack(pady=(0, 10))
        self.moves = MoveListController(self.moves_listbox)

        nav_frame = ttk.LabelFrame(self.side_frame, text="Navigation", padding=5)
        nav_frame.pack(fill="x", pady=(5, 5))
        ttk.Button(nav_frame, text="← Coup précédent", command=self.go_previous).pack(fill="x", pady=2)
        ttk.Button(nav_frame, text="Coup suivant →", command=self.go_next).pack(fill="x", pady=2)
        ttk.Button(nav_frame, text="Revenir au début", command=self.go_to_first).pack(fill="x", pady=2)

        analyse_frame = ttk.LabelFrame(self.side_frame, text="Analyse moteur", padding=5)
        analyse_frame.pack(fill="both", pady=(10, 0), expand=True)
        ttk.Button(analyse_frame, text="Analyser cette position", style="Accent.TButton", command=self.run_analysis).pack(fill="x", pady=5)
        self.eval_label = ttk.Label(analyse_frame, text="Évaluation : N/A", font=FONT_BODY)
        self.eval_label.pack(anchor="w", pady=(5, 5))
        self.branches_tree = ttk.Treeview(analyse_frame, columns=("eval", "move", "pv"), show="headings", height=5)
        self.branches_tree.heading("eval", text="Éval")
        self.branches_tree.heading("move", text="Coup")
        self.branches_tree.heading("pv", text="Ligne (PV)")
        self.branches_tree.column("eval", width=60, anchor="center")
        self.branches_tree.column("move", width=80, anchor="center")
        self.branches_tree.column("pv", width=200, anchor="w")
        self.branches_tree.pack(fill="both", expand=True, pady=(5, 0))

    # ------------------- Historique et FEN -------------------
    def _get_current_fen(self) -> Optional[str]:
        for attr in ("get_fen", "fen", "to_fen"):
            if hasattr(self.rules, attr):
                try:
                    fen = getattr(self.rules, attr)()
                    if fen:
                        return fen
                except:
                    pass
        messagebox.showerror("Erreur FEN", "Impossible d'obtenir la FEN.")
        return None

    def _set_position_from_fen(self, fen: str):
        for attr in ("set_from_fen", "load_fen", "from_fen"):
            if hasattr(self.rules, attr):
                try:
                    getattr(self.rules, attr)(fen)
                    self.renderer.redraw_position()
                    return
                except:
                    pass
        messagebox.showerror("Erreur FEN", "Impossible de charger la FEN.")

    def _push_position(self, fen: str):
        if self.history_index != len(self.position_history) - 1:
            self.position_history = self.position_history[:self.history_index + 1]
        self.position_history.append(fen)
        self.history_index = len(self.position_history) - 1

    # ------------------- Mouvement -------------------
    def _on_user_move_board_update(self):
        self.renderer.redraw_position()
        fen = self._get_current_fen()
        if fen:
            self._push_position(fen)

    def _on_user_move_record(self, notation, moved):
        self.moves.add(notation, moved)

    def _show_message(self, text, color):
        self.status_label.config(text=text, foreground=color)

    def _on_pseudo_game_over(self, reason):
        messagebox.showinfo("Info", f"Fin : {reason}")

    # ------------------- Navigation -------------------
    def go_previous(self):
        if self.history_index <= 0:
            return
        self.history_index -= 1
        self._set_position_from_fen(self.position_history[self.history_index])

    def go_next(self):
        if self.history_index >= len(self.position_history) - 1:
            return
        self.history_index += 1
        self._set_position_from_fen(self.position_history[self.history_index])

    def go_to_first(self):
        if not self.position_history:
            return
        self.history_index = 0
        self._set_position_from_fen(self.position_history[self.history_index])

    # ------------------- Analyse moteur -------------------
    def run_analysis(self):
        """Analyse manuelle (bouton)"""
        result = self.analyse_engine.analyse(self.rules, self.movement)
        self._update_analysis_display(result)

    def _update_analysis_display(self, result):
        """Met à jour l'affichage de l'évaluation et des branches"""
        if not result:
            return
        self.eval_label.config(text=f"Évaluation : {result[0]['eval_text']}")
        for item in self.branches_tree.get_children():
            self.branches_tree.delete(item)
        for br in result:
            self.branches_tree.insert("", "end", values=(br["eval_text"], br["move"], br["pv"]))

    # ------------------- Boucle d'analyse temps réel -------------------
    def _live_loop(self):
        last_fen = None
        while self._live_running:
            try:
                fen = self._get_current_fen()
                if fen and fen != last_fen:
                    last_fen = fen
                    result = self.analyse_engine.analyse(self.rules, self.movement)
                    self.after(0, lambda r=result: self._update_analysis_display(r))
            except Exception:
                pass
            time.sleep(1.0)  # rafraîchissement toutes les 1 sec

    # ------------------- Sortie -------------------
    def disable_board(self):
        if hasattr(self, "movement"):
            self.movement.unbind()

    def close(self):
        self._live_running = False
        self.disable_board()
        self.pack_forget()
        if self.on_exit_callback:
            self.on_exit_callback()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Analyse d'échecs (temps réel)")
    analyse_hmi = AnalyseHMI(
        root,
        skin="Classique",
        input_mode="click only",
        stockfish_path="stockfish.exe",
        on_exit_callback=lambda: root.destroy()
    )
    root.mainloop()

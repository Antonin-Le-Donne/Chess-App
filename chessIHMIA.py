import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from theme_ihm import setup_theme, BASE_BG, FONT_BODY
from ChessRules import ChessRules
from ChessIA import ChessIA
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

#Controlleur 
from boardRenderer import BoardRenderer
from moveList import MoveListController
from clockController import ClockController
from gameAction import GameActions
from mouvementAI import MovementAI


class ChessHMIAI(tk.Frame):
    SKINS = {
        'Classique': {'light_color': 'white',    'dark_color': 'darkgray', 'piece_images_dir': 'skins/classique'},
        'Coloré':    {'light_color': '#e0f7fa', 'dark_color': '#80deea',  'piece_images_dir': 'skins/colore'},
        'Bois':      {'light_color': '#D2B48C', 'dark_color': '#8B5A2B', 'piece_images_dir': 'skins/bois'},
    }

    def __init__(self, parent, time_control=None, input_mode="click only",
                 skin='Classique', on_exit_callback=None, ai_level="facile", player_color="blanc"):
        super().__init__(parent, bg=BASE_BG)
        self.parent = parent
        self.on_exit_callback = on_exit_callback
        setup_theme(self)

        # Règles
        self.rules = ChessRules()
        self.rules.game_over_callback = self._on_game_over
        # promotion_callback sera fixé plus bas (humain vs IA)

        # Paramètres
        self.time_control = time_control
        self.input_mode   = input_mode
        self.current_skin = self.SKINS[skin]
        self.player_color = player_color
        self.ai_color     = 'noir' if player_color == 'blanc' else 'blanc'
        self.ai_level     = ai_level

        # IA (Stockfish)
        stockfish_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")
        self.ia = ChessIA(self.ai_color, niveau=ai_level, stockfish_path=stockfish_path)

        # Plateau & skins
        self.square_size = 60
        self.margin      = 20
        self.piece_images = {}
        self._load_piece_images(self.current_skin['piece_images_dir'])

        # États
        self.game_over = False

        # Time control
        if time_control:
            self.white_time, self.increment = self._parse_time_control(time_control)
            self.black_time = self.white_time
        else:
            self.white_time = self.black_time = 0
            self.increment = 0

        # Construction IHM
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self._build_board()
        self._build_side_panel()

        # Label d'état
        self.message_label = ttk.Label(
            self, text=f"Tour des {'Blancs' if self.rules.current_turn=='blanc' else 'Noirs'}",
            font=("Segoe UI",14,"bold"), foreground="black"
        )
        self.message_label.grid(row=2, column=0, columnspan=2, pady=(10,0))

        # Actions de jeu (promotion, nulle, abandon). On ne met pas de boutons de nulle ici par défaut.
        self.actions = GameActions(
            rules=self.rules,
            show_message=self._show_message,
            parent=self,
            setup_theme_fn=setup_theme,
            base_bg=BASE_BG,
            font_body=FONT_BODY,
            white_draw_btn=None,
            black_draw_btn=None,
            Reine=Reine, Tour=Tour, Fou=Fou, Cavalier=Cavalier,
        )

        # Callback de promotion:
        # - Si couleur == IA: tente d'inférer la promotion via best move de Stockfish ; sinon, ouvre la boîte de dialogue.
        def promotion_choice(couleur: str):
            if couleur == self.ai_color:
                piece_map = {'q': Reine, 'n': Cavalier, 'b': Fou, 'r': Tour}
                # Essaye de demander à l'IA la meilleure continuation avec code de promo
                try:
                    fen = self.rules.get_fen()
                    self.ia.stockfish.set_fen_position(fen)
                    bm = self.ia.stockfish.get_best_move()
                    if bm and len(bm) == 5:  # ex "e7e8q"
                        code = bm[4].lower()
                        return piece_map.get(code, Reine)(couleur)
                except Exception:
                    pass
                return Reine(couleur)
            else:
                return self.actions.ask_promotion_choice(couleur)

        self.rules.promotion_callback = promotion_choice

        # Mouvement contrôlé par MovementAI
        def play_ai(rules):
            # ton ChessIA renvoie (start, end) en coordonnées plateau ("e2","e4")
            return self.ia.play(rules)

        self.movement = MovementAI(
            rules=self.rules,
            canvas=self.board_canvas,
            square_size=self.square_size,
            margin=self.margin,
            input_mode=self.input_mode,
            update_board=self._update_board,
            record_move=self._record_move,
            add_increment=self._add_increment,
            show_message=self._show_message,
            on_game_over=self._on_game_over,
            cancel_draw=lambda: None,  # pas de gestion de nulle par boutons ici
            player_color=self.player_color,
            play_ai=play_ai,
            ai_delay_ms=500
        )
        self.movement.bind()

        # Clock
        if time_control:
            def on_tick(w, b):
                self.white_clock_label.config(text=f"Blanc: {self._format_time(w)}")
                self.black_clock_label.config(text=f"Noir:  {self._format_time(b)}")

            def on_flag(color):
                winner = "Noir" if color == "blanc" else "Blanc"
                self.rules.game_over_callback(f"Temps: {winner}")

            self.clock = ClockController(
                rules=self.rules,
                white_time=self.white_time,
                increment=self.increment,
                on_tick=on_tick,
                on_flag=on_flag
            )
            self.clock.start(self)

        # Si c'est à l'IA de commencer
        if self.rules.current_turn == self.ai_color:
            self.after(500, self.movement._ai_play_if_needed)

    # ------------------- Chargement images -------------------
    def _load_piece_images(self, images_dir):
        self.piece_images.clear()
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(__file__)
        full = os.path.join(base, images_dir)
        for cls in ['Pion','Tour','Cavalier','Fou','Reine','Roi']:
            for col in ['blanc','noir']:
                fn = f"{col}_{cls.lower()}.png"
                path = os.path.join(full, fn)
                if os.path.exists(path):
                    img = tk.PhotoImage(file=path)
                    sw = max(1, img.width()  // self.square_size)
                    sh = max(1, img.height() // self.square_size)
                    self.piece_images[(cls, col)] = img.subsample(sw, sh)

    # ------------------- Plateau -------------------
    def _build_board(self):
        self.board_frame = ttk.Frame(self, padding=10)
        self.board_frame.grid(row=0, column=0, sticky="nsew")

        # Canvas; dessin délégué au renderer
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

        self.moves_listbox = tk.Listbox(
            self.side_frame, width=24, height=15, font=FONT_BODY
        )
        self.moves_listbox.pack(pady=(0,10))

        self.black_clock_label = ttk.Label(
            self.side_frame,
            text=f"Noir: {self._format_time(self.black_time)}" if self.time_control else "Noir: N/A",
            font=FONT_BODY
        ); self.black_clock_label.pack(pady=5)

        self.white_clock_label = ttk.Label(
            self.side_frame,
            text=f"Blanc: {self._format_time(self.white_time)}" if self.time_control else "Blanc: N/A",
            font=FONT_BODY
        ); self.white_clock_label.pack(pady=5)

        # Bouton d'abandon pour le joueur humain
        button_frame = ttk.Frame(self.side_frame); button_frame.pack(fill="x", pady=(10,0))
        ttk.Button(
            button_frame,
            text=f"Abandon {self.player_color.capitalize()}",
            command=lambda: self._confirm_resign(self.player_color),
            style="Accent.TButton"
        ).pack(side="left", expand=True)

        # Contrôleur liste de coups
        self.moves = MoveListController(self.moves_listbox)

    # ------------------- Hooks appelés par Movement/MovementAI -------------------
    def _update_board(self):
        self.renderer.redraw_position()

    def _record_move(self, notation, moved):
        self.moves.add(notation, moved)

    def _add_increment(self, couleur):
        if hasattr(self, "clock"):
            self.clock.add_increment(couleur)

    def _show_message(self, text, color):
        self.message_label.config(text=text, foreground=color)

    # ------------------- Actions non-mouvement -------------------
    def _confirm_resign(self, couleur):
        who = "Blanc" if couleur=='blanc' else "Noir"
        if messagebox.askyesno("Abandon", f"{who}, confirmez-vous l'abandon ?"):
            winner = "Noir" if couleur=='blanc' else "Blanc"
            self.rules.game_over_callback(f"Abandon: {winner}")

    # ------------------- Utilitaires généraux -------------------
    def _parse_time_control(self, tc):
        try:
            if '-' in tc:
                _, s = tc.split('-', 1)
            else:
                s = tc
            if '+' in s:
                m, inc = s.split('+', 1)
            else:
                m, inc = s, "0"
            mv = float(m.strip().split()[0])
            if 'min' in m:
                mv *= 60
            iv = ''.join(ch for ch in inc if ch.isdigit() or ch == '.')
            return int(mv), int(float(iv)) if iv else 0
        except:
            return 0, 0

    def _format_time(self, sec):
        return f"{sec//60:02d}:{sec%60:02d}"

    def _on_game_over(self, reason):
        messagebox.showinfo("Fin de partie", reason)
        self.disable_board()
        self.game_over = True
        self.pack_forget()
        if self.on_exit_callback:
            self.on_exit_callback()

    def disable_board(self):
        if hasattr(self, "movement"):
            self.movement.unbind()
        if hasattr(self, "clock"):
            self.clock.stop()


if __name__ == "__main__":
    root = tk.Tk()
    hmi = ChessHMIAI(
        root,
        time_control="Blitz - 3 min",
        input_mode="click and drag",
        skin="Classique",
        on_exit_callback=root.destroy,
        ai_level="intermediaire",
        player_color="blanc"
    )
    root.mainloop()

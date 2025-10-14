import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from theme_ihm import setup_theme, BASE_BG, FONT_BODY
from ChessRules import ChessRules
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

# Contrôleurs
from boardRenderer import BoardRenderer
from moveList import MoveListController
from clockController import ClockController
from gameAction import GameActions
from mouvement import Movement


class ChessHMI(tk.Frame):
    SKINS = {
        'Classique': {'light_color': 'white',    'dark_color': 'darkgray', 'piece_images_dir': 'skins/classique'},
        'Coloré':    {'light_color': '#e0f7fa', 'dark_color': '#80deea',  'piece_images_dir': 'skins/colore'},
        'Bois':      {'light_color': '#D2B48C', 'dark_color': '#8B5A2B', 'piece_images_dir': 'skins/bois'},
    }

    def __init__(self, parent, time_control=None, input_mode="click only",
                 skin='Classique', on_exit_callback=None):
        super().__init__(parent, bg=BASE_BG)
        self.parent = parent
        self.on_exit_callback = on_exit_callback
        setup_theme(self)

        # Règles
        self.rules = ChessRules()
        self.rules.game_over_callback = self._on_game_over
        # promotion_callback sera branché plus bas sur GameActions

        # Paramètres
        self.time_control = time_control
        self.input_mode   = input_mode
        self.current_skin = self.SKINS[skin]

        # Plateau & skins
        self.square_size = 60
        self.margin      = 20
        self.piece_images = {}
        self._load_piece_images(self.current_skin['piece_images_dir'])

        # États de partie
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
            self, text="Tour des Blancs", font=("Segoe UI",14,"bold"), foreground="black"
        )
        self.message_label.grid(row=2, column=0, columnspan=2, pady=(10,0))

        # Mouvement (JvJ)
        self.movement = Movement(
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
            cancel_draw=self._cancel_draw
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

        # Canvas uniquement ici (le dessin est délégué au BoardRenderer)
        self.board_canvas = tk.Canvas(self.board_frame)
        self.board_canvas.pack()

        # Renderer pour tout le dessin
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

        f1 = ttk.Frame(self.side_frame); f1.pack(fill="x", pady=(10,0))
        ttk.Button(f1, text="Abandon Blanc",
                   command=lambda: self._confirm_resign('blanc'),
                   style="Accent.TButton").pack(side="left", expand=True)
        self.white_draw_btn = ttk.Button(
            f1, text="Proposer Nulle",
            style="TButton"
        ); self.white_draw_btn.pack(side="left", expand=True)

        f2 = ttk.Frame(self.side_frame); f2.pack(fill="x", pady=(5,0))
        ttk.Button(f2, text="Abandon Noir",
                   command=lambda: self._confirm_resign('noir'),
                   style="Accent.TButton").pack(side="left", expand=True)
        self.black_draw_btn = ttk.Button(
            f2, text="Proposer Nulle",
            style="TButton"
        ); self.black_draw_btn.pack(side="left", expand=True)

        # Contrôleurs annexes
        self.moves = MoveListController(self.moves_listbox)
        self.actions = GameActions(
            rules=self.rules,
            show_message=self._show_message,
            parent=self,                    # parent pour Toplevel de promotion
            setup_theme_fn=setup_theme,
            base_bg=BASE_BG,
            font_body=FONT_BODY,
            white_draw_btn=self.white_draw_btn,
            black_draw_btn=self.black_draw_btn,
            Reine=Reine, Tour=Tour, Fou=Fou, Cavalier=Cavalier,
        )
        # Brancher le callback de promotion ici (après creation de actions)
        self.rules.promotion_callback = self.actions.ask_promotion_choice

        # Raccorder les boutons aux actions (au lieu des versions internes)
        self.white_draw_btn.config(command=lambda: self.actions.propose_draw('blanc'))
        self.black_draw_btn.config(command=lambda: self.actions.propose_draw('noir'))

    # ------------------- Hooks appelés par Movement -------------------
    def _update_board(self):
        self.renderer.redraw_position()

    def _record_move(self, notation, moved):
        self.moves.add(notation, moved)

    def _add_increment(self, couleur):
        if hasattr(self, "clock"):
            self.clock.add_increment(couleur)

    def _show_message(self, text, color):
        self.message_label.config(text=text, foreground=color)

    def _cancel_draw(self):
        self.actions.cancel_draw()

    # ------------------- Actions non-mouvement -------------------
    def _propose_draw(self, couleur):
        self.actions.propose_draw(couleur)

    def _accept_draw(self, proposer):
        self.actions.accept_draw(proposer)

    def _confirm_resign(self, couleur):
        self.actions.confirm_resign(couleur)

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


if __name__=="__main__":
    root = tk.Tk()
    hmi = ChessHMI(
        root,
        time_control="Blitz - 3 min",
        input_mode="click and drag",
        skin="Classique",
        on_exit_callback=lambda: root.destroy()
    )
    root.mainloop()

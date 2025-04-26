import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from theme_ihm import setup_theme, BASE_BG, FONT_BODY
from ChessRules import ChessRules
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

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

        # Initialisation des règles
        self.rules = ChessRules()
        self.rules.game_over_callback = self._on_game_over
        self.rules.promotion_callback   = self.ask_promotion_choice

        # Paramètres
        self.time_control = time_control
        self.input_mode   = input_mode
        self.current_skin = self.SKINS[skin]

        # Plateau et skins
        self.square_size = 60
        self.margin      = 20
        self.piece_images = {}
        self._load_piece_images(self.current_skin['piece_images_dir'])

        # États du jeu
        self.selected_piece = None
        self.dragging       = False
        self.game_over      = False
        self.draw_offer     = None
        self.move_number    = 1
        self.moves_list     = []

        # Temps
        if time_control:
            self.white_time, self.increment = self._parse_time_control(time_control)
            self.black_time = self.white_time
        else:
            self.white_time = self.black_time = 0
            self.increment = 0

        # Construction de l’IHM
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self._build_board()
        self._build_side_panel()

        # Label d’état
        self.message_label = ttk.Label(
            self, text="Tour des Blancs", font=("Segoe UI",14,"bold"), foreground="black"
        )
        self.message_label.grid(row=2, column=0, columnspan=2, pady=(10,0))

        if time_control:
            self._update_timer()


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



    def _build_board(self):
        self.board_frame = ttk.Frame(self, padding=10)
        self.board_frame.grid(row=0, column=0, sticky="nsew")
        size = self.square_size * 8
        cw = size + 2 * self.margin
        self.board_canvas = tk.Canvas(
            self.board_frame, width=cw, height=cw,
            bg=BASE_BG, highlightthickness=0
        )
        self.board_canvas.pack()
        self.buttons = {}
        for r in range(8):
            for c in range(8):
                coord = self.rules.plateau.notation_lettre((r, c))
                piece = self.rules.plateau[coord]
                color = (
                    self.current_skin['light_color']
                    if (r + c) % 2 == 0
                    else self.current_skin['dark_color']
                )
                btn = tk.Button(
                    self.board_canvas, bg=color,
                    width=self.square_size, height=self.square_size,
                    relief='flat'
                )
                btn.coord = coord
                if piece:
                    key = (piece.__class__.__name__, piece.couleur)
                    img = self.piece_images.get(key)
                    if img:
                        btn.config(image=img, text='')
                        btn.image = img
                    else:
                        btn.config(text=str(piece), font=("Segoe UI",16))
                if "click" in self.input_mode:
                    btn.config(command=lambda c=coord: self._on_click(c))
                if "drag" in self.input_mode:
                    btn.bind("<ButtonPress-1>",   self._on_press)
                    btn.bind("<B1-Motion>",       self._on_drag)
                    btn.bind("<ButtonRelease-1>", self._on_release)
                x = self.margin + c*self.square_size + self.square_size/2
                y = self.margin + r*self.square_size + self.square_size/2
                self.board_canvas.create_window(
                    x, y, window=btn,
                    width=self.square_size, height=self.square_size
                )
                self.buttons[coord] = btn
        half = self.margin // 2
        for i in range(8):
            x  = self.margin + i*self.square_size + self.square_size/2
            y  = self.margin + 8*self.square_size + half
            x2 = half
            y2 = self.margin + i*self.square_size + self.square_size/2
            self.board_canvas.create_text(x,  y,  text=chr(ord('a')+i), font=FONT_BODY)
            self.board_canvas.create_text(x2, y2, text=str(8-i),       font=FONT_BODY)


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
        )
        self.black_clock_label.pack(pady=5)
        self.white_clock_label = ttk.Label(
            self.side_frame,
            text=f"Blanc: {self._format_time(self.white_time)}" if self.time_control else "Blanc: N/A",
            font=FONT_BODY
        )
        self.white_clock_label.pack(pady=5)

        f1 = ttk.Frame(self.side_frame); f1.pack(fill="x", pady=(10,0))
        ttk.Button(f1, text="Abandon Blanc",
                   command=lambda: self._confirm_resign('blanc'),
                   style="Accent.TButton").pack(side="left", expand=True)
        self.white_draw_btn = ttk.Button(
            f1, text="Proposer Nulle",
            command=lambda: self._propose_draw('blanc'),
            style="TButton"
        )
        self.white_draw_btn.pack(side="left", expand=True)

        f2 = ttk.Frame(self.side_frame); f2.pack(fill="x", pady=(5,0))
        ttk.Button(f2, text="Abandon Noir",
                   command=lambda: self._confirm_resign('noir'),
                   style="Accent.TButton").pack(side="left", expand=True)
        self.black_draw_btn = ttk.Button(
            f2, text="Proposer Nulle",
            command=lambda: self._propose_draw('noir'),
            style="TButton"
        )
        self.black_draw_btn.pack(side="left", expand=True)


    def _on_click(self, coord):
        if not self.selected_piece:
            piece = self.rules.plateau[coord]
            if piece and piece.couleur == self.rules.current_turn:
                self.selected_piece = coord
            return

        start  = self.selected_piece
        piece  = self.rules.plateau[start]
        target = self.rules.plateau[coord]
        was_capture = bool(target and target.couleur != piece.couleur)
        moved = piece.couleur

        if self.rules.is_valid_move(piece, start, coord):
            self._cancel_draw()

            # Laisse ChessRules.execute_move gérer TOUTES les nulles
            self.rules.execute_move(piece, start, coord)
            self.rules.update_repetition()
            if self.rules.game_over:
                return

            # Mise à jour IHM
            self._update_board()

            # Notation promotion
            if isinstance(piece, Pion) and coord[1] in ('1','8'):
                prom = self.rules.plateau[coord]
                notation = f"{coord}={self.get_piece_letter(prom)}"
            else:
                notation = self.generate_move_notation(piece, start, coord, was_capture)

            self._record_move(notation, moved)
            self._add_increment(moved)

            # Check/checkmate/stalemate
            if self.rules.is_checkmate(self.rules.current_turn):
                winner = "Noir" if self.rules.current_turn=='blanc' else "Blanc"
                self._on_game_over(f"Échec et mat ! {winner} gagne !")
                return
            if self.rules.is_stalemate(self.rules.current_turn):
                self._on_game_over("Pat ! Match nul !")
                return
            if self.rules.is_in_check(self.rules.current_turn):
                self._show_message(f"Échec à {self.rules.current_turn}", "orange")
            else:
                self._show_message(f"Tour des {self.rules.current_turn}", "black")
        else:
            self._show_message("Coup invalide", "red")
            self.after(3000, lambda: self._show_message(f"Tour des {self.rules.current_turn}", "black"))

        self.selected_piece = None


    def _on_press(self, event):
        coord = getattr(event.widget, 'coord', None)
        if coord and self.rules.plateau[coord].couleur == self.rules.current_turn:
            self.selected_piece = coord
            self.dragging = False
        else:
            self.selected_piece = None

    def _on_drag(self, event):
        self.dragging = True

    def _on_release(self, event):
        if not self.dragging:
            coord = getattr(event.widget, 'coord', None)
            if coord:
                self._on_click(coord)
        else:
            dest = None
            for coord_, btn in self.buttons.items():
                x1, y1 = btn.winfo_rootx(), btn.winfo_rooty()
                x2, y2 = x1+btn.winfo_width(), y1+btn.winfo_height()
                if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                    dest = coord_; break
            if dest and self.selected_piece:
                self._on_click(dest)
        self.selected_piece = None
        self.dragging = False


    def _update_board(self):
        for coord, btn in self.buttons.items():
            p = self.rules.plateau[coord]
            if p:
                key = (p.__class__.__name__, p.couleur)
                img = self.piece_images.get(key)
                if img:
                    btn.config(image=img, text='')
                    btn.image = img
                else:
                    btn.config(text=str(p), image='')
            else:
                btn.config(text='', image='')


    def _record_move(self, notation, moved):
        if moved == 'blanc':
            line = f"{self.move_number}. {notation}"
            self.moves_list.append(line)
            self.moves_listbox.insert(tk.END, line)
        else:
            if not self.moves_list:
                line = f"1. {notation}"
                self.moves_list.append(line)
                self.moves_listbox.insert(tk.END, line)
                self.move_number = 2
                return
            old = self.moves_list[-1]
            new = old + f" {notation}"
            self.moves_list[-1] = new
            idx = self.moves_listbox.size() - 1
            self.moves_listbox.delete(idx)
            self.moves_listbox.insert(idx, new)
            self.move_number += 1


    def _add_increment(self, couleur):
        if self.increment > 0:
            if couleur == 'blanc':
                self.white_time += self.increment
            else:
                self.black_time += self.increment


    def _show_message(self, text, color):
        self.message_label.config(text=text, foreground=color)


    def _cancel_draw(self):
        if self.draw_offer:
            self._show_message("Proposition de nulle refusée", "red")
            self.draw_offer = None
            self.white_draw_btn.config(text="Proposer Nulle", state=tk.NORMAL,
                                       command=lambda: self._propose_draw('blanc'))
            self.black_draw_btn.config(text="Proposer Nulle", state=tk.NORMAL,
                                       command=lambda: self._propose_draw('noir'))


    def _propose_draw(self, couleur):
        if self.draw_offer: return
        self.draw_offer = couleur
        who = "Blanc" if couleur=='blanc' else "Noir"
        self._show_message(f"Nulle proposée par {who}", "blue")
        if couleur=='blanc':
            self.white_draw_btn.config(state=tk.DISABLED)
            self.black_draw_btn.config(text="Accepter Nulle", state=tk.NORMAL,
                                       command=lambda:self._accept_draw('blanc'))
        else:
            self.black_draw_btn.config(state=tk.DISABLED)
            self.white_draw_btn.config(text="Accepter Nulle", state=tk.NORMAL,
                                       command=lambda:self._accept_draw('noir'))


    def _accept_draw(self, proposer):
        if self.draw_offer == proposer:
            self.rules.game_over_callback("Match nul par accord !")


    def _confirm_resign(self, couleur):
        who = "Blanc" if couleur=='blanc' else "Noir"
        if messagebox.askyesno("Abandon", f"{who}, confirmez-vous l'abandon ?"):
            winner = "Noir" if couleur=='blanc' else "Blanc"
            self.rules.game_over_callback(f"Abandon: {winner}")


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


    def _update_timer(self):
        if self.game_over: return
        ct = self.rules.current_turn
        if ct == 'blanc':
            self.white_time -= 1
            if self.white_time <= 0:
                self.rules.game_over_callback("Temps: Noir")
                return
        else:
            self.black_time -= 1
            if self.black_time <= 0:
                self.rules.game_over_callback("Temps: Blanc")
                return
        self.white_clock_label.config(text=f"Blanc: {self._format_time(self.white_time)}")
        self.black_clock_label.config(text=f"Noir:  {self._format_time(self.black_time)}")
        self.after(1000, self._update_timer)


    def ask_promotion_choice(self, couleur):
        win = tk.Toplevel(self)
        setup_theme(win)
        win.configure(bg=BASE_BG)
        win.title("Promotion")
        ttk.Label(win, text="Choisissez une pièce :", font=FONT_BODY).pack(pady=10)
        opts = {
            "Reine":    Reine(couleur),
            "Tour":     Tour(couleur),
            "Fou":      Fou(couleur),
            "Cavalier": Cavalier(couleur),
        }
        choice = tk.StringVar(value="Reine")
        def set_choice(n):
            choice.set(n)
            win.destroy()
        frm = ttk.Frame(win, padding=5)
        frm.pack()
        for n in opts:
            ttk.Button(frm, text=n, command=lambda x=n: set_choice(x), style="Accent.TButton")\
                .pack(side="left", padx=5)
        win.wait_window()
        return opts[choice.get()]


    def generate_move_notation(self, piece, start, end, was_capture=False):
        if isinstance(piece, Roi):
            sf, ef = ord(start[0]) - ord('a'), ord(end[0]) - ord('a')
            if abs(ef - sf) == 2:
                return "O-O" if ef>sf else "O-O-O"
        if isinstance(piece, Pion) and end[1] in ('1','8'):
            return f"{end}={self.get_piece_letter(piece)}"
        if isinstance(piece, Pion):
            return f"{start[0]}x{end}" if start[0]!=end[0] else end
        lett = self.get_piece_letter(piece)
        cap  = "x" if was_capture else ""
        dis  = self.get_disambiguation(piece, start, end)
        return f"{lett}{dis}{cap}{end}"


    def get_piece_letter(self, piece):
        if isinstance(piece, Roi):      return "R"
        if isinstance(piece, Reine):    return "D"
        if isinstance(piece, Tour):     return "T"
        if isinstance(piece, Fou):      return "F"
        if isinstance(piece, Cavalier): return "C"
        return "?"


    def get_disambiguation(self, piece, start, end):
        cands = [
            c for c,p in self.rules.plateau.items()
            if type(p)==type(piece)
               and p.couleur==piece.couleur
               and c!=start
               and self.rules.is_legal(p, c, end)
        ]
        if not cands: return ""
        if any(c[0]!=start[0] for c in cands): return start[0]
        return start[1]


    def _on_game_over(self, reason):
        messagebox.showinfo("Fin de partie", reason)
        self.disable_board()
        self.game_over = True
        self.pack_forget()
        if self.on_exit_callback:
            self.on_exit_callback()


    def disable_board(self):
        for b in self.buttons.values():
            b.config(state=tk.DISABLED)


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

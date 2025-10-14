# movement.py — contrôleur des mouvements & notations (JvJ 1v1)
from __future__ import annotations
import tkinter as tk
from typing import Optional, Dict, Any, Tuple, List, Callable

# Pièces (pour isinstance / lettres)
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

Coord = str  # "e4", "a1", ...

class Movement:
    """Gère les interactions plateau (clic/drag), flèches & surlignages (clic droit),
    validation/exécution des coups et génération de la notation SAN pour un mode JvJ 1v1.

    Cette classe extrait tout ce qui est lié au *mouvement et au canvas* depuis ChessHMI.
    Elle appelle des callbacks (hooks) fournis par l'IHM pour :
      - update_board() : redessiner le plateau après un coup
      - record_move(notation:str, couleur:str)
      - add_increment(couleur:str)
      - show_message(texte:str, couleur_css:str)
      - on_game_over(raison:str)
      - cancel_draw() : annuler une proposition de nulle si active
    """

    def __init__(
        self,
        *,
        rules: Any,
        canvas: tk.Canvas,
        square_size: int,
        margin: int,
        input_mode: str = "click only",
        update_board: Optional[Callable[[], None]] = None,
        record_move: Optional[Callable[[str, str], None]] = None,
        add_increment: Optional[Callable[[str], None]] = None,
        show_message: Optional[Callable[[str, str], None]] = None,
        on_game_over: Optional[Callable[[str], None]] = None,
        cancel_draw: Optional[Callable[[], None]] = None,
    ) -> None:
        self.rules = rules
        self.canvas = canvas
        self.square_size = square_size
        self.margin = margin
        self.input_mode = input_mode or "click only"

        # Hooks UI (no-op si non fournis)
        self.update_board = update_board or (lambda: None)
        self.record_move  = record_move  or (lambda n,c: None)
        self.add_increment = add_increment or (lambda c: None)
        self.show_message = show_message or (lambda t,c: None)
        self.on_game_over = on_game_over or (lambda r: None)
        self.cancel_draw  = cancel_draw  or (lambda: None)

        # États d'interaction
        self.selected_piece: Optional[Coord] = None
        self.dragging: bool = False
        self.arrow_start: Optional[Tuple[int, int]] = None
        self.temp_arrow: Optional[int] = None
        self.arrows: List[int] = []
        self.highlights: Dict[Coord, int] = {}

    # ===================== BIND / UNBIND =====================
    def bind(self) -> None:
        """Lier les événements souris au canvas, selon input_mode."""
        if "click" in self.input_mode:
            self.canvas.bind("<Button-1>", self._on_canvas_click)
        if "drag" in self.input_mode:
            self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
            self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
            self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<ButtonPress-3>", self._on_right_press)
        self.canvas.bind("<B3-Motion>", self._on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_right_release)

    def unbind(self) -> None:
        for seq in ("<Button-1>", "<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>",
                    "<ButtonPress-3>", "<B3-Motion>", "<ButtonRelease-3>"):
            self.canvas.unbind(seq)
        self._clear_drawings()

    # ===================== UTILITAIRES =====================
    def _coord_from_xy(self, x: int, y: int) -> Optional[Coord]:
        col = int((x - self.margin) // self.square_size)
        row = int((y - self.margin) // self.square_size)
        if 0 <= row < 8 and 0 <= col < 8:
            return self.rules.plateau.notation_lettre((row, col))
        return None

    def _clear_drawings(self) -> None:
        for item in self.arrows:
            self.canvas.delete(item)
        self.arrows.clear()
        for item in self.highlights.values():
            self.canvas.delete(item)
        self.highlights.clear()
        self.arrow_start = None
        self.temp_arrow = None

    def _toggle_highlight(self, coord: Coord) -> None:
        if coord in self.highlights:
            self.canvas.delete(self.highlights[coord])
            del self.highlights[coord]
            return
        row, col = self.rules.plateau.notation_nombre(coord)
        x1 = self.margin + col * self.square_size
        y1 = self.margin + row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)
        self.highlights[coord] = rect

    # ===================== ÉVÈNEMENTS GAUCHE =====================
    def _on_canvas_click(self, event: tk.Event) -> None:
        self._clear_drawings()
        coord = self._coord_from_xy(event.x, event.y)
        if coord:
            self._on_click(coord)

    def _on_canvas_press(self, event: tk.Event) -> None:
        self._clear_drawings()
        coord = self._coord_from_xy(event.x, event.y)
        if coord and self.rules.plateau[coord] and \
           self.rules.plateau[coord].couleur == self.rules.current_turn:
            self.selected_piece = coord
            self.dragging = False
        else:
            self.selected_piece = None

    def _on_canvas_drag(self, event: tk.Event) -> None:
        self.dragging = True

    def _on_canvas_release(self, event: tk.Event) -> None:
        coord = self._coord_from_xy(event.x, event.y)
        if not self.dragging:
            if coord:
                self._on_click(coord)
        else:
            dest = coord
            if dest and self.selected_piece:
                self._on_click(dest)
        self.selected_piece = None
        self.dragging = False

    # ===================== ÉVÈNEMENTS DROIT =====================
    def _on_right_press(self, event: tk.Event) -> None:
        self.arrow_start = (event.x, event.y)
        self.temp_arrow = None

    def _on_right_drag(self, event: tk.Event) -> None:
        if self.arrow_start:
            if self.temp_arrow:
                self.canvas.delete(self.temp_arrow)
            self.temp_arrow = self.canvas.create_line(
                self.arrow_start[0], self.arrow_start[1], event.x, event.y,
                arrow=tk.LAST, width=4, fill="red"
            )

    def _on_right_release(self, event: tk.Event) -> None:
        if self.arrow_start is None:
            return
        if self.temp_arrow:
            self.canvas.delete(self.temp_arrow)
        start_coord = self._coord_from_xy(*self.arrow_start)
        end_coord = self._coord_from_xy(event.x, event.y)
        if start_coord and end_coord:
            # Clic simple = surlignage, sinon flèche
            if start_coord == end_coord and self.temp_arrow is None:
                self._toggle_highlight(start_coord)
            else:
                sx, sy = self.arrow_start
                row, col = self.rules.plateau.notation_nombre(end_coord)
                ex = self.margin + col * self.square_size + self.square_size / 2
                ey = self.margin + row * self.square_size + self.square_size / 2
                arrow_id = self.canvas.create_line(
                    sx, sy, ex, ey, arrow=tk.LAST, width=4, fill="green"
                )
                self.arrows.append(arrow_id)
        self.arrow_start = None
        self.temp_arrow = None

    # ===================== COEUR DU MOUVEMENT =====================
    def _on_click(self, coord: Coord) -> None:
        # 1) Sélectionner une pièce du trait
        if not self.selected_piece:
            piece = self.rules.plateau[coord]
            if piece and piece.couleur == self.rules.current_turn:
                self.selected_piece = coord
            return

        # 2) Tenter le coup
        start  = self.selected_piece
        piece  = self.rules.plateau[start]
        target = self.rules.plateau[coord]
        was_capture = bool(target and target.couleur != piece.couleur)
        moved = piece.couleur

        if self.rules.is_valid_move(piece, start, coord):
            # Annuler une éventuelle proposition de nulle
            self.cancel_draw()

            # Laisser ChessRules gérer roques, e.p., nulles 50 coups / répétition, etc.
            self.rules.execute_move(piece, start, coord)
            self.rules.update_repetition()
            if getattr(self.rules, "game_over", False):
                return

            # Mise à jour visuelle
            self.update_board()

            # Notation (promotion traitée ici, sinon SAN standard)
            if isinstance(piece, Pion) and coord[1] in ('1', '8'):
                prom = self.rules.plateau[coord]
                notation = f"{coord}={self.get_piece_letter(prom)}"
            else:
                notation = self.generate_move_notation(piece, start, coord, was_capture)

            # Hooks post-coup
            self.record_move(notation, moved)
            self.add_increment(moved)

            # États post-coup
            if self.rules.is_checkmate(self.rules.current_turn):
                winner = "Noir" if self.rules.current_turn == 'blanc' else "Blanc"
                self.on_game_over(f"Échec et mat ! {winner} gagne !")
                return
            if self.rules.is_stalemate(self.rules.current_turn):
                self.on_game_over("Pat ! Match nul !")
                return
            if self.rules.is_in_check(self.rules.current_turn):
                self.show_message(f"Échec à {self.rules.current_turn}", "orange")
            else:
                self.show_message(f"Tour des {self.rules.current_turn}", "black")
        else:
            self.show_message("Coup invalide", "red")
        self.selected_piece = None

    # ===================== NOTATION =====================
    def generate_move_notation(self, piece: Any, start: Coord, end: Coord, was_capture: bool=False) -> str:
        # Roque
        if isinstance(piece, Roi):
            sf, ef = ord(start[0]) - ord('a'), ord(end[0]) - ord('a')
            if abs(ef - sf) == 2:
                return "O-O" if ef > sf else "O-O-O"
        # Promotion pion (redondant avec _on_click, mais sûr)
        if isinstance(piece, Pion) and end[1] in ('1','8'):
            return f"{end}={self.get_piece_letter(piece)}"
        # Pion : capture ou avance simple
        if isinstance(piece, Pion):
            return f"{start[0]}x{end}" if start[0] != end[0] else end

        clean_end = end[0:2] if len(end) > 2 else end
        lett = self.get_piece_letter(piece)
        cap = "x" if was_capture else ""
        # Note : ces symboles dépendent de l'état des règles après coup
        check = "+" if self.rules.is_in_check(self.rules.current_turn) else ""
        mate  = "#" if self.rules.is_checkmate(self.rules.current_turn) else ""
        dis = self.get_disambiguation(piece, start, clean_end)
        return f"{lett}{dis}{cap}{end}{check}{mate}"

    def get_piece_letter(self, piece: Any) -> str:
        if isinstance(piece, Roi):      return "R"
        if isinstance(piece, Reine):    return "D"
        if isinstance(piece, Tour):     return "T"
        if isinstance(piece, Fou):      return "F"
        if isinstance(piece, Cavalier): return "C"
        return "?"

    def get_disambiguation(self, piece: Any, start: Coord, end: Coord) -> str:
        clean_end = end[0:2] if len(end) > 2 else end
        cands = [
            c for c,p in self.rules.plateau.items()
            if type(p) == type(piece)
            and p.couleur == piece.couleur
            and c != start
            and self.rules.is_legal(p, c, clean_end)
        ]
        if not cands:
            return ""
        if any(c[0] != start[0] for c in cands):
            return start[0]
        return start[1]

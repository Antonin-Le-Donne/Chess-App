from __future__ import annotations
import tkinter as tk
from typing import Optional, Dict, Any, Tuple, List, Callable

# Pièces (pour isinstance / lettres)
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

Coord = str  # "e4", "a1", ...

class Movement:
    """Gère les interactions plateau (clic/drag), flèches & surlignages (clic droit),
    validation/exécution des coups et génération de la notation SAN pour un mode JvJ 1v1.

    Étendu pour supporter aussi les flèches d'analyse moteur (vert/bleu)
    qui s'affichent sous les flèches du joueur.
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

        # Ajout pour l'analyse moteur
        self.analysis_arrows: List[int] = []  # calque séparé

    # ===================== BIND / UNBIND =====================
    def bind(self) -> None:
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
        self.clear_analysis_overlays()

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
                # important : joueur au-dessus des flèches IA
                self.canvas.tag_raise(arrow_id)
                self.arrows.append(arrow_id)
        self.arrow_start = None
        self.temp_arrow = None

    # ===================== FLÈCHES D’ANALYSE =====================
    def clear_analysis_overlays(self) -> None:
        """Supprime uniquement les flèches d’analyse moteur (vert/bleu)."""
        for item in self.analysis_arrows:
            self.canvas.delete(item)
        self.analysis_arrows.clear()

    def draw_analysis_arrow(self, start: str, end: str,
                            color: str = "blue", width: int = 5) -> None:
        """Dessine une flèche d'analyse moteur, plus épaisse et sous les flèches joueur."""
        try:
            row_from, col_from = self.rules.plateau.notation_nombre(start)
            row_to, col_to = self.rules.plateau.notation_nombre(end)
        except Exception:
            return

        sx = self.margin + col_from * self.square_size + self.square_size / 2
        sy = self.margin + row_from * self.square_size + self.square_size / 2
        ex = self.margin + col_to * self.square_size + self.square_size / 2
        ey = self.margin + row_to * self.square_size + self.square_size / 2

        arrow_id = self.canvas.create_line(
            sx, sy, ex, ey,
            arrow=tk.LAST,
            width=width,
            fill=color
        )
        # placer sous les flèches du joueur
        self.canvas.tag_lower(arrow_id)
        self.analysis_arrows.append(arrow_id)

    # ===================== COEUR DU MOUVEMENT =====================
    def _on_click(self, coord: Coord) -> None:
        if not self.selected_piece:
            piece = self.rules.plateau[coord]
            if piece and piece.couleur == self.rules.current_turn:
                self.selected_piece = coord
            return

        start = self.selected_piece
        piece = self.rules.plateau[start]
        target = self.rules.plateau[coord]
        was_capture = bool(target and target.couleur != piece.couleur)
        moved = piece.couleur

        if self.rules.is_valid_move(piece, start, coord):
            self.cancel_draw()
            self.rules.execute_move(piece, start, coord)
            self.rules.update_repetition()
            if getattr(self.rules, "game_over", False):
                return

            self.update_board()
            if isinstance(piece, Pion) and coord[1] in ('1', '8'):
                prom = self.rules.plateau[coord]
                notation = f"{coord}={self.get_piece_letter(prom)}"
            else:
                notation = self.generate_move_notation(piece, start, coord, was_capture)

            self.record_move(notation, moved)
            self.add_increment(moved)

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
        if isinstance(piece, Roi):
            sf, ef = ord(start[0]) - ord('a'), ord(end[0]) - ord('a')
            if abs(ef - sf) == 2:
                return "O-O" if ef > sf else "O-O-O"
        if isinstance(piece, Pion) and end[1] in ('1','8'):
            return f"{end}={self.get_piece_letter(piece)}"
        if isinstance(piece, Pion):
            return f"{start[0]}x{end}" if start[0] != end[0] else end
        clean_end = end[0:2] if len(end) > 2 else end
        lett = self.get_piece_letter(piece)
        cap = "x" if was_capture else ""
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

from __future__ import annotations
import tkinter as tk
from typing import Any, Callable, Optional, Tuple
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

# ATTENTION: adapte si ton fichier s'appelle 'movement.py' (anglais)
from mouvement import Movement


class MovementAI(Movement):
    """
    Étend Movement pour un mode Joueur vs IA.
    Ajout : support flèches d’analyse moteur (bleues),
            sans modifier Movement normal.
    """

    def __init__(
        self,
        *,
        rules: Any,
        canvas: tk.Canvas,
        square_size: int,
        margin: int,
        input_mode: str,
        update_board: Callable[[], None],
        record_move: Callable[[str, str], None],
        add_increment: Callable[[str], None],
        show_message: Callable[[str, str], None],
        on_game_over: Callable[[str], None],
        cancel_draw: Optional[Callable[[], None]],
        # --- Spécifique IA ---
        player_color: str,
        play_ai: Callable[[Any], Optional[Tuple[str, str]]],
        ai_delay_ms: int = 500,
    ) -> None:

        super().__init__(
            rules=rules,
            canvas=canvas,
            square_size=square_size,
            margin=margin,
            input_mode=input_mode,
            update_board=update_board,
            record_move=record_move,
            add_increment=add_increment,
            show_message=show_message,
            on_game_over=on_game_over,
            cancel_draw=cancel_draw
        )

        self.player_color = player_color
        self.ai_color = 'noir' if player_color == 'blanc' else 'blanc'
        self._play_ai = play_ai
        self._ai_delay_ms = ai_delay_ms

        # --- Flèches d’analyse moteur (uniquement pour MovementAI) ---
        self.analysis_arrows: list[int] = []

    # -------------------- FLÈCHES ANALYSE --------------------

    def clear_analysis_overlays(self) -> None:
        """
        Supprime les flèches d'analyse moteur uniquement.
        Ne touche PAS aux flèches utilisateur.
        """
        for item in self.analysis_arrows:
            self.canvas.delete(item)
        self.analysis_arrows.clear()

    def draw_analysis_arrow(self, start: str, end: str,
                            color: str = "blue", width: int = 4) -> None:
        """
        Dessine une flèche d'analyse (bleue) pour un coup moteur.
        start/end en 'e2', 'e4'.
        """

        # Convertir en coordonnées graphiques
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
        self.analysis_arrows.append(arrow_id)

    # -------------------- FILTRE TOUR IA --------------------

    def _on_canvas_click(self, event: tk.Event) -> None:
        if self.rules.current_turn != self.player_color or getattr(self.rules, "game_over", False):
            return
        super()._on_canvas_click(event)

    def _on_canvas_press(self, event: tk.Event) -> None:
        if self.rules.current_turn != self.player_color or getattr(self.rules, "game_over", False):
            return
        super()._on_canvas_press(event)

    def _on_canvas_drag(self, event: tk.Event) -> None:
        if self.rules.current_turn != self.player_color or getattr(self.rules, "game_over", False):
            return
        super()._on_canvas_drag(event)

    def _on_canvas_release(self, event: tk.Event) -> None:
        if self.rules.current_turn != self.player_color or getattr(self.rules, "game_over", False):
            return
        super()._on_canvas_release(event)

    # -------------------- COUP HUMAIN -> IA --------------------

    def _on_click(self, coord: str) -> None:
        before = self.rules.current_turn
        super()._on_click(coord)

        # si le trait a changé et c'est maintenant à l'IA
        if (
            not getattr(self.rules, "game_over", False)
            and self.rules.current_turn == self.ai_color
            and before != self.rules.current_turn
        ):
            # IMPORTANT : nettoyer les flèches d'analyse avant coup IA
            self.clear_analysis_overlays()
            self.canvas.after(self._ai_delay_ms, self._ai_play_if_needed)

    # -------------------- COUP IA --------------------

    def _ai_play_if_needed(self) -> None:
        """
        Joue le coup de l'IA si c'est à son tour.
        Les flèches analyse sont nettoyées juste avant.
        """
        if getattr(self.rules, "game_over", False) or self.rules.current_turn != self.ai_color:
            return

        ai_move = self._play_ai(self.rules)
        if not ai_move:
            self.on_game_over("Pat ! Match nul !")
            return

        start, end = ai_move

        # récupérer pièces
        try:
            piece = self.rules.plateau[start]
            target = self.rules.plateau[end]
        except KeyError:
            return

        if piece is None:
            return

        couleur_piece = getattr(piece, "couleur", None)
        couleur_target = getattr(target, "couleur", None) if target else None
        was_capture = target is not None and couleur_piece != couleur_target

        moved = couleur_piece

        # exécuter le coup
        self.rules.execute_move(piece, start, end)
        self.rules.update_repetition()
        if getattr(self.rules, "game_over", False):
            return

        self.update_board()

        # notation
        if isinstance(piece, Pion) and end[1] in ('1','8'):
            prom_piece = self.rules.plateau[end]
            notation = f"{end}={self.get_piece_letter(prom_piece)}"
        else:
            notation = self.generate_move_notation(piece, start, end, was_capture)

        if moved:
            self.record_move(notation, moved)
            self.add_increment(moved)

        # états spéciaux
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

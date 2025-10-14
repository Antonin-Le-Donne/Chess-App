# movement_ai.py — contrôleur Mouvement + tour IA (JvIA)
from __future__ import annotations
import tkinter as tk
from typing import Any, Callable, Optional, Tuple
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi

# ATTENTION: adapte si ton fichier s'appelle 'movement.py' (anglais)
from mouvement import Movement


class MovementAI(Movement):
    """
    Étend Movement pour un mode Joueur vs IA.
    - Bloque l'entrée utilisateur si ce n'est pas le tour du joueur humain.
    - Après un coup humain réussi => joue automatiquement le coup IA (via callback play_ai()).
    - Réutilise toute la pipeline de Movement: execute_move -> update_board -> notation -> record_move -> increment -> messages.
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
        player_color: str,             # "blanc" ou "noir" (humain)
        play_ai: Callable[[Any], Optional[Tuple[str, str]]],  # fn(rules) -> (start, end)
        ai_delay_ms: int = 500,
    ) -> None:
        super().__init__(
            rules=rules, canvas=canvas, square_size=square_size, margin=margin, input_mode=input_mode,
            update_board=update_board, record_move=record_move, add_increment=add_increment,
            show_message=show_message, on_game_over=on_game_over, cancel_draw=cancel_draw
        )
        self.player_color = player_color
        self.ai_color = 'noir' if player_color == 'blanc' else 'blanc'
        self._play_ai = play_ai
        self._ai_delay_ms = ai_delay_ms

    # ----- Filtre l'entrée utilisateur au tour IA -----
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

    # ----- Après un coup HUMAIN valide, déclenche l'IA -----
    def _on_click(self, coord: str) -> None:
        before = self.rules.current_turn
        super()._on_click(coord)
        # si le trait a changé ET c'est maintenant à l'IA
        if not getattr(self.rules, "game_over", False) and self.rules.current_turn == self.ai_color and before != self.rules.current_turn:
            self.canvas.after(self._ai_delay_ms, self._ai_play_if_needed)

    # ----- Coup IA -----
    def _ai_play_if_needed(self) -> None:
        if getattr(self.rules, "game_over", False) or self.rules.current_turn != self.ai_color:
            return

        ai_move = self._play_ai(self.rules)  # (start, end) ex: ("e2","e4")
        if not ai_move:
            # pas de coup: considère pat
            self.on_game_over("Pat ! Match nul !")
            return

        start, end = ai_move
        piece  = self.rules.plateau[start]
        target = self.rules.plateau[end]
        was_capture = bool(target and target.couleur != piece.couleur)
        moved = piece.couleur

        # Exécution (ChessRules gère promotion via promotion_callback si besoin)
        self.rules.execute_move(piece, start, end)
        self.rules.update_repetition()
        if getattr(self.rules, "game_over", False):
            return

        # Update visuel
        self.update_board()

        # Notation (promotion ou standard)
        if isinstance(piece, Pion) and end[1] in ('1','8'):
            prom_piece = self.rules.plateau[end]
            notation = f"{end}={self.get_piece_letter(prom_piece)}"
        else:
            notation = self.generate_move_notation(piece, start, end, was_capture)

        # Hooks post-coup
        self.record_move(notation, moved)
        self.add_increment(moved)

        # États : mat / pat / échec ?
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

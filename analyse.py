from __future__ import annotations
from typing import Any, List, Dict
from stockfish import Stockfish
import threading
import time


class AnalyseEngine:
    """
    Petit wrapper Stockfish assurant :
    - extraction FEN via rules.get_fen()
    - récupération des top 3 coups
    - formatage des évaluations
    - dessin des flèches moteur via MovementAI
    - mise à jour automatique en temps réel (optionnelle)
    """

    def __init__(self, stockfish_path="stockfish.exe", stockfish_obj: Stockfish | None = None):
        if stockfish_obj:
            self.sf = stockfish_obj
        else:
            self.sf = Stockfish(path=stockfish_path)

        # Variables pour le mode temps réel
        self._live_thread = None
        self._stop_live = threading.Event()
        self._last_fen = None

    # -------------------- FORMATAGE --------------------

    @staticmethod
    def _format_eval(eval_type: str, value: int) -> str:
        """Transforme cp/mate en texte lisible."""
        if eval_type == "mate":
            if value == 0:
                return "#0"
            sign = "" if value > 0 else "-"
            return f"{sign}#{abs(value)}"
        pawns = value / 100
        return f"{pawns:+.2f}"

    def _extract_branches(self, top_moves: List[Dict]) -> List[Dict]:
        """Transforme top_moves de Stockfish en branches propres."""
        branches = []
        for idx, info in enumerate(top_moves[:3], start=1):
            move = info.get("Move")
            if not move:
                continue

            # évaluation
            cp = info.get("Centipawn")
            mate = info.get("Mate")

            if mate is not None:
                eval_type = "mate"
                value = int(mate)
            else:
                eval_type = "cp"
                value = int(cp) if cp is not None else 0

            eval_text = self._format_eval(eval_type, value)
            pv = info.get("Pv", move)

            branches.append({
                "rank": idx,
                "move": move,
                "eval_text": eval_text,
                "pv": pv,
            })
        return branches

    # -------------------- ANALYSE --------------------

    def analyse(self, rules: Any, movementAI: Any | None = None) -> List[Dict]:
        """
        Analyse la position via Stockfish.
        Si movementAI fourni → dessin des flèches.
        """
        fen = rules.get_fen()
        self.sf.set_fen_position(fen)

        try:
            top_moves = self.sf.get_top_moves(3)
        except Exception:
            top_moves = []

        branches = self._extract_branches(top_moves)
        if not branches:
            return []

        # --------- AFFICHAGE DES FLÈCHES ---------
        if movementAI is not None:
            if hasattr(movementAI, "clear_analysis_overlays"):
                movementAI.clear_analysis_overlays()

            # Meilleur coup = vert
            best = branches[0]["move"]
            if len(best) >= 4:
                s, e = best[:2], best[2:4]
                movementAI.draw_analysis_arrow(s, e, color="green", width=4)

            # Autres branches = bleu
            for br in branches[1:]:
                mv = br["move"]
                if len(mv) < 4:
                    continue
                s, e = mv[:2], mv[2:4]
                movementAI.draw_analysis_arrow(s, e, color="blue", width=3)
        # ------------------------------------------------
        return branches

    # -------------------- TEMPS RÉEL --------------------

    def _live_loop(self, rules, movementAI, interval: float):
        """Boucle interne pour mise à jour périodique."""
        while not self._stop_live.is_set():
            fen = rules.get_fen()
            if fen != self._last_fen:
                self._last_fen = fen
                self.analyse(rules, movementAI)
            time.sleep(interval)

    def start_live_analysis(self, rules, movementAI, interval: float = 1.0):
        """Démarre l’analyse automatique en continu (thread)."""
        if self._live_thread and self._live_thread.is_alive():
            return  # déjà en cours

        self._stop_live.clear()
        self._last_fen = None
        self._live_thread = threading.Thread(
            target=self._live_loop,
            args=(rules, movementAI, interval),
            daemon=True
        )
        self._live_thread.start()

    def stop_live_analysis(self):
        """Arrête proprement l’analyse continue."""
        if self._live_thread and self._live_thread.is_alive():
            self._stop_live.set()
            self._live_thread.join(timeout=1)

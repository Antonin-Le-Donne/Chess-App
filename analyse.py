"""
analyse.py

Analyse de position avec Stockfish + affichage de flèches d'analyse
dans MovementAI uniquement (bleu/vert).

Utilisation :
    engine = AnalyseEngine(stockfish_path="stockfish.exe")
    branches = engine.analyse(rules, movementAI)

Retourne :
    liste de dicts :
        {
            "move": "e2e4",
            "eval_text": "+0.82",
            "pv": "e2e4 e7e5 g1f3 ...",
            "rank": 1
        }
"""

from __future__ import annotations
from typing import Any, List, Dict
from stockfish import Stockfish


class AnalyseEngine:
    """
    Petit wrapper Stockfish assurant :
    - extraction FEN via rules.get_fen()
    - récupération des top 3 coups
    - formatage des évaluations
    - dessin des flèches moteur via MovementAI
    """

    def __init__(self, stockfish_path="stockfish.exe", stockfish_obj: Stockfish | None = None):
        if stockfish_obj:
            self.sf = stockfish_obj
        else:
            self.sf = Stockfish(path=stockfish_path)

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

            pv = info.get("Pv")
            if not pv:
                pv = move

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

        # Récupérer la fen depuis ChessRules
        fen = rules.get_fen()
        self.sf.set_fen_position(fen)

        # On demande top 3
        try:
            top_moves = self.sf.get_top_moves(3)
        except Exception:
            top_moves = []

        # Construire les branches
        branches = self._extract_branches(top_moves)

        # Si aucun coup → juste retourner
        if not branches:
            return []

        # --------- AFFICHAGE DES FLÈCHES via MovementAI ---------
        if movementAI is not None:

            # Effacer anciennes flèches
            if hasattr(movementAI, "clear_analysis_overlays"):
                movementAI.clear_analysis_overlays()

            # Best move = vert
            best = branches[0]["move"]
            s = best[:2]
            e = best[2:4]
            movementAI.draw_analysis_arrow(s, e, color="green", width=4)

            # Autres branches = bleu
            for br in branches[1:]:
                mv = br["move"]
                if len(mv) < 4:
                    continue
                ss = mv[:2]
                ee = mv[2:4]
                movementAI.draw_analysis_arrow(ss, ee, color="blue", width=3)

        # --------------------------------------------------------

        return branches
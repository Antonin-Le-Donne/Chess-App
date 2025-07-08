import random
from stockfish import Stockfish

class ChessIA:
    def __init__(self, couleur, niveau='debutant', stockfish_path='stockfish.exe'):
        self.couleur = couleur
        self.niveau = niveau
        self.profondeur = self.get_profondeur()
        self.stockfish = Stockfish(path=stockfish_path)
        self.stockfish.set_elo_rating(self.get_stockfish_elo())

    def get_profondeur(self):
        return {
            'debutant': 0,
            'facile': 1,
            'intermediaire': 2,
            'fort': 3,
            'maitre': 4,
            'gmaitre': 5
        }.get(self.niveau, 1)

    def get_stockfish_elo(self):
        return {
            'debutant': 800,
            'facile': 1200,
            'intermediaire': 1600,
            'fort': 1900,
            'maitre': 2200,
            'gmaitre': 2500
        }.get(self.niveau, 1500)

    def get_legal_moves(self, rules):
        moves = []
        for start, piece in rules.plateau.items():
            if piece and piece.couleur == self.couleur:
                for end in rules.plateau.keys():
                    if rules.is_valid_move(piece, start, end):
                        sauvegarde = rules.plateau[end]
                        rules.plateau[end] = piece
                        rules.plateau[start] = None
                        roi_safe = not rules.is_in_check(self.couleur)
                        rules.plateau[start] = piece
                        rules.plateau[end] = sauvegarde
                        if roi_safe:
                            moves.append((start, end))
        return moves

    def play(self, rules):
        fen = rules.get_fen()
        self.stockfish.set_fen_position(fen)
        move_uci = self.stockfish.get_best_move()

        if move_uci:
            start = move_uci[:2]
            end = move_uci[2:4]
            piece = rules.plateau[start]
            if piece:
                rules.execute_move(piece, start, end)
                return (start, end)
            else:
                print("Erreur : pièce non trouvée au départ.")
        else:
            print("Stockfish n’a pas pu proposer de coup. Fallback Minimax...")

        # Fallback si Stockfish échoue : joue un coup au hasard
        legal_moves = self.get_legal_moves(rules)
        if legal_moves:
            move = random.choice(legal_moves)
            piece = rules.plateau[move[0]]
            rules.execute_move(piece, move[0], move[1])
            return move

        return None

    def close(self):
        if hasattr(self, "stockfish") and self.stockfish is not None:
            self.stockfish.quit()
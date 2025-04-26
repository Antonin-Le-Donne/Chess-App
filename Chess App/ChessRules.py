from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi
from plateau import Plateau

class ChessRules:
    """
    Classe pour gérer les règles du jeu d'échecs, y compris les mouvements spéciaux.
    """

    def __init__(self):
        self.plateau = Plateau()
        self.current_turn = 'blanc'
        self.en_passant_target = None
        self.castling_rights = {
            'blanc': {'king_side': True, 'queen_side': True},
            'noir': {'king_side': True, 'queen_side': True}
        }
        self.move_counter = 0
        self.game_over = False
        self.positions_history = {}
        self.game_over_callback = None
        self.initialize_pieces()


    def get_board_state(self):
        state = []
        for square in sorted(self.plateau.keys()):
            piece = self.plateau[square]
            if piece:
                state.append(f"{square}:{piece.__class__.__name__}_{piece.couleur}")
            else:
                state.append(f"{square}:None")
        state.append(f"turn:{self.current_turn}")
        state.append(f"en_passant:{self.en_passant_target}")
        state.append(f"castling:{self.castling_rights}")
        return ";".join(state)
    
    def update_repetition(self):
        state = self.get_board_state()
        self.positions_history[state] = self.positions_history.get(state, 0) + 1
        if self.positions_history[state] >= 3:
            if self.game_over_callback:
                self.game_over_callback("Match nul par répétition triple !")
            else:
                print("GAME OVER: Match nul par répétition triple !")
            self.game_over = True

    def initialize_pieces(self):
        # Pièces blanches
        self.plateau['a1'] = Tour('blanc')
        self.plateau['b1'] = Cavalier('blanc')
        self.plateau['c1'] = Fou('blanc')
        self.plateau['d1'] = Reine('blanc')
        self.plateau['e1'] = Roi('blanc')
        self.plateau['f1'] = Fou('blanc')
        self.plateau['g1'] = Cavalier('blanc')
        self.plateau['h1'] = Tour('blanc')
        for col in 'abcdefgh':
            self.plateau[f'{col}2'] = Pion('blanc')
        # Pièces noires
        self.plateau['a8'] = Tour('noir')
        self.plateau['b8'] = Cavalier('noir')
        self.plateau['c8'] = Fou('noir')
        self.plateau['d8'] = Reine('noir')
        self.plateau['e8'] = Roi('noir')
        self.plateau['f8'] = Fou('noir')
        self.plateau['g8'] = Cavalier('noir')
        self.plateau['h8'] = Tour('noir')
        for col in 'abcdefgh':
            self.plateau[f'{col}7'] = Pion('noir')

    def is_legal(self, piece, start, end):
        """
        Vérifie si le mouvement est légal pour la pièce donnée,
        en tenant compte des règles spécifiques de déplacement et
        de la sécurité du roi (cette méthode est utilisée pour
        la détection de stalemate et checkmate et ne vérifie pas le tour).
        """
        # Le coup ne peut pas être nul
        if start == end:
            return False

        # On ne peut pas capturer une pièce de même couleur
        target_piece = self.plateau[end]
        if target_piece and target_piece.couleur == piece.couleur:
            return False

        # Récupération des coordonnées
        start_row, start_col = self.plateau.notation_nombre(start)
        end_row, end_col = self.plateau.notation_nombre(end)

        # Vérifier que le déplacement respecte les règles spécifiques de la pièce
        if isinstance(piece, Pion):
            if not self.is_valid_pawn_move(start_row, start_col, end_row, end_col, piece.couleur):
                return False
        elif isinstance(piece, Tour):
            if not self.is_valid_rook_move(start_row, start_col, end_row, end_col):
                return False
        elif isinstance(piece, Cavalier):
            if not self.is_valid_knight_move(start_row, start_col, end_row, end_col):
                return False
        elif isinstance(piece, Fou):
            if not self.is_valid_bishop_move(start_row, start_col, end_row, end_col):
                return False
        elif isinstance(piece, Reine):
            if not self.is_valid_queen_move(start_row, start_col, end_row, end_col):
                return False
        elif isinstance(piece, Roi):
            if not self.is_valid_king_move(start_row, start_col, end_row, end_col):
                return False

        # Simulation du coup pour vérifier que le roi n'est pas en échec après le mouvement
        original_piece = self.plateau[end]
        self.plateau[end] = piece
        self.plateau[start] = None
        result = not self.is_in_check(piece.couleur)
        # Restauration de l'état initial, même en cas d'erreur
        self.plateau[start] = piece
        self.plateau[end] = original_piece

        return result


    def is_valid_move(self, piece, start, end):
        """
        Vérifie si un mouvement est valide pour la pièce donnée,
        en tenant compte de son type et de la possibilité d'échec.
        """
        print(f"DEBUG: Tour actuel: {self.current_turn}, Pièce: {piece}, Déplacement: {start} -> {end}")

        # Vérifications de base
        if start == end:
            print(f"Mouvement invalide : la pièce ne peut pas rester sur place ({start} -> {end})")
            return False

        if piece.couleur != self.current_turn:
            print(f"Mouvement invalide : ce n'est pas le tour de cette pièce ({start} -> {end}).")
            return False

        target_piece = self.plateau[end]
        if target_piece and target_piece.couleur == piece.couleur:
            print(f"Mouvement invalide : case occupée par une pièce alliée ({start} -> {end}).")
            return False

        # Règles spécifiques selon le type de pièce
        start_row, start_col = self.plateau.notation_nombre(start)
        end_row, end_col = self.plateau.notation_nombre(end)

        if isinstance(piece, Pion):
            if not self.is_valid_pawn_move(start_row, start_col, end_row, end_col, piece.couleur):
                print("Mouvement invalide : le pion ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Tour):
            if not self.is_valid_rook_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : la tour ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Cavalier):
            if not self.is_valid_knight_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : le cavalier ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Fou):
            if not self.is_valid_bishop_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : le fou ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Reine):
            if not self.is_valid_queen_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : la reine ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Roi):
            if not self.is_valid_king_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : le roi ne peut pas se déplacer ainsi.")
                return False
        else:
            return False

        # Simulation du coup pour vérifier que le roi n'est pas en échec.
        original_piece = self.plateau[end]
        # Sauvegarde de l'état initial
        self.plateau[start], self.plateau[end] = None, piece
        try:
            if self.is_in_check(piece.couleur):
                print("Mouvement invalide : ce coup laisse votre roi en échec.")
                return False
        finally:
            # Restauration de l'état initial
            self.plateau[start], self.plateau[end] = piece, original_piece

        print(f"Mouvement valide : {start} -> {end}")
        return True
        """
        Vérifie si un mouvement est valide pour la pièce donnée,
        en tenant compte de son type et de la possibilité d'échec.
        """
        print(f"DEBUG: Tour actuel: {self.current_turn}, Pièce: {piece}, Déplacement: {start} -> {end}")

        # 1) Vérifications de base
        if start == end:
            print(f"Mouvement invalide : la pièce ne peut pas rester sur place ({start} -> {end})")
            return False

        if piece.couleur != self.current_turn:
            print(f"Mouvement invalide : ce n'est pas le tour de cette pièce ({start} -> {end}).")
            return False

        target_piece = self.plateau[end]
        if target_piece and target_piece.couleur == piece.couleur:
            print(f"Mouvement invalide : tentative de déplacement sur une case occupée par une pièce alliée ({start} -> {end}).")
            return False

        # 2) Vérification du déplacement propre à chaque type de pièce
        start_row, start_col = self.plateau.notation_nombre(start)
        end_row, end_col = self.plateau.notation_nombre(end)

        if isinstance(piece, Pion):
            if not self.is_valid_pawn_move(start_row, start_col, end_row, end_col, piece.couleur):
                print("Mouvement invalide : le pion ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Tour):
            if not self.is_valid_rook_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : la tour ne peut pas se déplacer ainsi (ligne/colonne obstruée ?).")
                return False
        elif isinstance(piece, Cavalier):
            if not self.is_valid_knight_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : le cavalier ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Fou):
            if not self.is_valid_bishop_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : le fou ne peut pas se déplacer ainsi (diagonale obstruée ?).")
                return False
        elif isinstance(piece, Reine):
            if not self.is_valid_queen_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : la reine ne peut pas se déplacer ainsi.")
                return False
        elif isinstance(piece, Roi):
            if not self.is_valid_king_move(start_row, start_col, end_row, end_col):
                print("Mouvement invalide : le roi ne peut pas se déplacer ainsi.")
                return False
        else:
            # Type de pièce inconnu ?
            return False

        # 3) Simuler le coup pour vérifier si le roi reste (ou devient) en échec
        original_piece = self.plateau[end]
        self.plateau[end] = piece
        self.plateau[start] = None

        if self.is_in_check(piece.couleur):
            # On remet le plateau dans son état initial
            self.plateau[start] = piece
            self.plateau[end] = original_piece
            print("Mouvement invalide : ce coup laisse votre roi en échec.")
            return False

        # On restaure avant de renvoyer True (le mouvement est légal)
        self.plateau[start] = piece
        self.plateau[end] = original_piece

        print(f"Mouvement valide : {start} -> {end}")
        return True


    def is_valid_pawn_move(self, start_row, start_col, end_row, end_col, couleur):
        """
        Vérifie si un mouvement de pion est valide, y compris en passant.
        """
        direction = -1 if couleur == 'blanc' else 1  # Blanc va vers le haut, noir vers le bas

        # Mouvement normal (1 case vers l'avant)
        if end_col == start_col and end_row == start_row + direction:
            return self.plateau[self.plateau.notation_lettre((end_row, end_col))] is None

        # Double mouvement (2 cases vers l'avant au premier coup)
        if end_col == start_col and end_row == start_row + 2 * direction:
            if (couleur == 'blanc' and start_row == 6) or (couleur == 'noir' and start_row == 1):
                intermediate_pos = (start_row + direction, start_col)
                return (
                    self.plateau[self.plateau.notation_lettre(intermediate_pos)] is None and
                    self.plateau[self.plateau.notation_lettre((end_row, end_col))] is None
                )
            return False

        # Capture (diagonale)
        if abs(end_col - start_col) == 1 and end_row == start_row + direction:
            target_piece = self.plateau[self.plateau.notation_lettre((end_row, end_col))]
            if target_piece is not None and target_piece.couleur != couleur:
                return True

            # En passant
            if self.en_passant_target == self.plateau.notation_lettre((end_row, end_col)):
                captured_pawn_pos = self.plateau.notation_lettre((start_row, end_col))
                if isinstance(self.plateau[captured_pawn_pos], Pion) and self.plateau[captured_pawn_pos].couleur != couleur:
                    return True

        return False

    def is_valid_rook_move(self, start_row, start_col, end_row, end_col):
        """
        Vérifie si un mouvement de tour est valide.
        """
        if start_row != end_row and start_col != end_col:
            return False  # La tour doit se déplacer en ligne droite

        # Vérifie les obstacles sur le chemin
        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if self.plateau[self.plateau.notation_lettre((start_row, col))] is not None:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if self.plateau[self.plateau.notation_lettre((row, start_col))] is not None:
                    return False

        return True

    def is_valid_knight_move(self, start_row, start_col, end_row, end_col):
        """
        Vérifie si un mouvement de cavalier est valide.
        """
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def is_valid_bishop_move(self, start_row, start_col, end_row, end_col):
        """
        Vérifie si un mouvement de fou est valide.
        """
        if abs(end_row - start_row) != abs(end_col - start_col):
            return False  # Le fou doit se déplacer en diagonale

        # Vérifie les obstacles sur le chemin
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        row, col = start_row + row_step, start_col + col_step
        while row != end_row and col != end_col:
            if self.plateau[self.plateau.notation_lettre((row, col))] is not None:
                return False
            row += row_step
            col += col_step

        return True

    def is_valid_queen_move(self, start_row, start_col, end_row, end_col):
        """
        Vérifie si un mouvement de reine est valide.
        """
        # La reine peut se déplacer comme une tour ou un fou
        return self.is_valid_rook_move(start_row, start_col, end_row, end_col) or \
               self.is_valid_bishop_move(start_row, start_col, end_row, end_col)

    def is_valid_king_move(self, start_row, start_col, end_row, end_col):
        """
        Vérifie si le mouvement du roi est valide.
        Pour un déplacement normal, le roi se déplace d'une case dans n'importe quelle direction.
        Pour le roque (déplacement de 2 cases horizontalement), la méthode vérifie seulement
        si le roque est possible, sans l'exécuter.
        """
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)

        # Mouvement normal : le roi se déplace d'une case dans n'importe quelle direction
        if row_diff <= 1 and col_diff <= 1:
            return True

        # Roque : déplacement de deux cases horizontalement
        if row_diff == 0 and col_diff == 2:
            return self.is_castling_possible(start_row, start_col, end_row, end_col)

        return False

    def is_castling_possible(self, start_row, start_col, end_row, end_col):
        """
        Vérifie si le roque est possible.
        """
        couleur = self.plateau[self.plateau.notation_lettre((start_row, start_col))].couleur
        king_side = (end_col > start_col)
        # Correction : pour les blancs, le roi doit être sur la rangée 7 (et pour les noirs sur la rangée 0)
        if (couleur == 'blanc' and start_row != 7) or (couleur == 'noir' and start_row != 0):
            return False

        if not self.castling_rights[couleur]['king_side' if king_side else 'queen_side']:
            return False

        if king_side:
            for col in range(start_col + 1, 7):
                if self.plateau[self.plateau.notation_lettre((start_row, col))] is not None:
                    return False
        else:
            for col in range(1, start_col):
                if self.plateau[self.plateau.notation_lettre((start_row, col))] is not None:
                    return False

        opponent_color = 'noir' if couleur == 'blanc' else 'blanc'
        for col in range(start_col, end_col + (1 if king_side else -1), (1 if king_side else -1)):
            square = self.plateau.notation_lettre((start_row, col))
            if self.is_square_under_attack(square, opponent_color):
                return False

        return True


    def perform_castling(self, couleur, start_row, start_col, end_col):
        """
        Effectue le roque en déplaçant le roi et la tour.
        """
        king_pos = self.plateau.notation_lettre((start_row, start_col))
        king = self.plateau[king_pos]

        # Déplacement du roi
        self.plateau[self.plateau.notation_lettre((start_row, end_col))] = king
        self.plateau[king_pos] = None  # Supprime le roi de sa position initiale

        # Déplacement de la tour
        if end_col > start_col:  # Roque côté roi
            rook_start = self.plateau.notation_lettre((start_row, 7))
            rook_end = self.plateau.notation_lettre((start_row, end_col - 1))
        else:  # Roque côté dame
            rook_start = self.plateau.notation_lettre((start_row, 0))
            rook_end = self.plateau.notation_lettre((start_row, end_col + 1))

        self.plateau[rook_end] = self.plateau[rook_start]
        self.plateau[rook_start] = None

        # Mise à jour des droits de roque
        self.castling_rights[couleur]['king_side'] = False
        self.castling_rights[couleur]['queen_side'] = False

    def is_square_under_attack(self, square, attacker_color):
        """
        Vérifie si une case est sous attaque par une pièce de la couleur donnée.
        """
        for coord, piece in self.plateau.items():
            if piece and piece.couleur == attacker_color:
                if self.is_valid_move(piece, coord, square):
                    return True
        return False

    def does_move_leave_king_in_check(self, piece, start, end):
        """
        Simule un mouvement et vérifie si le roi est en échec après le mouvement.
        """
        original_piece = self.plateau[end]
        self.plateau[end] = piece
        self.plateau[start] = None

        king_pos = None
        for coord, p in self.plateau.items():
            if isinstance(p, Roi) and p.couleur == piece.couleur:
                king_pos = coord
                break

        is_in_check = self.is_square_under_attack(king_pos, 'noir' if piece.couleur == 'blanc' else 'blanc')

        self.plateau[start] = piece
        self.plateau[end] = original_piece

        return is_in_check

    def execute_move(self, piece, start, end):
        if not self.is_valid_move(piece, start, end):
            return False

        # Révoquer les droits de roque si le roi ou une tour bouge
        if isinstance(piece, Roi):
            self.castling_rights[piece.couleur]['king_side'] = False
            self.castling_rights[piece.couleur]['queen_side'] = False
        elif isinstance(piece, Tour):
            # Tour quitte a1/a8 ⇒ plus de roque côté dame
            if start == ('a1' if piece.couleur == 'blanc' else 'a8'):
                self.castling_rights[piece.couleur]['queen_side'] = False
            # Tour quitte h1/h8 ⇒ plus de roque côté roi
            if start == ('h1' if piece.couleur == 'blanc' else 'h8'):
                self.castling_rights[piece.couleur]['king_side'] = False

        fr, fc = self.plateau.notation_nombre(start)
        tr, tc = self.plateau.notation_nombre(end)

        # Roque
        if isinstance(piece, Roi) and abs(tc - fc) == 2:
            self.perform_castling(piece.couleur, fr, fc, tc)
            self.en_passant_target = None
            self.switch_turn()
            return True

        # Prise en passant
        if isinstance(piece, Pion) and fc != tc and self.plateau[end] is None:
            captured = self.plateau.notation_lettre((fr, tc))
            self.plateau[captured] = None

        # Déplacement normal / capture
        capture = self.plateau[end] is not None
        self.plateau[end] = piece
        self.plateau[start] = None

        # Règle des 50 coups
        self.move_counter = 0 if isinstance(piece, Pion) or capture else self.move_counter + 1

        # Mise à jour de la cible en passant
        if isinstance(piece, Pion) and abs(tr - fr) == 2:
            mid = (fr + tr) // 2
            self.en_passant_target = self.plateau.notation_lettre((mid, fc))
        else:
            self.en_passant_target = None

        # Promotion
        if isinstance(piece, Pion) and end[1] in ('1', '8'):
            prom = self.promotion_callback(piece.couleur) if self.promotion_callback else Reine(piece.couleur)
            self.promote_pawn(end, prom)

        # Nulles et fin de partie
        if self.move_counter >= 50:
            self.game_over = True
            if self.game_over_callback:
                self.game_over_callback("Match nul par règle des 50 coups !")
            return True

        self.update_repetition()
        if self.game_over:
            return True

        if self.is_insufficient_material():
            self.game_over = True
            if self.game_over_callback:
                self.game_over_callback("Match nul par matériel insuffisant !")
            return True

        if self.is_checkmate(self.current_turn):
            self.game_over = True
            if self.game_over_callback:
                self.game_over_callback(f"Checkmate! {'Blanc' if self.current_turn=='noir' else 'Noir'} gagne!")
            return True

        if self.is_stalemate(self.current_turn):
            self.game_over = True
            if self.game_over_callback:
                self.game_over_callback("Pat! Match nul!")
            return True

        self.switch_turn()
        return True


    def is_path_clear(self, start, end):
        start_row, start_col = self.plateau.notation_nombre(start)
        end_row, end_col = self.plateau.notation_nombre(end)
            
        # Calculer le pas en ligne et en colonne
        if start_row != end_row:
            row_step = (end_row - start_row) // abs(end_row - start_row)
        else:
            row_step = 0
        if start_col != end_col:
            col_step = (end_col - start_col) // abs(end_col - start_col)
        else:
            col_step = 0

        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != (end_row, end_col):
            # Assurez-vous que l'indice est dans les limites
            if not (0 <= current_row < 8 and 0 <= current_col < 8):
                 return False
            if self.plateau[self.plateau.notation_lettre((current_row, current_col))] is not None:
                return False
            current_row += row_step
            current_col += col_step

        return True

    def switch_turn(self):
        """
        Change le tour de joueur après un mouvement valide.
        Vérifie si le joueur dont c'est le tour est en stalemate.
        """
        self.current_turn = 'noir' if self.current_turn == 'blanc' else 'blanc'
        print(f"DEBUG: Changement de tour -> Nouveau tour : {self.current_turn}")

       

    def make_move(self, start, end):
        """
        Effectue un mouvement si celui-ci est valide.
        Le changement de tour est géré dans execute_move().
        """
        if self.game_over:
            print("La partie est terminée.")
            return
        piece = self.plateau[start]
        if piece and self.is_valid_move(piece, start, end):
            self.execute_move(piece, start, end)

    def is_in_check(self, couleur):
        king_pos = next((coord for coord, piece in self.plateau.items() if isinstance(piece, Roi) and piece.couleur == couleur), None)
        if not king_pos:
            return False

        opponent_color = 'noir' if couleur == 'blanc' else 'blanc'

        for coord, piece in self.plateau.items():
            if piece and piece.couleur == opponent_color:
                if self.can_attack(piece, coord, king_pos):
                    return True
        return False

    def can_attack(self, piece, start, target):
        start_row, start_col = self.plateau.notation_nombre(start)
        target_row, target_col = self.plateau.notation_nombre(target)

        if isinstance(piece, Pion):
            direction = -1 if piece.couleur == 'blanc' else 1
            return abs(target_col - start_col) == 1 and (target_row - start_row) == direction

        elif isinstance(piece, Cavalier):
            return (abs(start_row - target_row), abs(start_col - target_col)) in [(2, 1), (1, 2)]

        elif isinstance(piece, Fou):
            return abs(start_row - target_row) == abs(start_col - target_col) and self.is_path_clear(start, target)

        elif isinstance(piece, Tour):
            return (start_row == target_row or start_col == target_col) and self.is_path_clear(start, target)

        elif isinstance(piece, Reine):
            return (start_row == target_row or start_col == target_col or abs(start_row - target_row) == abs(start_col - target_col)) and self.is_path_clear(start, target)

        elif isinstance(piece, Roi):
            return abs(start_row - target_row) <= 1 and abs(start_col - target_col) <= 1

        return False

    def is_path_obstructed(self, start, end):
        start_row, start_col = self.plateau.notation_nombre(start)
        end_row, end_col = self.plateau.notation_nombre(end)
        # Calcul des pas (row_step et col_step)
        row_diff = end_row - start_row
        col_diff = end_col - start_col
        row_step = row_diff // max(1, abs(row_diff))
        col_step = col_diff // max(1, abs(col_diff))
        
        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != (end_row, end_col):
            # Vérifie que l'on reste dans les bornes du plateau
            if not (0 <= current_row < 8 and 0 <= current_col < 8):
                # Si la position calculée est hors plateau, on considère le chemin comme obstrué
                return True
            if self.plateau[self.plateau.notation_lettre((current_row, current_col))] is not None:
                print(f"DEBUG: Chemin obstrué à {self.plateau.notation_lettre((current_row, current_col))}")
                return True
            current_row += row_step
            current_col += col_step
        return False


    def is_checkmate(self, couleur):
        """
        Vérifie si le joueur est en échec et mat.
        """
        if not self.is_in_check(couleur):
            return False

        for start, piece in self.plateau.items():
            if piece and piece.couleur == couleur:
                for end in self.plateau.keys():
                    if self.is_valid_move(piece, start, end):
                        return False
        return True


    def is_stalemate(self, couleur):
        """
        Vérifie si le joueur actif est en stalemate (pat).
        Un stalemate se produit si :
          - Le joueur n'est pas en échec,
          - Aucune de ses pièces ne peut effectuer de mouvement légal.
        """
        if self.is_in_check(couleur):
            print(f"DEBUG: {couleur} est en échec, donc ce n'est pas un stalemate.")
            return False

        has_legal_moves = False
        for start, piece in self.plateau.items():
            if piece and piece.couleur == couleur:
                for end in self.plateau.keys():
                    if self.is_legal(piece, start, end):
                        print(f"DEBUG: {couleur} peut bouger {piece} de {start} à {end}, donc pas un stalemate.")
                        has_legal_moves = True
                        break
                if has_legal_moves:
                    break

        if not has_legal_moves:
            print(f"DEBUG: Aucun coup légal possible pour {couleur}, stalemate détecté.")
            return True
        return False

    def is_fifty_move_rule(self):
        """
        Vérifie la règle des 50 coups : nulle si 50 coups consécutifs sans capture ni déplacement de pion.
        """
        return self.move_counter >= 50

    def promote_pawn(self, position, new_piece):
        """
        Remplace un pion promu par une pièce choisie par le joueur.
        """
        piece = self.plateau[position]
        if not isinstance(piece, Pion):
            return  # Ce n'est pas un pion, donc pas de promotion

        if (piece.couleur == 'blanc' and position[1] == '8') or (piece.couleur == 'noir' and position[1] == '1'):
            self.plateau[position] = new_piece  # Remplace le pion par la nouvelle pièce


    def is_insufficient_material(self):
        # Récupère pièces non-roi
        def pcs(color):
            return [p for p in self.plateau.plateau.values() if p and p.couleur == color and not isinstance(p, Roi)]
        def minor(p):
            return isinstance(p, (Fou, Cavalier))
        def insuf(color):
            pieces = pcs(color)
            if not pieces:
                return True
            if len(pieces) == 1 and minor(pieces[0]):
                return True
            if len(pieces) == 2 and all(minor(p) for p in pieces):
                return True
            return False
        return insuf('blanc') and insuf('noir')


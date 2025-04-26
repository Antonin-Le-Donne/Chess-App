class PieceEchec:
    """
    Classe de base pour toutes les pièces d'échecs.
    """
    def __init__(self, couleur, symbol):
        self.couleur = couleur  # 'blanc' ou 'noir'
        self.symbol = symbol  # Unicode symbol for the piece

    def __str__(self):
        return self.symbol


class Pion(PieceEchec):
    """
    Classe pour la pièce Pion.
    """
    def __init__(self, couleur):
        symbol = '♙' if couleur == 'blanc' else '♟'
        super().__init__(couleur, symbol)


class Tour(PieceEchec):
    """
    Classe pour la pièce Tour.
    """
    def __init__(self, couleur):
        symbol = '♖' if couleur == 'blanc' else '♜'
        super().__init__(couleur, symbol)


class Cavalier(PieceEchec):
    """
    Classe pour la pièce Cavalier.
    """
    def __init__(self, couleur):
        symbol = '♘' if couleur == 'blanc' else '♞'
        super().__init__(couleur, symbol)


class Fou(PieceEchec):
    """
    Classe pour la pièce Fou.
    """
    def __init__(self, couleur):
        symbol = '♗' if couleur == 'blanc' else '♝'
        super().__init__(couleur, symbol)


class Reine(PieceEchec):
    """
    Classe pour la pièce Reine (ou Dame).
    """
    def __init__(self, couleur):
        symbol = '♕' if couleur == 'blanc' else '♛'
        super().__init__(couleur, symbol)


class Roi(PieceEchec):
    """
    Classe pour la pièce Roi.
    """
    def __init__(self, couleur):
        symbol = '♔' if couleur == 'blanc' else '♚'
        super().__init__(couleur, symbol)
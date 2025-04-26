class Plateau:
    """
    Classe représentant le plateau d'échecs.
    """

    def __init__(self):
        self.plateau = {}
        self.initialiser_plateau()

    def initialiser_plateau(self):
        for ligne in range(8):
            for colonne in range(8):
                coord = self.notation_lettre((ligne, colonne))
                self.plateau[coord] = None

    def deplacer(self, depart, arrivee):
        if depart not in self.plateau or arrivee not in self.plateau:
            raise ValueError("Coordonnée invalide.")

        piece = self.plateau[depart]
        if not piece:
            raise ValueError("Aucune pièce à cet emplacement.")

        self.plateau[arrivee] = piece
        self.plateau[depart] = None

    def items(self):
        return self.plateau.items()

    def keys(self):
        """
        Retourne les coordonnées du plateau.
        """
        return self.plateau.keys()

    def notation_nombre(self, coord):
        colonne = ord(coord[0]) - ord('a')
        ligne = 8 - int(coord[1])
        return (ligne, colonne)

    def notation_lettre(self, position):
        lettres = 'abcdefgh'
        chiffres = '12345678'
        return lettres[position[1]] + chiffres[7 - position[0]]

    def __getitem__(self, coord):
        return self.plateau[coord]

    def __setitem__(self, coord, piece):
        self.plateau[coord] = piece
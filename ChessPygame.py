import os
import sys
import pygame

from ChessRules import ChessRules
from pieceEchec import Pion, Tour, Cavalier, Fou, Reine, Roi


class ChessPygame:
    LIGHT_COLOR = (240, 217, 181)
    DARK_COLOR = (181, 136, 99)

    def __init__(self):
        pygame.init()
        self.square_size = 80
        self.top_margin = 40
        width = self.square_size * 8
        height = width + self.top_margin
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Chess Game - Pygame")
        self.font = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        self.rules = ChessRules()
        self.selected = None
        self.message = "Blanc à jouer"
        self._load_images()

    def _load_images(self):
        self.images = {}
        base = os.path.join(os.path.dirname(__file__), "skins", "classique")
        for cls in ["Pion", "Tour", "Cavalier", "Fou", "Reine", "Roi"]:
            for color in ["blanc", "noir"]:
                fn = f"{color}_{cls.lower()}.png"
                path = os.path.join(base, fn)
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (self.square_size, self.square_size))
                self.images[(cls, color)] = img

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                color = self.LIGHT_COLOR if (r + c) % 2 == 0 else self.DARK_COLOR
                x = c * self.square_size
                y = self.top_margin + r * self.square_size
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
        if self.selected:
            r, c = self.rules.plateau.notation_nombre(self.selected)
            x = c * self.square_size
            y = self.top_margin + r * self.square_size
            pygame.draw.rect(self.screen, (255, 0, 0), (x, y, self.square_size, self.square_size), 3)

    def draw_pieces(self):
        for coord, piece in self.rules.plateau.items():
            if piece:
                r, c = self.rules.plateau.notation_nombre(coord)
                img = self.images.get((piece.__class__.__name__, piece.couleur))
                if img:
                    self.screen.blit(img, (c * self.square_size, self.top_margin + r * self.square_size))

    def draw_message(self):
        text = self.font.render(self.message, True, (0, 0, 0))
        self.screen.blit(text, (10, 5))

    def handle_click(self, pos):
        x, y = pos
        if y < self.top_margin:
            return
        c = x // self.square_size
        r = (y - self.top_margin) // self.square_size
        if 0 <= r < 8 and 0 <= c < 8:
            coord = self.rules.plateau.notation_lettre((r, c))
            if self.selected is None:
                piece = self.rules.plateau[coord]
                if piece and piece.couleur == self.rules.current_turn:
                    self.selected = coord
            else:
                piece = self.rules.plateau[self.selected]
                if self.rules.is_valid_move(piece, self.selected, coord):
                    self.rules.execute_move(piece, self.selected, coord)
                    self.message = f"Tour des {self.rules.current_turn}"
                self.selected = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.screen.fill((200, 200, 200))
            self.draw_board()
            self.draw_pieces()
            self.draw_message()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    gui = ChessPygame()
    gui.run()

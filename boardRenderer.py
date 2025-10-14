# board_renderer.py
from __future__ import annotations
import tkinter as tk
from typing import Dict, Tuple, Any

Coord = str  # "e4", ...

class BoardRenderer:
    def __init__(
        self,
        *,
        canvas: tk.Canvas,
        rules: Any,
        piece_images: Dict[Tuple[str, str], tk.PhotoImage],
        skin: Dict[str, str],
        square_size: int,
        margin: int,
        coord_font,
        base_bg: str,
    ) -> None:
        self.canvas = canvas
        self.rules = rules
        self.piece_images = piece_images
        self.skin = skin
        self.square_size = square_size
        self.margin = margin
        self.coord_font = coord_font
        self.base_bg = base_bg

        self.squares: Dict[Coord, int] = {}
        self.pieces_items: Dict[Coord, int] = {}

    def build(self) -> None:
        """Dessine les cases + repères (a-h, 8-1) et place les pièces initiales."""
        size = self.square_size * 8
        cw = size + 2 * self.margin
        self.canvas.config(width=cw, height=cw, bg=self.base_bg, highlightthickness=0)

        for r in range(8):
            for c in range(8):
                coord = self.rules.plateau.notation_lettre((r, c))
                piece = self.rules.plateau[coord]
                color = self.skin["light_color"] if (r + c) % 2 == 0 else self.skin["dark_color"]

                x1 = self.margin + c * self.square_size
                y1 = self.margin + r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                self.squares[coord] = rect

                if piece:
                    key = (piece.__class__.__name__, piece.couleur)
                    img = self.piece_images.get(key)
                    cx = x1 + self.square_size / 2
                    cy = y1 + self.square_size / 2
                    if img:
                        pid = self.canvas.create_image(cx, cy, image=img)
                    else:
                        pid = self.canvas.create_text(cx, cy, text=str(piece))
                    self.pieces_items[coord] = pid

        # Coordonnées (a-h, 8-1)
        half = self.margin // 2
        for i in range(8):
            x  = self.margin + i * self.square_size + self.square_size / 2
            y  = self.margin + 8 * self.square_size + half
            x2 = half
            y2 = self.margin + i * self.square_size + self.square_size / 2
            self.canvas.create_text(x,  y,  text=chr(ord("a") + i), font=self.coord_font)
            self.canvas.create_text(x2, y2, text=str(8 - i),       font=self.coord_font)

    def redraw_position(self) -> None:
        """Efface/replace toutes les pièces selon self.rules.plateau."""
        for coord in list(self.squares.keys()):
            if coord in self.pieces_items:
                self.canvas.delete(self.pieces_items[coord])
                del self.pieces_items[coord]
            p = self.rules.plateau[coord]
            if p:
                key = (p.__class__.__name__, p.couleur)
                img = self.piece_images.get(key)
                row, col = self.rules.plateau.notation_nombre(coord)
                x = self.margin + col * self.square_size + self.square_size / 2
                y = self.margin + row * self.square_size + self.square_size / 2
                if img:
                    pid = self.canvas.create_image(x, y, image=img)
                else:
                    pid = self.canvas.create_text(x, y, text=str(p))
                self.pieces_items[coord] = pid

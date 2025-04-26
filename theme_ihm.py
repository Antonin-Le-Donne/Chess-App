import tkinter as tk
from tkinter import ttk

# 🎨 Palette classique
BASE_BG    = "#F5F5F5"
FRAME_BG   = "#333333"
BTN_BG     = "#444444"
ACCENT     = "#2A9D8F"
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_BODY  = ("Segoe UI", 12)

def setup_theme(root):
    style = ttk.Style(root)
    style.theme_use("default")  # Ou "clam", "alt", selon tes préférences

    # Style général
    style.configure("TFrame", background=BASE_BG)
    style.configure("TLabel", background=BASE_BG, font=FONT_BODY)
    style.configure("TButton",
        font=FONT_BODY,
        padding=8,
        background=BTN_BG,
        foreground="white"
    )
    style.map("TButton",
        background=[("active", "#555555")],
        foreground=[("active", "white")]
    )

    # Style accentué
    style.configure("Accent.TButton",
        background=ACCENT,
        foreground="white",
        font=FONT_BODY,
        padding=8
    )
    style.map("Accent.TButton",
        background=[("active", "#237F72"), ("pressed", "#237F72")],
        foreground=[("active", "white"), ("pressed", "white")]
    )

    # Style pour menu latéral
    style.configure("Menu.TFrame", background=FRAME_BG)
    style.configure("Menu.TButton",
        background=BTN_BG,
        foreground="white",
        font=FONT_BODY,
        padding=6
    )
    style.map("Menu.TButton",
        background=[("active", "#555555")],
        foreground=[("active", "white")]
    )

# move_list.py
from __future__ import annotations
import tkinter as tk

class MoveListController:
    def __init__(self, listbox: tk.Listbox) -> None:
        self.listbox = listbox
        self.moves = []
        self.number = 1

    def add(self, san: str, color: str) -> None:
        if color == "blanc":
            line = f"{self.number}. {san}"
            self.moves.append(line)
            self.listbox.insert(tk.END, line)
        else:
            if not self.moves:
                line = f"1. {san}"
                self.moves.append(line)
                self.listbox.insert(tk.END, line)
                self.number = 2
                self.listbox.yview(tk.END)
                return
            old = self.moves[-1]
            new = old + f" {san}"
            self.moves[-1] = new
            idx = self.listbox.size() - 1
            self.listbox.delete(idx)
            self.listbox.insert(idx, new)
            self.number += 1
        self.listbox.yview(tk.END)

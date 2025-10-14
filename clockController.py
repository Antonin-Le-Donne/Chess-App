# clock_controller.py
from __future__ import annotations
from typing import Callable, Any

class ClockController:
    def __init__(
        self,
        *,
        rules: Any,
        white_time: int,
        increment: int,
        on_tick: Callable[[int, int], None],  # (white, black) -> update labels
        on_flag: Callable[[str], None],       # "blanc" | "noir"
    ) -> None:
        self.rules = rules
        self.w = int(white_time)
        self.b = int(white_time)
        self.inc = int(increment)
        self.on_tick = on_tick
        self.on_flag = on_flag
        self._running = False

    def start(self, tk_root) -> None:
        if self._running:
            return
        self._running = True
        self._tick(tk_root)

    def stop(self) -> None:
        self._running = False

    def add_increment(self, color: str) -> None:
        if self.inc <= 0:
            return
        if color == "blanc":
            self.w += self.inc
        else:
            self.b += self.inc

    def _tick(self, tk_root) -> None:
        if not self._running:
            return

        if self.rules.current_turn == "blanc":
            self.w -= 1
            if self.w <= 0:
                self.on_flag("blanc")
                return
        else:
            self.b -= 1
            if self.b <= 0:
                self.on_flag("noir")
                return

        self.on_tick(self.w, self.b)
        tk_root.after(1000, lambda: self._tick(tk_root))

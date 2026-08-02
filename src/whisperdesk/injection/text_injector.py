"""
Text injection — types text into whatever app currently has focus,
as if the user typed it themselves.
"""

from pynput.keyboard import Controller


class TextInjector:
    def __init__(self):
        self._controller = Controller()

    def inject(self, text: str) -> None:
        """Types the given text at the current cursor position."""
        if not text:
            return
        self._controller.type(text)
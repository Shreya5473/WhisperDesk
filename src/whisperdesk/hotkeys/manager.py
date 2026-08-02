"""
Global hotkey listener.

Listens for a specific key combination system-wide (works even when
this app isn't the focused window) and calls user-provided callback
functions when the combo is pressed and released.
"""

from pynput import keyboard


class HotkeyManager:
    def __init__(self, hotkey: str = "<cmd>+<shift>+space"):
        self._hotkey_keys = self._parse_hotkey(hotkey)
        self._currently_pressed: set = set()
        self._is_combo_active = False

        self.on_activate = None   # callback: combo pressed down
        self.on_deactivate = None # callback: combo released

        self._listener: keyboard.Listener | None = None

    def _parse_hotkey(self, hotkey: str) -> set:
        """Convert a string like '<cmd>+<shift>+space' into a set of
        pynput Key objects we can compare against pressed keys."""
        parts = hotkey.split("+")
        keys = set()
        for part in parts:
            part = part.strip()
            if part.startswith("<") and part.endswith(">"):
                key_name = part[1:-1]
                keys.add(getattr(keyboard.Key, key_name))
            else:
                keys.add(keyboard.KeyCode.from_char(part))
        return keys

    def _on_press(self, key):
        self._currently_pressed.add(key)
        if self._hotkey_keys.issubset(self._currently_pressed) and not self._is_combo_active:
            self._is_combo_active = True
            if self.on_activate:
                self.on_activate()

    def _on_release(self, key):
        if key in self._currently_pressed:
            self._currently_pressed.discard(key)
        if self._is_combo_active and not self._hotkey_keys.issubset(self._currently_pressed):
            self._is_combo_active = False
            if self.on_deactivate:
                self.on_deactivate()

    def start(self) -> None:
        """Start listening in the background. Non-blocking — this
        returns immediately, listening continues on its own thread."""
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
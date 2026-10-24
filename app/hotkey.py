from pynput import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyListener(QObject):
    """Global push-to-talk key listener. Works even when our app isn't focused."""

    pressed = Signal()
    released = Signal()

    def __init__(self, keys):
        super().__init__()
        self._keys = set(keys)  # any of these keys triggers push-to-talk
        self._is_down = False
        self._listener: keyboard.Listener | None = None

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self._listener.start()  # runs in its own thread

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()

    def _on_press(self, key) -> None:
        # While a key is held, the OS sends repeated "press" events.
        # `_is_down` makes sure we react only to the first one.
        if key in self._keys and not self._is_down:
            self._is_down = True
            self.pressed.emit()

    def _on_release(self, key) -> None:
        if key in self._keys and self._is_down:
            self._is_down = False
            self.released.emit()
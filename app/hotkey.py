from pynput import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyListener(QObject):
    """Global hotkey listener. Supports hold (push-to-talk) and toggle modes."""

    pressed = Signal()   # means "start recording"
    released = Signal()  # means "stop recording"

    def __init__(self, keys, toggle: bool = False):
        super().__init__()
        self._keys = set(keys)
        self._toggle = toggle
        self._is_down = False   # physical key state (filters auto-repeat)
        self._active = False    # toggle mode: are we currently "recording"?
        self._listener: keyboard.Listener | None = None

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()

    def _on_press(self, key) -> None:
        if key in self._keys and not self._is_down:
            self._is_down = True
            if self._toggle:
                # Every physical press flips the state.
                self._active = not self._active
                if self._active:
                    self.pressed.emit()
                else:
                    self.released.emit()
            else:
                self.pressed.emit()

    def _on_release(self, key) -> None:
        if key in self._keys and self._is_down:
            self._is_down = False
            if not self._toggle:
                self.released.emit()
import sys
import threading
import time

import pyperclip
from pynput.keyboard import Controller, Key


class TextInjector:
    """Inserts text into whatever window currently has the cursor."""

    def __init__(self):
        self._kb = Controller()
        # Paste shortcut: Cmd+V on macOS, Ctrl+V elsewhere.
        self._mod = Key.cmd if sys.platform == "darwin" else Key.ctrl

    def paste(self, text: str) -> None:
        # Run in a thread so the small sleeps never block the UI.
        threading.Thread(target=self._paste, args=(text,), daemon=True).start()

    def _paste(self, text: str) -> None:
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = None

        pyperclip.copy(text + " ")  # trailing space so dictation can continue
        time.sleep(0.05)            # let the clipboard update

        with self._kb.pressed(self._mod):
            self._kb.press("v")
            self._kb.release("v")

        time.sleep(0.25)            # let the target app read the clipboard
        if old_clipboard is not None:
            pyperclip.copy(old_clipboard)  # restore what the user had copied
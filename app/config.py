from dataclasses import dataclass

from pynput import keyboard


@dataclass
class Config:
    # Right Alt is reported as alt_r or alt_gr depending on keyboard layout.
    hotkeys: tuple = (keyboard.Key.alt_r, keyboard.Key.alt_gr)

    # True: press once to start, press again to stop.
    # False: hold the key while speaking (push-to-talk).
    toggle_mode: bool = True

    # English-only model
    model_name: str = "small.en"
    language: str = "en"

    sample_rate: int = 16000
    min_seconds: float = 0.4
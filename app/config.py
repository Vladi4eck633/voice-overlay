from dataclasses import dataclass

from pynput import keyboard


@dataclass
class Config:
    # Push-to-talk keys. Hold to record, release to transcribe.
    # Right Alt is reported as alt_r or alt_gr depending on keyboard layout,
    # so we accept both.
    hotkeys: tuple = (keyboard.Key.alt_r, keyboard.Key.alt_gr)

    # Whisper model. "small.en" = English-only, good quality/speed balance.
    # Alternatives: "tiny.en" (fastest), "base.en", "medium.en" (most accurate).
    model_name: str = "small.en"
    language: str = "en"

    # Whisper expects 16 kHz mono audio.
    sample_rate: int = 16000

    # Recordings shorter than this are ignored (accidental key taps).
    min_seconds: float = 0.4
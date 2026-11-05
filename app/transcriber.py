import threading

import numpy as np
from PySide6.QtCore import QObject, Signal


class Transcriber(QObject):
    """Wraps faster-whisper. Loading and inference run in background threads."""

    ready = Signal()
    text_ready = Signal(str)
    failed = Signal(str)

    def __init__(self, model_name: str, language: str):
        super().__init__()
        self.model_name = model_name
        self.language = language
        self._model = None

    def load_async(self) -> None:
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self) -> None:
        try:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_name, device="auto", compute_type="int8"
            )
            self.ready.emit()
        except Exception as e:
            self.failed.emit(f"Model load failed: {e}")

    def transcribe_async(self, audio: np.ndarray) -> None:
        threading.Thread(target=self._run, args=(audio,), daemon=True).start()

    def _run(self, audio: np.ndarray) -> None:
        try:
            segments, _info = self._model.transcribe(
                audio,
                language=self.language,
                beam_size=5,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            text = " ".join(s.text.strip() for s in segments).strip()
            self.text_ready.emit(text)
        except Exception as e:
            self.failed.emit(f"Transcription failed: {e}")
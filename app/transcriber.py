import threading

import numpy as np
from PySide6.QtCore import QObject, Signal


class Transcriber(QObject):
    """Wraps faster-whisper. Loading and inference run in background threads."""

    ready = Signal()          # model loaded
    text_ready = Signal(str)  # transcription finished
    failed = Signal(str)      # something went wrong (message for the user)

    def __init__(self, model_name: str, language: str):
        super().__init__()
        self.model_name = model_name
        self.language = language
        self._model = None

    # ---- model loading -------------------------------------------------
    def load_async(self) -> None:
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self) -> None:
        try:
            # Imported here so the UI appears before the heavy import happens.
            from faster_whisper import WhisperModel

            # device="auto": GPU if CUDA is available, otherwise CPU.
            # int8: quantized weights, much faster on CPU with tiny quality loss.
            self._model = WhisperModel(
                self.model_name, device="auto", compute_type="int8"
            )
            self.ready.emit()
        except Exception as e:
            self.failed.emit(f"Model load failed: {e}")

    # ---- inference -----------------------------------------------------
    def transcribe_async(self, audio: np.ndarray) -> None:
        threading.Thread(target=self._run, args=(audio,), daemon=True).start()

    def _run(self, audio: np.ndarray) -> None:
        try:
            segments, _info = self._model.transcribe(
                audio,
                language=self.language,
                beam_size=5,
                vad_filter=True,  # cut silence, reduces hallucinations
                condition_on_previous_text=False,
            )
            # `segments` is a lazy generator: the real work happens during iteration.
            text = " ".join(s.text.strip() for s in segments).strip()
            self.text_ready.emit(text)
        except Exception as e:
            self.failed.emit(f"Transcription failed: {e}")
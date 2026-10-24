import threading

import numpy as np
import sounddevice as sd
from PySide6.QtCore import QObject, Signal


class Recorder(QObject):
    """Records microphone audio while active and reports the input loudness."""

    # Emitted from the audio thread with the current loudness (RMS, 0..~0.3).
    level = Signal(float)

    def __init__(self, sample_rate: int = 16000):
        super().__init__()
        self.sample_rate = sample_rate
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Open the microphone and start collecting audio."""
        with self._lock:
            self._chunks = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._on_audio,
        )
        self._stream.start()

    def _on_audio(self, indata, frames, time_info, status) -> None:
        # Called by PortAudio in a separate thread every few milliseconds.
        chunk = indata[:, 0].copy()  # copy: PortAudio reuses the buffer
        with self._lock:
            self._chunks.append(chunk)
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        self.level.emit(rms)

    def stop(self) -> np.ndarray:
        """Close the microphone and return everything recorded (float32 mono)."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._chunks:
                return np.zeros(0, dtype=np.float32)
            return np.concatenate(self._chunks)
from PySide6.QtCore import QObject, Qt, Slot

from app.config import Config
from app.hotkey import HotkeyListener
from app.injector import TextInjector
from app.overlay import Overlay, State
from app.recorder import Recorder
from app.transcriber import Transcriber


class Controller(QObject):
    """Glues everything together: hotkey -> record -> transcribe -> paste."""

    def __init__(self, overlay: Overlay, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.overlay = overlay

        self.recorder = Recorder(cfg.sample_rate)
        self.transcriber = Transcriber(cfg.model_name, cfg.language)
        self.injector = TextInjector()
        self.hotkey = HotkeyListener(cfg.hotkeys)

        self._model_ready = False
        self._recording = False
        self._busy = False  # True while a transcription is running

        # Signals from background threads -> our slots (run in the Qt main thread).
        self.hotkey.pressed.connect(self._on_press, Qt.QueuedConnection)
        self.hotkey.released.connect(self._on_release, Qt.QueuedConnection)
        self.recorder.level.connect(self.overlay.set_level, Qt.QueuedConnection)
        self.transcriber.ready.connect(self._on_model_ready, Qt.QueuedConnection)
        self.transcriber.text_ready.connect(self._on_text, Qt.QueuedConnection)
        self.transcriber.failed.connect(self._on_error, Qt.QueuedConnection)

    def start(self) -> None:
        self.overlay.set_state(State.LOADING, "Loading model…")
        self.transcriber.load_async()
        self.hotkey.start()

    def stop(self) -> None:
        self.hotkey.stop()

    # ---- slots ---------
    @Slot()
    def _on_model_ready(self) -> None:
        self._model_ready = True
        self.overlay.flash("Ready: hold Right Alt and speak", 2000)

    @Slot()
    def _on_press(self) -> None:
        if not self._model_ready:
            self.overlay.flash("Model is still loading…")
            return
        if self._busy or self._recording:
            return
        try:
            self.recorder.start()
        except Exception as e:
            self.overlay.flash(f"Mic error: {e}", 3000)
            return
        self._recording = True
        self.overlay.set_state(State.RECORDING)

    @Slot()
    def _on_release(self) -> None:
        if not self._recording:
            return
        self._recording = False
        audio = self.recorder.stop()

        if len(audio) / self.cfg.sample_rate < self.cfg.min_seconds:
            self.overlay.set_state(State.HIDDEN)  # too short, ignore
            return

        self._busy = True
        self.overlay.set_state(State.PROCESSING, "Transcribing…")
        self.transcriber.transcribe_async(audio)

    @Slot(str)
    def _on_text(self, text: str) -> None:
        self._busy = False
        if text:
            self.injector.paste(text)
            self.overlay.flash("Done", 600)
        else:
            self.overlay.flash("Nothing heard", 1200)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self._busy = False
        self._recording = False
        self.overlay.flash(message, 4000)
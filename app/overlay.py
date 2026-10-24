import math
from enum import Enum, auto

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Slot
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QWidget


class State(Enum):
    HIDDEN = auto()
    LOADING = auto()
    RECORDING = auto()
    PROCESSING = auto()
    MESSAGE = auto()


class Overlay(QWidget):
    """Small always-on-top pill that shows the current status."""

    W, H = 270, 56

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint        # no title bar / borders
            | Qt.WindowStaysOnTopHint     # above other windows
            | Qt.Tool                     # no taskbar entry
            | Qt.WindowDoesNotAcceptFocus # never steal focus from the target app
        )
        self.setAttribute(Qt.WA_TranslucentBackground)   # allows rounded corners
        self.setAttribute(Qt.WA_ShowWithoutActivating)   # show without focusing
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # clicks pass through
        self.resize(self.W, self.H)

        self._state = State.HIDDEN
        self._text = ""
        self._level = 0.0   # smoothed, drawn
        self._target = 0.0  # latest raw value
        self._angle = 0.0   # animation phase

        # ~30 FPS animation timer (runs only while the overlay is visible).
        self._anim = QTimer(self)
        self._anim.setInterval(33)
        self._anim.timeout.connect(self._tick)

        # Auto-hide timer for short messages.
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(lambda: self.set_state(State.HIDDEN))

    # ---- public API ----------------------------------------------------
    def set_state(self, state: State, text: str = "") -> None:
        self._hide_timer.stop()
        self._state = state
        self._text = text
        if state == State.HIDDEN:
            self._anim.stop()
            self.hide()
            return
        self._place()
        self.show()
        self._anim.start()
        self.update()

    def flash(self, text: str, ms: int = 1200) -> None:
        """Show a message and hide it automatically."""
        self.set_state(State.MESSAGE, text)
        self._hide_timer.start(ms)

    @Slot(float)
    def set_level(self, rms: float) -> None:
        self._target = min(1.0, rms * 10)  # speech RMS is ~0.01-0.1, scale to 0..1

    # ---- internals -----------------------------------------------------
    def _place(self) -> None:
        """Bottom center of the primary screen, above the taskbar."""
        area = QGuiApplication.primaryScreen().availableGeometry()
        x = area.x() + (area.width() - self.W) // 2
        y = area.y() + area.height() - self.H - 40
        self.move(x, y)

    def _tick(self) -> None:
        # Exponential smoothing so the level bar doesn't jitter.
        self._level += (self._target - self._level) * 0.35
        self._angle = (self._angle + 12) % 360
        self.update()  # schedule paintEvent

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Background pill
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(24, 24, 28, 235))
        p.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        font = QFont()
        font.setPointSize(11)
        p.setFont(font)
        text_color = QColor(235, 235, 240)
        cy = self.H / 2

        if self._state == State.RECORDING:
            # Pulsing red dot
            pulse = 0.65 + 0.35 * math.sin(math.radians(self._angle * 2))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 70, 70, int(255 * pulse)))
            p.drawEllipse(QPointF(30, cy), 7, 7)

            p.setPen(text_color)
            p.drawText(QRectF(50, 0, 100, self.H), Qt.AlignVCenter | Qt.AlignLeft, "Listening")

            # Level bar: gray track + red fill
            bar_x, bar_w = 150, 95
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 40))
            p.drawRoundedRect(QRectF(bar_x, cy - 3, bar_w, 6), 3, 3)
            p.setBrush(QColor(255, 90, 90))
            p.drawRoundedRect(QRectF(bar_x, cy - 3, max(6.0, bar_w * self._level), 6), 3, 3)

        elif self._state in (State.LOADING, State.PROCESSING):
            # Spinner: a rotating arc
            pen = QPen(QColor(120, 170, 255), 3)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawArc(QRectF(22, cy - 9, 18, 18), int(-self._angle * 16), 100 * 16)

            p.setPen(text_color)
            p.drawText(QRectF(52, 0, self.W - 64, self.H), Qt.AlignVCenter | Qt.AlignLeft, self._text)

        elif self._state == State.MESSAGE:
            p.setPen(text_color)
            p.drawText(rect, Qt.AlignCenter, self._text)

        p.end()
import signal
import sys

from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from app.config import Config
from app.controller import Controller
from app.overlay import Overlay


def make_tray_icon() -> QIcon:
    """Draw a simple red-dot icon in code, so we don't need an image file."""
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(255, 70, 70))
    p.setPen(QColor(0, 0, 0, 0))
    p.drawEllipse(10, 10, 44, 44)
    p.end()
    return QIcon(pix)


def main() -> int:
    app = QApplication(sys.argv)
    # We have no normal window, so don't quit when the overlay is hidden.
    app.setQuitOnLastWindowClosed(False)
    # Let Ctrl+C in the terminal stop the app.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    cfg = Config()
    overlay = Overlay()
    controller = Controller(overlay, cfg)

    # Tray icon with a Quit entry (the only way to close the app otherwise).
    tray = QSystemTrayIcon(make_tray_icon(), app)
    tray.setToolTip("Voice Overlay")
    menu = QMenu()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()

    app.aboutToQuit.connect(controller.stop)
    controller.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

    
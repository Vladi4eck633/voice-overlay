import signal
import sys

from PySide6.QtGui import QAction, QActionGroup, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from app.config import Config
from app.controller import Controller
from app.overlay import Overlay


def make_tray_icon() -> QIcon:
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
    app.setQuitOnLastWindowClosed(False)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    cfg = Config()
    overlay = Overlay()
    controller = Controller(overlay, cfg)

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
    print("started: look for the red dot in the tray", flush=True)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
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
    # Model submenu with radio-style items
    model_menu = menu.addMenu("Model")
    group = QActionGroup(model_menu)
    group.setExclusive(True)
    model_actions = {}

    def on_model_chosen(name: str) -> None:
        if not controller.set_model(name):
            # Switch was refused: put the check mark back on the model in use
            model_actions[controller.transcriber.model_name].setChecked(True)

    for name, label in cfg.models:
        act = QAction(f"{label}  ({name})", model_menu)
        act.setCheckable(True)
        act.setChecked(name == cfg.model_name)
        act.triggered.connect(lambda checked=False, n=name: on_model_chosen(n))
        group.addAction(act)
        model_menu.addAction(act)
        model_actions[name] = act
    menu.addSeparator()
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()

    app.aboutToQuit.connect(controller.stop)
    controller.start()
    print("started: look for the red dot in the tray", flush=True)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
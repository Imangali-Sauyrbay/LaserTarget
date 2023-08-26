import sys
from os import path
import pyautogui

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QCheckBox, QMessageBox
from PyQt5.QtGui import QIcon

from .sub_windows import ConfigDLG
from ..start_tracker import Tracker
from ..configs import Config
from ..controller import Controller
from ..utils import check_if_cams_available, show_cam_not_found_warn


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Захват Лазера'
        w, h = pyautogui.size()
        self.width = 250
        self.height = 200
        self.left = int((w / 2) - (self.width / 2))
        self.top = int((h / 2) - (self.height / 2))
        self.config = Config.get_instance()

        self.btn_start = QPushButton('Start', self)
        self.btn_conf = QPushButton('Откалибровать', self)
        self.about_lbl = QLabel(self)
        self.is_pseye = QCheckBox('Камера Ps3Eye', self)

        self.tracker = Tracker(parent=self)
        self.tracker.started.connect(self.toggle_handler(False, 'Stop'))
        self.tracker.stopped.connect(self.toggle_handler(True, 'Start'))

        self.cont = Controller(self.tracker)

        self.config_dlg = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.move(self.left, self.top)
        self.setFixedSize(self.width, self.height)

        self.setWindowIcon(QIcon(path.abspath(path.join(path.dirname(__file__), '..', 'assets', 'icon.ico'))))

        self.btn_start.move(int((self.width / 2) - (self.btn_start.width() / 2)), int(.20 * self.height))
        self.btn_start.clicked.connect(lambda: self.tracker.toggle())

        self.btn_conf.move(int((self.width / 2) - (self.btn_conf.width() / 2)), int(.45 * self.height))
        self.btn_conf.clicked.connect(self.show_config_window)

        self.is_pseye.setCheckState(2 if self.config.get('is_pseye') else 0)
        self.is_pseye.move(int((self.width / 2) - (self.is_pseye.width() / 2)), int(.65 * self.height))
        self.is_pseye.stateChanged.connect(self.toggle_pseye)

        self.about_lbl.setText('IP19-3tk Sauyrbai Imangali 2020-2022')
        self.about_lbl.setStyleSheet('font-size:11px; color: gray;')
        self.about_lbl.resize(185, 30)
        self.about_lbl.move(int((self.width / 2) - (self.about_lbl.width() / 2)), int(.80 * self.height))

        self.show()

    def show_config_window(self):
        if not check_if_cams_available(self.config.get('is_pseye')):
            return show_cam_not_found_warn(self)

        self.config_dlg = ConfigDLG(self)
        self.btn_conf.setEnabled(False)
        self.config_dlg.on_close.connect(self.config_dlg_closed)

    def config_dlg_closed(self):
        self.btn_conf.setEnabled(True)

    def toggle_pseye(self, state):
        self.config.set('is_pseye', True if state else False)
        self.config.save()

    def toggle_handler(self, btn_state, text):
        def _inner():
            self.btn_start.setText(text)
            self.btn_conf.setEnabled(btn_state)
            self.is_pseye.setEnabled(btn_state)
        return _inner

    def closeEvent(self, e) -> None:
        super(App, self).closeEvent(e)
        if self.tracker is not None and self.tracker.is_running:
            self.tracker.stop()


def _init():
    app = QApplication(sys.argv)
    App()
    app.exec()


if __name__ == '__main__':
    _init()

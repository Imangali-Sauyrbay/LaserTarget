from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from ..configs import Config
from ..components import QMoveButton


class Points(QWidget):
    pointMovedSignal = pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        super(Points, self).__init__(*args, **kwargs)
        self.config = Config.get_instance()
        self.points = []

        self.init_points()

    def init_points(self):
        for i in range(1, 5):
            btn = QMoveButton(str(i), self.parent())
            self.points.append(btn)
            btn.resize(14, 14)
            btn.setStyleSheet('border-radius: 7px; border: 1px solid black; background-color: #ccc; font-size: 8px')
            btn.movedSignal.connect(self.btn_moved_handler(i - 1))
        self.calc_positions()

    def calc_positions(self):
        (w, h) = (self.parent().width(), self.parent().height())

        for i in range(1, 5):
            data = self.config.get('point_' + str(i))
            point = self.points[i - 1]
            if data is None:
                return

            length = point.width()
            x = int((data[0] * w) - (length / 2))
            y = int((data[1] * h) - (length / 2))
            point.setGeometry(x, y, length, length)

    def get_cords(self):
        res = []

        for i in self.points:
            length = i.width() / 2
            res.append((int(i.pos().x() + length), int(i.pos().y() + length)))

        return res

    def btn_moved_handler(self, btn_id):
        return lambda: self.pointMovedSignal.emit(
            (
                (
                    self.points[btn_id].pos().x() + int(self.points[btn_id].width() / 2),
                    self.points[btn_id].pos().y() + int(self.points[btn_id].width() / 2)
                ),
                btn_id
            )
        )

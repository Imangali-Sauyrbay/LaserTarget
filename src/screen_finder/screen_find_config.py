from PyQt5.QtWidgets import QGridLayout, QLabel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from .points import Points
from ..configs import Config
from ..utils import clamp


class ScreenFindLabel(QLabel):
    def __init__(self, points=[], *args, **kwargs):
        super(ScreenFindLabel, self).__init__(*args, **kwargs)
        self.points = points

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(Qt.red))

        for i in range(len(self.points)):
            x, y = self.points[i]
            to_x, to_y = self.points[i + 1 if (i < (len(self.points) - 1)) else 0]
            painter.drawLine(x, y, to_x, to_y)

    def update_lines(self, points):
        self.points = points
        self.update()


class ScreenFindConfig(QGridLayout):
    def __init__(self, *args, **kwargs):
        super(ScreenFindConfig, self).__init__(*args, **kwargs)
        self.config = Config.get_instance()
        self.setContentsMargins(0, 0, 0, 0)
        self.lbl = ScreenFindLabel()
        self.points = Points(self.lbl)
        self.addWidget(self.lbl)

        self.points.pointMovedSignal.connect(self.points_moved_handler)

    def update_lines(self):
        self.lbl.update_lines(self.points.get_cords())

    def update_dots(self):
        self.points.calc_positions()

    def points_moved_handler(self, data):
        pos, _id = data
        x, y = pos
        self.config.set('point_' + str(_id + 1), [
            clamp(x / self.lbl.width(), 0, 1),
            clamp(y / self.lbl.height(), 0, 1)
        ])
        self.update_lines()

    def get_cords(self, w, h):
        res = []
        for i in range(1, 5):
            point = self.config.get('point_' + str(i))
            res.append([point[0] * w, point[1] * h])
        return res

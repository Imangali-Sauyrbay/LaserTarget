from PyQt5.QtCore import QThread, pyqtSlot
from pyautogui import moveTo, size
from ....utils import cool_down, get_normalized_x, get_normalized_y


@cool_down
def mouse_move(x, y):
    moveTo(x, y)


class HandleTestTh(QThread):
    def __init__(self, screen_conf, *args, **kwargs):
        super(HandleTestTh, self).__init__(*args, **kwargs)
        self.screen_conf = screen_conf

    @pyqtSlot(tuple)
    def handle_testing(self, data):
        point, frame = data
        h, w, _ = frame
        points = self.screen_conf.get_cords(w, h)
        if point:
            coord = point[0]
            if coord:
                sw, sh = size()
                sx = get_normalized_x(points, coord, sw)
                sy = get_normalized_y(points, coord, sh)
                if sx is not None and sy is not None:
                    mouse_move(sx, sy)

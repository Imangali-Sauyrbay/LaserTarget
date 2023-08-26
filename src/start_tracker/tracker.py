import pyautogui

from PyQt5.QtCore import pyqtSignal, QObject

from ..configs import Config
from ..utils import get_normalized_y, get_normalized_x, cool_down, check_if_cams_available, show_cam_not_found_warn
# from ..laser_tracker import CV2VideoCapture, PSEyeVideoCapture
from ..laser_tracker import CV2VideoCapture


@cool_down
def _click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()


class Tracker(QObject):
    started = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Tracker, self).__init__(*args, **kwargs)
        self.config = Config.get_instance()
        self.is_running = False
        self.th = None

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def start(self):
        is_pseye = self.config.get('is_pseye')
        if not check_if_cams_available(is_pseye):
            return show_cam_not_found_warn(self.parent())

        # self.th = PSEyeVideoCapture(should_stream=False) if is_pseye else CV2VideoCapture(should_stream=False)
        self.th = CV2VideoCapture(should_stream=False)
        self.th.change_data.connect(self.handle_data_update)
        self.th.start()
        self.is_running = True
        self.started.emit()

    def stop(self):
        self.th.change_data.disconnect(self.handle_data_update)
        self.th.stop()
        self.is_running = False
        self.stopped.emit()

    def handle_data_update(self, data):
        point, frame = data
        h, w, _ = frame
        points = self.get_points(w, h)
        if point:
            coord = point[0]
            if coord:
                sw, sh = pyautogui.size()
                sx = get_normalized_x(points, coord, sw)
                sy = get_normalized_y(points, coord, sh)
                if sx is not None and sy is not None:
                    _click(sx, sy)

    def get_points(self, w, h):
        p = []
        for i in range(1, 5):
            point = self.config.get('point_' + str(i))
            p.append([point[0] * w, point[1] * h])
        return p

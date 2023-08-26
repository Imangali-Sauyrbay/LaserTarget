from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage
from ...laser_tracker import LaserTracker
from ...configs import Config
from ...utils import apply_saturation, apply_brightness, apply_contrast, apply_zoom


class AbstractVideoCapture(QThread):
    changePixmap = pyqtSignal(QImage)
    layers_pixmap = pyqtSignal(dict)
    change_data = pyqtSignal(tuple)

    changeCurrentCamera = pyqtSignal()
    changeResolution = pyqtSignal()

    cap = None

    def __init__(self, mutex=None, condition=None, should_stream=True):
        super().__init__()
        self.mutex = mutex
        self.condition = condition
        self.tracker = LaserTracker()
        self.is_running = True
        self.should_stream = should_stream
        self.config = Config.get_instance()
        self.change_camera()
        self.update_camera_config()

    def run(self):
        while self.is_running:
            if not self.cap:
                continue

            ret, frame = self.get_frame()

            if ret:
                frame = apply_zoom(
                    frame=frame,
                    zoom=self.config.get('zoom'),
                    interpolation=self.get_interpolation()
                )

                if self.config.get('is_saturation_on'):
                    frame = apply_saturation(frame, self.config.get('saturation'))

                if self.config.get('is_brightness_on'):
                    frame = apply_brightness(frame, self.config.get('brightness'))

                if self.config.get('is_contrast_on'):
                    frame = apply_contrast(frame, self.config.get('contrast'))

                (data, frame, channels) = self.tracker.get_data(frame)

                if self.should_stream:
                    frame = self.last_frame_manipulation(frame)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
                    self.layers_pixmap.emit(channels)
                    self.condition.wait(self.mutex)
                self.change_data.emit((data, frame.shape))
        else:
            self.release_capture()

    def get_interpolation(self):
        return self.config.get('interp')

    '''
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    '''
    def last_frame_manipulation(self, frame):
        raise Exception('method not implemented!')

    def _init(self):
        raise Exception('method not implemented!')

    def release_capture(self):
        raise Exception('method not implemented!')

    def get_frame(self):
        raise Exception('method not implemented!')

    def change_camera(self):
        raise Exception('method not implemented!')

    def update_camera_config(self):
        raise Exception('method not implemented!')

    def stop(self):
        self.is_running = False
        self.quit()

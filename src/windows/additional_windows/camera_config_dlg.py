from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
from ...components import QNamedSlider
from ...configs import Config


class CameraConfigDLG(QDialog):
    brightness_slider = None
    vbl = None
    contrast_slider = None
    sat_slider = None
    hue_slider = None

    def __init__(self, parent, thread):
        super(CameraConfigDLG, self).__init__(parent=parent)
        self.config = Config.get_instance()
        self.th = thread
        self.title = 'Калибровка Камеры'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.vbl = QVBoxLayout()
        self.vbl.setAlignment(Qt.AlignTop)

        if self.config.get('is_pseye'):
            self.gain_slider = QNamedSlider(
                name='Gain',
                on_changed_cb=lambda val: self.set_conf('pseye_gain', val),
                parent_layout=self.vbl,
                value=self.config.get('pseye_gain'),
                _max=63
            )

            self.exposure_slider = QNamedSlider(
                name='Exposure',
                on_changed_cb=lambda val: self.set_conf('pseye_exposure', val),
                parent_layout=self.vbl,
                value=self.config.get('pseye_exposure'),
                _max=255
            )

            self.rb_slider = QNamedSlider(
                name='Red Balance',
                on_changed_cb=lambda val: self.set_conf('red_balance', val),
                parent_layout=self.vbl,
                value=self.config.get('red_balance'),
                _max=255
            )

            self.gb_slider = QNamedSlider(
                name='Green Balance',
                on_changed_cb=lambda val: self.set_conf('green_balance', val),
                parent_layout=self.vbl,
                value=self.config.get('green_balance'),
                _max=255
            )

            self.bb_slider = QNamedSlider(
                name='Blue Balance',
                on_changed_cb=lambda val: self.set_conf('blue_balance', val),
                parent_layout=self.vbl,
                value=self.config.get('blue_balance'),
                _max=255
            )

        else:
            # Brightness
            self. brightness_slider = QNamedSlider(
                name='Яркость',
                on_changed_cb=lambda val: self.set_conf('camera_brightness', val),
                parent_layout=self.vbl,
                value=self.config.get('camera_brightness'),
            )

            # Contrast
            self.contrast_slider = QNamedSlider(
                name='Контраст',
                on_changed_cb=lambda val: self.set_conf('camera_contrast', val),
                parent_layout=self.vbl,
                value=self.config.get('camera_contrast'),
            )

            # Sat
            self.sat_slider = QNamedSlider(
                name='Насыщенность',
                on_changed_cb=lambda val: self.set_conf('camera_sat', val),
                parent_layout=self.vbl,
                value=self.config.get('camera_sat'),
            )

            # hue
            self.hue_slider = QNamedSlider(
                name='Цвет',
                on_changed_cb=lambda val: self.set_conf('camera_hue', val),
                parent_layout=self.vbl,
                value=self.config.get('camera_hue'),
            )

        self.setLayout(self.vbl)
        self.show()

    def set_conf(self, key, val):
        self.config.set(key, val)
        self.th.update_camera_config()

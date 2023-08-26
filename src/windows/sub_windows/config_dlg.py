import sys
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QSpinBox,
    QColorDialog,
    QMessageBox,
)
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QMutex, QWaitCondition
from PyQt5.QtGui import QImage, QPixmap, QColor

# from ...laser_tracker import CV2VideoCapture, PSEyeVideoCapture
from ...laser_tracker import CV2VideoCapture
from ...utils import list_of_cams
from ...components import QNamedSlider
from ...configs import Config
from ...screen_finder import ScreenFindConfig
from ..additional_windows import AdditionalInfos, CameraConfigDLG
from .threads import HandleTestTh


class ConfigDLG(QDialog):
    on_close = pyqtSignal()
    th = None
    zoom_slider = None
    brightness_slider = None
    contrast_slider = None
    saturation_slider = None

    def __init__(self, parent):
        super(ConfigDLG, self).__init__(parent=parent)
        self.config = Config.get_instance()
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.title = 'Калибровка'
        self.left = 100
        self.top = 100
        self.width = 1280
        self.height = 480
        self.is_testing = False
        self.init_ui()
        self.last_width = None
        self.last_height = None

    @pyqtSlot(QImage)
    def set_image(self, image: QImage):
        self.mutex.lock()
        try:
            self.label.setPixmap(QPixmap.fromImage(image))
            w = self.label.width()
            h = self.label.height()
            if w != self.last_width or h != self.last_height:
                self.screen_conf.update_dots()
                self.screen_conf.update_lines()
                self.last_width = w
                self.last_height = h
        finally:
            self.mutex.unlock()
            self.condition.wakeAll()

    @pyqtSlot(tuple)
    def set_data(self, data):
        coords_text = 'Координаты лазера: '
        rad_text = 'Радиус лазера: '
        res_text = 'Качество кадра: '
        data, shape = data
        if data:
            center, rad = data

            if center:
                coords_text += f"x: {center[0]}; y: {center[1]};"

            else:
                coords_text += f"x: none; y: none;"

            if rad:
                rad_text += str(int(rad))
            else:
                rad_text += 'none;'
        else:
            coords_text += f"x: none; y: none;"
            rad_text += 'none;'

        res_text += f"{shape[1]}x{shape[0]};"

        self.center_info.setText(coords_text)
        self.rad_info.setText(rad_text)
        self.res_info.setText(res_text)

    def init_ui(self):
        is_pseye = self.config.get('is_pseye')
        self.mutex.lock()
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.hbl_main_conf = QHBoxLayout()
        self.vbl_main_hbl_video = QVBoxLayout()
        self.vbl_main_hbl_video.setAlignment(Qt.AlignTop)
        self.vbl_main_hbl_conf = QVBoxLayout()
        self.vbl_main_hbl_conf.setAlignment(Qt.AlignTop)

        # Video label

        self.label = QLabel()
        self.label.resize(int(self.width / 2), self.height)
        self.vbl_main_hbl_video.addWidget(self.label)

        # Label points
        self.screen_conf = ScreenFindConfig()
        self.label.setLayout(self.screen_conf)

        # camera select
        self.camera_select_box = QComboBox()
        self.update_camera_list()
        _id = self.camera_select_box.findData(self.config.get('camera'))
        if _id != -1:
            self.camera_select_box.setCurrentIndex(_id)
        self.camera_select_box.currentIndexChanged.connect(self.camera_idx_changed)
        self.vbl_main_hbl_conf.addWidget(self.camera_select_box)

        # resolution select
        if not is_pseye:
            self.resolution_select = QComboBox()
            self.update_resolution_list()
            _id = self.resolution_select.findData(self.config.get('selected_resolution'))
            if _id != -1:
                self.resolution_select.setCurrentIndex(_id)
            self.resolution_select.currentIndexChanged.connect(self.resolution_changed)
            self.vbl_main_hbl_conf.addWidget(self.resolution_select)

        # zoom
        self.zoom_slider = QNamedSlider(
            name='Zoom',
            on_changed_cb=lambda val: self.set_conf('zoom', val),
            parent_layout=self.vbl_main_hbl_conf,
            value=self.config.get('zoom'),
            _min=1,
            _max=10,
            step=0.1,
            is_float=True
        )

        # brightness
        self.brightness_slider = QNamedSlider(
            name='Яркость',
            on_changed_cb=lambda val: self.set_conf('brightness', val),
            parent_layout=self.vbl_main_hbl_conf,
            value=self.config.get('brightness'),
            _min=-200,
            _max=200,
            step=1,
            can_be_offed=True,
            initial_state=self.config.get('is_brightness_on'),
            checked_cb=lambda state: self.config.set('is_brightness_on', state)
        )

        # Contrast
        self.contrast_slider = QNamedSlider(
            name='Контраст',
            on_changed_cb=lambda val: self.set_conf('contrast', val),
            parent_layout=self.vbl_main_hbl_conf,
            value=self.config.get('contrast'),
            _min=-90,
            _max=90,
            step=1,
            can_be_offed=True,
            initial_state=self.config.get('is_contrast_on'),
            checked_cb=lambda state: self.config.set('is_contrast_on', state)
        )

        # Saturation
        self.saturation_slider = QNamedSlider(
            name='Насыщенность',
            on_changed_cb=lambda val: self.set_conf('saturation', val),
            parent_layout=self.vbl_main_hbl_conf,
            value=self.config.get('saturation'),
            _min=0,
            _max=5,
            step=0.1,
            is_float=True,
            can_be_offed=True,
            initial_state=self.config.get('is_saturation_on'),
            checked_cb=lambda state: self.config.set('is_saturation_on', state)
        )


        # interpolation select
        self.select_interpolation = QComboBox()
        self.updata_interpolation_list()
        self.select_interpolation.currentIndexChanged.connect(self.interpolation_changed)
        _id = self.select_interpolation.findData(self.config.get('interp'))
        if _id != -1:
            self.select_interpolation.setCurrentIndex(_id)
        self.vbl_main_hbl_conf.addWidget(self.select_interpolation)

        # Color Buttons
        self.color_btns_hbl = QHBoxLayout()

        self.lower_color_btn = QPushButton('Нижняя граница цвета')
        self.lower_color_btn.clicked.connect(self.set_lower_color)
        self.color_btns_hbl.addWidget(self.lower_color_btn)

        self.upper_color_btn = QPushButton('Верхняя граница цвета')
        self.upper_color_btn.clicked.connect(self.set_upper_color)
        self.color_btns_hbl.addWidget(self.upper_color_btn)

        self.vbl_main_hbl_conf.addLayout(self.color_btns_hbl)

        # Radius MIN
        self.radius_hbl = QHBoxLayout()
        self.radius_hbl.setAlignment(Qt.AlignLeft)

        self.radius_min_spinbox_label = QLabel()
        self.radius_min_spinbox_label.setText('Выберите мин. радиус точки:')
        self.radius_hbl.addWidget(self.radius_min_spinbox_label)

        self.radius_min_spinbox = QSpinBox()
        self.radius_min_spinbox.setSingleStep(1)
        self.radius_min_spinbox.setMinimum(0)
        self.radius_min_spinbox.setValue(self.config.get('min_dot_rad'))
        self.radius_min_spinbox.setMinimumWidth(50)
        self.radius_min_spinbox.valueChanged.connect(self.min_dot_rad_changed)
        self.radius_hbl.addWidget(self.radius_min_spinbox)

        # Radius MAX

        self.radius_max_spinbox_label = QLabel()
        self.radius_max_spinbox_label.setText('макс. радиус точки:')
        self.radius_hbl.addWidget(self.radius_max_spinbox_label)

        self.radius_max_spinbox = QSpinBox()
        self.radius_max_spinbox.setSingleStep(1)
        self.radius_max_spinbox.setMinimum(0)
        self.radius_max_spinbox.setValue(self.config.get('max_dot_rad'))
        self.radius_max_spinbox.setMinimumWidth(50)
        self.radius_max_spinbox.valueChanged.connect(self.max_dot_rad_changed)
        self.radius_hbl.addWidget(self.radius_max_spinbox)

        self.vbl_main_hbl_conf.addLayout(self.radius_hbl)

        # OffSets
        self.offsets_hbl = QHBoxLayout()
        self.offsets_hbl.setAlignment(Qt.AlignLeft)

        # X
        self.offset_x_label = QLabel()
        self.offset_x_label.setText('Отступ по X:')
        self.offsets_hbl.addWidget(self.offset_x_label)

        self.offset_x_spinbox = QSpinBox()
        self.offset_x_spinbox.setSingleStep(1)
        self.offset_x_spinbox.setMinimum(-500)
        self.offset_x_spinbox.setMaximum(500)
        self.offset_x_spinbox.setValue(self.config.get('offset_x'))
        self.offset_x_spinbox.setMinimumWidth(50)
        self.offset_x_spinbox.valueChanged.connect(self.offset_x_changed)
        self.offsets_hbl.addWidget(self.offset_x_spinbox)

        # Y
        self.offset_y_label = QLabel()
        self.offset_y_label.setText('Отступ по Y:')
        self.offsets_hbl.addWidget(self.offset_y_label)

        self.offset_y_spinbox = QSpinBox()
        self.offset_y_spinbox.setSingleStep(1)
        self.offset_y_spinbox.setMinimum(-500)
        self.offset_y_spinbox.setMaximum(500)
        self.offset_y_spinbox.setValue(self.config.get('offset_y'))
        self.offset_y_spinbox.setMinimumWidth(50)
        self.offset_y_spinbox.valueChanged.connect(self.offset_y_changed)
        self.offsets_hbl.addWidget(self.offset_y_spinbox)

        # CoolDown
        self.cool_down_label = QLabel()
        self.cool_down_label.setText('Кулдаун(мс):')
        self.offsets_hbl.addWidget(self.cool_down_label)

        self.cool_down_spinbox = QSpinBox()
        self.cool_down_spinbox.setSingleStep(10)
        self.cool_down_spinbox.setMinimum(0)
        self.cool_down_spinbox.setMaximum(1000)
        self.cool_down_spinbox.setValue(self.config.get('cool_down'))
        self.cool_down_spinbox.setMinimumWidth(50)
        self.cool_down_spinbox.valueChanged.connect(self.cool_down_changed)
        self.offsets_hbl.addWidget(self.cool_down_spinbox)

        self.vbl_main_hbl_conf.addLayout(self.offsets_hbl)

        # Camera Options
        self.camera_infos_dlg_btn = QPushButton()
        self.camera_infos_dlg_btn.setText('Настройки камеры')
        self.camera_infos_dlg_btn.clicked.connect(self.show_camera_conf)
        self.vbl_main_hbl_conf.addWidget(self.camera_infos_dlg_btn)

        # new window with channels
        self.additional_infos_btn = QPushButton()
        self.additional_infos_btn.setText('Показать дополнительные каналы')
        self.additional_infos_btn.clicked.connect(self.show_additional_info)
        self.vbl_main_hbl_conf.addWidget(self.additional_infos_btn)

        # Save btn
        self.save_btn = QPushButton()
        self.save_btn.setText('Сохранить')
        self.save_btn.clicked.connect(self.save_config)
        self.vbl_main_hbl_conf.addWidget(self.save_btn)

        # Default btn
        self.default_btn = QPushButton()
        self.default_btn.setText('По Умолчанию')
        self.default_btn.clicked.connect(self.default_config)
        self.vbl_main_hbl_conf.addWidget(self.default_btn)

        # INFOS:

        self.infos_vbl = QVBoxLayout()

        self.center_info = QLabel()
        self.rad_info = QLabel()
        self.res_info = QLabel()

        self.infos_vbl.addWidget(self.center_info)
        self.infos_vbl.addWidget(self.rad_info)
        self.infos_vbl.addWidget(self.res_info)

        self.vbl_main_hbl_conf.addLayout(self.infos_vbl)

        # Test Btn
        self.test_btn = QPushButton('Тест Старт')
        self.test_btn.clicked.connect(self.toggle_testing)
        self.vbl_main_hbl_conf.addWidget(self.test_btn)

        # Video capture thread
        # self.th = PSEyeVideoCapture(mutex=self.mutex, condition=self.condition) if self.config.get('is_pseye')\
        #     else CV2VideoCapture(mutex=self.mutex, condition=self.condition)
        self.th = CV2VideoCapture(mutex=self.mutex, condition=self.condition)
        self.th.changePixmap.connect(self.set_image)
        self.th.change_data.connect(self.set_data)
        self.th.start()

        self.test_th = HandleTestTh(self.screen_conf)
        self.test_th.start()

        self.hbl_main_conf.addLayout(self.vbl_main_hbl_video)
        self.hbl_main_conf.addLayout(self.vbl_main_hbl_conf)

        self.setLayout(self.hbl_main_conf)
        self.show()

    def update_camera_list(self):
        is_pseye = self.config.get('is_pseye')
        self.camera_select_box.clear()
        self.camera_select_box.addItem('Выберите камеру:', -1)
        for i in list_of_cams(is_pseye):
            self.camera_select_box.addItem(f'Camera: {i};' + (' (PsEye)' if is_pseye else ''), i)

    def updata_interpolation_list(self):
        self.select_interpolation.clear()
        self.select_interpolation.addItem(f'Выберите вид интерполяций:', -1)
        interps = self.config.get('interps')
        for i in interps.keys():
            self.select_interpolation.addItem(i, interps[i])

    def update_resolution_list(self):
        self.resolution_select.clear()
        self.resolution_select.addItem(f'Выберите качество видео:', -1)
        resolutions = self.config.get('resolutions')
        for i in resolutions:
            self.resolution_select.addItem(i, i)

    def camera_idx_changed(self, idx):
        self.config.set('camera', self.camera_select_box.itemData(idx))
        if not (self.th is None):
            self.th.changeCurrentCamera.emit()

    def resolution_changed(self, idx):
        val = self.resolution_select.itemData(idx)
        if type(val) == int and val < 0:
            return
        self.config.set('selected_resolution', val)
        if not (self.th is None):
            self.th.changeResolution.emit()

    def interpolation_changed(self, idx):
        n = self.select_interpolation.itemData(idx)
        if n < 0:
            return

        self.config.set('interp', n)

    def closeEvent(self, event):
        self.th.stop()
        self.test_th.quit()
        self.on_close.emit()

    def set_conf(self, key, val):
        self.config.set(key, val)

    def show_additional_info(self):
        AdditionalInfos(parent=self.parent(), thread=self.th)

    def min_dot_rad_changed(self, val):
        self.config.set('min_dot_rad', val)

    def max_dot_rad_changed(self, val):
        self.config.set('max_dot_rad', val)

    def cool_down_changed(self, val):
        self.config.set('cool_down', val)

    def offset_x_changed(self, val):
        self.config.set('offset_x', val)

    def offset_y_changed(self, val):
        self.config.set('offset_y', val)

    def set_upper_color(self):
        dlg = QColorDialog(self)
        dlg.setWindowTitle('Верхняя граница цвета')
        color = QColor.fromHsv(
            self.config.get('hue_max'),
            self.config.get('sat_max'),
            self.config.get('val_max')
        )
        dlg.setCurrentColor(color)
        dlg.currentColorChanged.connect(self.save_upper_color)
        dlg.rejected.connect(self.restore_upper_value(color))
        dlg.show()

    def save_upper_color(self, color: QColor):
        self.config.set('hue_max', color.hue())
        self.config.set('sat_max', color.saturation())
        self.config.set('val_max', color.value())

    def restore_upper_value(self, color: QColor):
        return lambda: self.save_upper_color(color)

    def set_lower_color(self):
        dlg = QColorDialog(self)
        dlg.setWindowTitle('Нижняя граница цвета')
        color = QColor.fromHsv(
            self.config.get('hue_min'),
            self.config.get('sat_min'),
            self.config.get('val_min')
        )
        dlg.setCurrentColor(color)
        dlg.currentColorChanged.connect(self.save_lower_color)
        dlg.rejected.connect(self.restore_lower_value(color))
        dlg.show()

    def save_lower_color(self, color: QColor):
        self.config.set('hue_min', color.hue())
        self.config.set('sat_min', color.saturation())
        self.config.set('val_min', color.value())

    def restore_lower_value(self, color: QColor):
        return lambda: self.save_lower_color(color)

    def save_config(self):
        ans = QMessageBox.question(self, 'Подтверждение',
                                   'Вы подтверждаете сохранение?', QMessageBox.Save | QMessageBox.Cancel)
        if ans == QMessageBox.Save:
            self.config.save()
            QMessageBox.information(self, 'Уведомление', 'Успешно сохранено')
            self.close()

    def default_config(self):
        ans = QMessageBox.question(self, 'Подтверждение',
                                   'Вы подтверждаете востановление по умолчанию?', QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            self.config.set_default()
            QMessageBox.information(self, 'Уведомление', 'Успешно востановлено')
            self.close()

    def toggle_testing(self):
        if self.is_testing:
            self.is_testing = False
            self.test_btn.setText('Тест Старт')
            self.th.change_data.disconnect(self.test_th.handle_testing)

        else:
            self.is_testing = True
            self.test_btn.setText('Тест Стоп')
            self.th.change_data.connect(self.test_th.handle_testing)

    def show_camera_conf(self):
        CameraConfigDLG(parent=self.parent(), thread=self.th)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConfigDLG()
    sys.exit(app.exec_())

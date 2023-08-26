from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, Qt
import cv2

class AdditionalInfos(QDialog):

    def __init__(self, thread, parent):
        super(AdditionalInfos, self).__init__(parent=parent)
        self.title = 'Доп. каналы'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.chanel = 'laser'
        self.th = thread
        self.th.layers_pixmap.connect(self.setImage)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedHeight(int(self.height * 1.1))
        self.setMinimumWidth(self.width)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)


        self.vbl = QVBoxLayout()
        self.vbl.setAlignment(Qt.AlignTop)
        self.select = QComboBox()
        self.fill_select()
        self.select.currentIndexChanged.connect(self.change_chanel)
        self.vbl.addWidget(self.select)

        self.label = QLabel()
        self.label.resize(self.width, self.height)
        self.vbl.addWidget(self.label)

        self.setLayout(self.vbl)
        self.show()

    def closeEvent(self, event):
        self.th.layers_pixmap.disconnect(self.setImage)
        super().closeEvent(event)

    @pyqtSlot(dict)
    def setImage(self, dict):
        frame = dict[self.chanel]
        if self.chanel != 'hsv':
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        h, w, ch = frame.shape

        bytesPerLine = ch * w
        convertToQtFormat = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.label.setPixmap(QPixmap.fromImage(p))

    def fill_select(self):
        for i in ['laser', 'hue', 'saturation', 'value', 'hsv']:
            self.select.addItem(i, i)

    def change_chanel(self):
        self.chanel = self.select.currentData()

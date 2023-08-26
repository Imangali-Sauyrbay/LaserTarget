from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QPushButton
from ...utils import clamp


class QMoveButton(QPushButton):
    movedSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QMoveButton, self).__init__(*args, **kwargs)
        self._move_start = False
        self.__mouse_press_pos = 0
        self.__mouse_move_pos = 0

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.buttons() == Qt.LeftButton:
            self._move_start = True
            self.__mouse_press_pos = e.globalPos()
            self.__mouse_move_pos = e.globalPos()
        super(QMoveButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if self._move_start and self.__mouse_press_pos is not None:
            self._move_start = False
            moved = e.globalPos() - self.__mouse_press_pos
            if moved.manhattanLength() > 3:
                e.ignore()
                return

        super(QMoveButton, self).mouseReleaseEvent(e)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if self._move_start and Qt.LeftButton:
            curr_pos = self.mapToGlobal(self.pos())
            global_pos = e.globalPos()
            diff = global_pos - self.__mouse_move_pos
            new_pos = self.mapFromGlobal(curr_pos + diff)
            self.move(
                clamp(
                    new_pos.x(),  # val
                    0 - int(self.width() / 2),  # min
                    int(self.parent().width() - (self.width() / 2))  # max
                ),
                clamp(
                    new_pos.y(),  # val
                    0 - int(self.width() / 2),  # min
                    int(self.parent().height() - (self.width() / 2))  # max
                )
            )
            self.__mouse_move_pos = global_pos
            self.movedSignal.emit()
        super(QMoveButton, self).mouseMoveEvent(e)

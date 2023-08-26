from PyQt5.QtWidgets import QSlider, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt5.QtCore import Qt

from .sliderqt import QDoubleSlider


class QNamedSlider(QWidget):
    def __init__(
            self,
            name,
            on_changed_cb,
            parent_layout,
            value=0,
            _min=0,
            _max=100,
            step=1,
            initial_state=True,
            is_float=False,
            can_be_offed=False,
            checked_cb=None,
            orientation=Qt.Orientation.Horizontal,
            *args,
            **kwargs
    ):
        super(QNamedSlider, self).__init__(*args, **kwargs)
        self.name = name
        self.on_changed = on_changed_cb
        self.value = value
        self._min = _min
        self._max = _max
        self.step = step
        self.initial_state = initial_state
        self.can_be_offed = can_be_offed
        self.checked_cb = checked_cb
        self.orientation = orientation
        self.is_float = is_float
        self.parent_layout = parent_layout

        self.label = QLabel()
        self.checkbox = None
        self.slider = QDoubleSlider(orientation=self.orientation) if is_float \
            else QSlider(orientation=self.orientation)
        self.vbl = QVBoxLayout()
        self.hbl = QHBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.hbl.setAlignment(Qt.AlignLeft)

        if self.can_be_offed:
            self.checkbox = QCheckBox()
            self.checkbox.setCheckState(Qt.CheckState.Checked if self.initial_state else Qt.CheckState.Unchecked)
            self.checkbox.stateChanged.connect(self.toggle_self)
            self.hbl.addWidget(self.checkbox)

        self.label.setText(f"{self.name}({self.value}):")
        self.hbl.addWidget(self.label)

        self.vbl.addLayout(self.hbl)

        self.slider.setMinimum(self._min)
        self.slider.setMaximum(self._max)
        self.slider.setSingleStep(self.step)
        self.slider.setValue(self.value)
        if self.is_float:
            self.slider.doubleValueChanged.connect(self._on_changed)
        else:
            self.slider.valueChanged.connect(self._on_changed)

        self.slider.setEnabled(self.initial_state)
        self.vbl.addWidget(self.slider)

        self.parent_layout.addLayout(self.vbl)

    def _on_changed(self, val):
        self.on_changed(val)
        self.label.setText(f"{self.name}({round(val, 2)}):")

    def toggle_self(self, state):
        state = False if state == 0 else True
        self.slider.setEnabled(state)
        if self.checked_cb is not None:
            self.checked_cb(state)

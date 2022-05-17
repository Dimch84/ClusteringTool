from copy import copy
from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout, QCheckBox


class CheckBoxParamEditor(QWidget):
    def __init__(self, specified: bool, value):
        super().__init__()
        self.specified = copy(specified)
        self.value = copy(value)

        layout = QVBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.addItem('None')
        self.combo_box.addItem('Do not specify')
        self.combo_box.addItem('Specify')
        self.combo_box.currentIndexChanged.connect(self.change_value)
        layout.addWidget(self.combo_box)
        self.check_box = QCheckBox()
        self.check_box.stateChanged.connect(self.current_state_changed)
        self.check_box.setEnabled(False)
        layout.addWidget(self.check_box)
        self.setLayout(layout)

        if not self.specified:
            if self.value is not None:
                raise KeyError
            self.combo_box.setCurrentIndex(1)
        else:
            if self.value is None:
                self.combo_box.setCurrentIndex(0)
            else:
                self.check_box.setChecked(self.value)
                self.combo_box.setCurrentIndex(2)

    def change_value(self, index: int):
        if index == 0:
            self.specified = True
            self.value = None
            self.check_box.setEnabled(False)
        elif index == 1:
            self.specified = False
            self.value = None
            self.check_box.setEnabled(False)
        elif index == 2:
            self.specified = True
            self.value = self.check_box.isChecked()
            self.check_box.setEnabled(True)

    def current_state_changed(self, checked: bool):
        if self.combo_box.currentIndex() == 2:
            self.value = checked

    def is_specified(self):
        return self.specified

    def get_value(self):
        return self.value

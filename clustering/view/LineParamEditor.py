from copy import copy

from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout, QLineEdit


class LineParamEditor(QWidget):
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
        self.line_edit = QLineEdit()
        self.line_edit.textChanged.connect(self.current_text_changed)
        self.line_edit.setEnabled(False)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

        if not self.specified:
            if self.value is not None:
                raise KeyError
            self.combo_box.setCurrentIndex(1)
        else:
            if self.value is None:
                self.combo_box.setCurrentIndex(0)
            else:
                self.line_edit.setText(self.value)
                self.combo_box.setCurrentIndex(2)

    def change_value(self, index: int):
        if index == 0:
            self.specified = True
            self.value = None
            self.line_edit.setEnabled(False)
        elif index == 1:
            self.specified = False
            self.value = None
            self.line_edit.setEnabled(False)
        elif index == 2:
            self.specified = True
            self.value = self.line_edit.text()
            self.line_edit.setEnabled(True)

    def current_text_changed(self, text: str):
        if self.combo_box.currentIndex() == 2:
            self.value = text

    def is_specified(self):
        return self.specified

    def get_value(self):
        return self.value

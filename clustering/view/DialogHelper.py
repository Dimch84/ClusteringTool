from PyQt5.QtGui import QIntValidator, QDoubleValidator, QValidator
from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLineEdit, QWidget, QHBoxLayout, QLabel, QDialogButtonBox


class PositiveIntValidator(QIntValidator):
    def __init__(self):
        super().__init__()

    def validate(self, inp: str, pos: int):
        result, i, p = super().validate(inp, pos)
        if result == QValidator.Acceptable and int(inp) <= 0:
            print(14, result, int(inp))
            return QValidator.Invalid, i, p
        return result, i, p


class NonNegativeDoubleValidator(QDoubleValidator):
    def __init__(self):
        super().__init__()

    def validate(self, inp: str, pos: int):
        result, i, p = super().validate(inp, pos)
        if result == QValidator.Acceptable and float(inp) < 0:
            return QValidator.Invalid, i, p
        return result, i, p


class DialogHelper:
    def create_button_box(self):
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    @staticmethod
    def add_title_to_widget(title: str, widget: QWidget, set_title_horizontally: bool = False):
        if set_title_horizontally:
            result = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(QLabel(title))
        else:
            result = QGroupBox(title)
            layout = QVBoxLayout()
        layout.addWidget(widget)
        result.setLayout(layout)
        return result

    def create_named_text_field(self, name: str, action, default_value="", validator=None, set_title_horizontally=False):
        res = QLineEdit()
        res.setText(str(default_value))
        res.textChanged.connect(action)
        if validator is not None:
            validator.setLocale(QLocale("en"))
            res.setValidator(validator)
        return self.add_title_to_widget(name, res, set_title_horizontally)

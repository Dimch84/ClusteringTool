from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QCheckBox, QGroupBox, QDialogButtonBox, QLineEdit, \
    QWidget
from dataclasses import dataclass

from clustering.view.DialogHelper import DialogHelper


@dataclass
class AddDatasetDialogResults:
    name: str
    included_cols: list[str]
    normalise: bool


class AddDatasetDialog(QDialog, DialogHelper):
    def __init__(self, parent: QWidget, columns: list[str]):
        super().__init__(parent)
        self.cols = columns
        self.included_cols = set()
        self.normalise = False
        self.dataset_name = "Unnamed"

        self.setWindowTitle("Dataset editor")
        self.setMinimumSize(600, 300)

        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_dataset_name_input())
        self.layout.addWidget(self.__create_cols_selector())
        self.layout.addWidget(self.__create_normalise_box())
        self.layout.addWidget(self.create_button_box())
        self.setLayout(self.layout)

    def __create_dataset_name_input(self):
        return self.create_named_text_field("Dataset's name", self.__change_dataset_name, self.dataset_name)

    def __change_dataset_name(self, new_name: str):
        self.dataset_name = new_name

    def __create_cols_selector(self):
        selector = QGroupBox("Features to include in dataset:")
        layout = QVBoxLayout()
        for column in self.cols:
            checkBox = QCheckBox(column)
            checkBox.stateChanged.connect(
                lambda x, c=column: self.included_cols.add(c) if x else self.included_cols.discard(c)
            )
            layout.addWidget(checkBox)
        selector.setLayout(layout)
        return selector

    def __create_normalise_box(self):
        checkBox = QCheckBox("Normalise features?")
        checkBox.stateChanged.connect(self.__set_normalise)
        return checkBox

    def __set_normalise(self, val: bool):
        self.normalise = val

    def get_result(self):
        return AddDatasetDialogResults(
            name=self.dataset_name,
            included_cols=list([column for column in self.cols if column in self.included_cols]),
            normalise=self.normalise
        )

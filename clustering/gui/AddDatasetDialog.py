from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QCheckBox, QGroupBox, QDialogButtonBox, QLineEdit
from dataclasses import dataclass


@dataclass
class AddDatasetDialogResults:
    name: str
    included_cols: [str]
    normalise: bool


class AddDatasetDialog(QDialog):
    def __init__(self, parent, cols, default_name: str = ""):
        super().__init__(parent)
        self.cols = cols
        self.included_cols = set()
        self.normalise = False
        self.dataset_name = default_name

        self.setWindowTitle("Dataset editor")
        self.setMinimumSize(600, 300)

        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_dataset_name_input(default_name))
        self.layout.addWidget(self.__create_cols_selector())
        self.layout.addWidget(self.__create_normalise_box())
        self.layout.addWidget(self.__create_button_box())
        self.setLayout(self.layout)

    def __create_button_box(self):
        QBtn = QDialogButtonBox.Ok
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    def __create_dataset_name_input(self, default_name: str):
        res = QGroupBox("Dataset's name")
        layout = QVBoxLayout()
        num_of_clusters_input = QLineEdit()
        num_of_clusters_input.setText(default_name)
        num_of_clusters_input.textChanged.connect(self.__change_dataset_name)
        layout.addWidget(num_of_clusters_input)
        res.setLayout(layout)
        return res

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
            self.dataset_name,
            [column for column in self.cols if column in self.included_cols],
            self.normalise
        )

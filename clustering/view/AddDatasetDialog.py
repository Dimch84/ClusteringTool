from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QCheckBox, QGroupBox, QRadioButton
from dataclasses import dataclass

from clustering.view.WidgetHelper import WidgetHelper


@dataclass
class AddDatasetDialogResults:
    name: str
    included_cols: list[str]
    title_col: str | None
    normalise: bool


class AddDatasetDialog(QDialog, WidgetHelper):
    def __init__(self, feature_cols: list[str], title_cols: list[str]):
        super().__init__()
        self.feature_cols = feature_cols
        self.title_cols = title_cols + ["Generate automatically"]
        self.included_cols = set()
        self.normalise = False
        self.dataset_name = "Unnamed"
        self.title_col = None

        self.setWindowTitle("Dataset editor")
        self.setMinimumSize(600, 300)

        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_dataset_name_input())
        self.layout.addWidget(self.__create_title_selector())
        self.layout.addWidget(self.__create_cols_selector())
        self.layout.addWidget(self.__create_normalise_box())
        self.layout.addWidget(self.create_button_box())
        self.setLayout(self.layout)

    def __create_dataset_name_input(self):
        return self.create_named_text_field("Dataset's name", self.__change_dataset_name, self.dataset_name)

    def __change_dataset_name(self, new_name: str):
        self.dataset_name = new_name

    def __create_title_selector(self):
        selector = QGroupBox("Choose column to use as titles:")
        layout = QVBoxLayout()
        for column in self.title_cols:
            btn = QRadioButton(column)
            btn.toggled.connect(lambda checked, b=btn: self.__title_selector_changed(checked, b))
            layout.addWidget(btn)
        selector.setLayout(layout)
        return selector

    def __title_selector_changed(self, checked: bool, btn):
        if checked:
            if btn.text() == "Generate automatically":
                self.title_col = None
            else:
                self.title_col = btn.text()

    def __create_cols_selector(self):
        selector = QGroupBox("Features to include in dataset:")
        layout = QVBoxLayout()
        for column in self.feature_cols:
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
            included_cols=list([column for column in self.feature_cols if column in self.included_cols]),
            title_col=self.title_col,
            normalise=self.normalise
        )

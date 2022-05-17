from PyQt5.QtWidgets import QDialog, QFormLayout, QPushButton

from clustering.model.Model import AppMode
from clustering.view.WidgetHelper import WidgetHelper


class SelectModeDialog(QDialog, WidgetHelper):
    def __init__(self):
        super().__init__()
        self.result = None
        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_research_mode_button())
        self.layout.addWidget(self.__create_compare_mode_button())
        self.setLayout(self.layout)

    def __create_research_mode_button(self):
        btn = QPushButton("Research mode")
        btn.clicked.connect(self.__research_mode_selected)
        return btn

    def __research_mode_selected(self):
        self.result = AppMode.ResearchMode
        self.accept()

    def __create_compare_mode_button(self):
        btn = QPushButton("Compare mode")
        btn.clicked.connect(self.__compare_mode_selected)
        return btn

    def __compare_mode_selected(self):
        self.result = AppMode.CompareMode
        self.accept()

    def get_result(self):
        return self.result

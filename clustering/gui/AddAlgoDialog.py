from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QComboBox, QLineEdit
from clustering.algorithm import load_algorithms
from dataclasses import dataclass


@dataclass
class AddAlgoDialogResults():
    algo_name: str
    num_of_clusters: int


class AddAlgoDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
        self.algo_selector = self.__create_selector()
        self.current_algorithm = self.algo_selector.currentText()

        self.setWindowTitle("Algorithm settings")
        self.setMinimumSize(200, 400)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.num_of_clusters_input = QLineEdit()
        self.num_of_clusters_input.setPlaceholderText("Enter the number of clusters")
        self.num_of_clusters_input.textChanged.connect(self.__change_current_num_of_clusters)
        self.num_of_clusters = 0

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.algo_selector, )
        self.layout.addWidget(self.num_of_clusters_input)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def __create_selector(self):
        selector = QComboBox()
        selector.addItems(self.algorithms)
        selector.activated[str].connect(self.__change_current_algorithm)
        return selector

    def __change_current_num_of_clusters(self, text: str):
        self.num_of_clusters = int(text)

    def __change_current_algorithm(self, algorithm_name: str):
        self.current_algorithm = algorithm_name

    def get_result(self):
        return AddAlgoDialogResults(self.current_algorithm, self.num_of_clusters)

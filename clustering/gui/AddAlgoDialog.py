from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox

from clustering.algorithm import load_algorithms


class AddAlgoDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
        self.algo_selector = self.create_selector()
        self.current_algorithm = self.algo_selector.currentText()

        self.setWindowTitle("Algorithm settings")
        self.setMinimumSize(200, 200)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.algo_selector)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def create_selector(self):
        selector = QComboBox()
        selector.addItems(self.algorithms)
        selector.activated[str].connect(self.change_current_algorithm)
        return selector

    def change_current_algorithm(self, algorithm_name: str):
        self.current_algorithm = algorithm_name
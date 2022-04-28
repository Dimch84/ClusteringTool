from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QComboBox, QLineEdit, QFormLayout, QLabel, \
    QCheckBox, QGroupBox
from clustering.algorithm import load_algorithms
from dataclasses import dataclass
from clustering.metrics import metrics


@dataclass
class AddAlgoDialogResults:
    algo_name: str
    num_of_clusters: int
    selected_metrics: set


class AddAlgoDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_metrics = set()
        self.algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}

        self.setWindowTitle("Algorithm settings")
        self.setMinimumSize(600, 400)

        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_algo_selector())
        self.layout.addWidget(self.__create_num_of_clusters_inp())
        self.layout.addWidget(self.__create_metrics_selector())
        self.layout.addWidget(self.__create_button_box())
        self.setLayout(self.layout)

    def __create_metrics_selector(self):
        selector = QGroupBox("Metrics")
        layout = QVBoxLayout()
        for metric in metrics:
            checkBox = QCheckBox(metric.name)
            checkBox.stateChanged.connect(lambda x, y=metric.name: self.add_metric(y) if x else self.erase_metric(y))
            layout.addWidget(checkBox)
        selector.setLayout(layout)
        return selector

    def add_metric(self, metric_name):
        self.selected_metrics.add(metric_name)

    def erase_metric(self, metric_name):
        self.selected_metrics.discard(metric_name)

    def __create_algo_selector(self):
        selector = QGroupBox("Algorithms")
        layout = QVBoxLayout()
        box = QComboBox()
        box.addItems(self.algorithms)
        box.activated[str].connect(self.__change_current_algorithm)
        self.current_algorithm = box.currentText()
        layout.addWidget(box)
        selector.setLayout(layout)
        return selector

    def __create_num_of_clusters_inp(self):
        res = QGroupBox("Num of clusters")
        layout = QVBoxLayout()
        num_of_clusters_input = QLineEdit()
        num_of_clusters_input.setPlaceholderText("Enter the number of clusters")
        num_of_clusters_input.textChanged.connect(self.__change_current_num_of_clusters)
        layout.addWidget(num_of_clusters_input)
        res.setLayout(layout)
        return res

    def __create_button_box(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    def __change_current_num_of_clusters(self, text: str):
        self.num_of_clusters = int(text)

    def __change_current_algorithm(self, algorithm_name: str):
        self.current_algorithm = algorithm_name

    def get_result(self):
        return AddAlgoDialogResults(self.current_algorithm, self.num_of_clusters, self.selected_metrics)

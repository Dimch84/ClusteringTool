from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QComboBox, QLineEdit, QFormLayout, QLabel, \
    QCheckBox, QGroupBox, QHBoxLayout, QWidget
from clustering.algorithm import load_algorithms, Algorithm
from dataclasses import dataclass
from clustering.scores import scores


@dataclass
class AddAlgoDialogResults:
    algo_name: str
    num_of_clusters: int
    extra_params: dict
    selected_scores: set


class AddAlgoDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_scores = set()
        self.algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
        self.extra_params: dict = {}
        self.num_of_clusters = None

        self.setWindowTitle("Algorithm settings")
        self.setMinimumSize(600, 800)

        self.params_selector = None
        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_algo_selector())
        self.layout.addWidget(self.__create_num_of_clusters_input())
        self.layout.addWidget(self.__create_scores_selector())
        self.layout.addWidget(self.params_selector)
        self.layout.addWidget(self.__create_button_box())
        self.setLayout(self.layout)

    def __create_scores_selector(self):
        selector = QGroupBox("Scores")
        layout = QVBoxLayout()
        for score in scores:
            checkBox = QCheckBox(score.name)
            checkBox.stateChanged.connect(lambda x, y=score.name: self.add_score(y) if x else self.erase_score(y))
            layout.addWidget(checkBox)
        selector.setLayout(layout)
        return selector

    def add_score(self, score_name):
        self.selected_scores.add(score_name)

    def erase_score(self, score_name):
        self.selected_scores.discard(score_name)

    def __create_algo_selector(self):
        selector = QGroupBox("Algorithms")
        layout = QVBoxLayout()
        box = QComboBox()
        box.addItems(self.algorithms)
        box.activated[str].connect(self.__change_current_algorithm)
        self.__change_current_algorithm(box.currentText())
        layout.addWidget(box)
        selector.setLayout(layout)
        return selector

    def __create_num_of_clusters_input(self):
        res = QGroupBox("Num of clusters")
        layout = QVBoxLayout()
        num_of_clusters_input = QLineEdit()
        num_of_clusters_input.setPlaceholderText("Enter the number of clusters")
        num_of_clusters_input.textChanged.connect(self.__change_current_num_of_clusters)
        layout.addWidget(num_of_clusters_input)
        res.setLayout(layout)
        return res

    def __create_params_selector(self, algorithm: Algorithm):
        extra_params_selector = QGroupBox("Extra params")
        extra_params_layout = QVBoxLayout()
        for param_name in algorithm.extra_params.keys():
            param_selector = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(QLabel(param_name))
            box = QComboBox()
            box.addItems(algorithm.extra_params[param_name])
            box.activated[str].connect(lambda text_str, x=param_name:
                                       self.__change_param_value(x, text_str))
            self.extra_params[param_name] = box.currentText()
            layout.addWidget(box)
            param_selector.setLayout(layout)
            extra_params_layout.addWidget(param_selector)
        extra_params_selector.setLayout(extra_params_layout)
        return extra_params_selector

    def __change_param_value(self, param_name, text_str):
        self.extra_params[param_name] = text_str

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
        next_state = self.__create_params_selector(self.algorithms[self.current_algorithm])
        if self.params_selector is None:
            self.params_selector = next_state
        else:
            self.layout.replaceWidget(self.params_selector, next_state)
            self.params_selector.close()
            self.params_selector = next_state

    def get_result(self):
        return AddAlgoDialogResults (
            self.current_algorithm,
            self.num_of_clusters,
            self.extra_params,
            self.selected_scores
        )
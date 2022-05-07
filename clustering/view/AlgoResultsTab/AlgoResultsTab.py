import uuid

from PyQt5.QtWidgets import QWidget, QGridLayout, QFormLayout, QLabel, QGroupBox, QVBoxLayout, QPushButton

from clustering.view.AlgoResultsTab.ClusteringView import ClusteringView
from clustering.presenter.Presenter import Presenter
from clustering.view.AlgoParamsSetter import AlgoParamsSetter, ParamsSetterAttr


class ScoresWidget(QWidget):
    def __init__(self, scores: dict):
        super().__init__()
        self.setMinimumSize(400, 300)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)
        for score_name in scores.keys():
            layout.addRow(QLabel(f"{score_name}: "), QLabel(str(scores[score_name])))


class AlgoResultsTab(QWidget):
    def __init__(self, presenter: Presenter, algo_run_id: uuid):
        super().__init__()
        self.presenter = presenter
        self.algo_run_id = algo_run_id

        algo_run_results = presenter.get_algo_run_results(algo_run_id)

        self.parameters_widget = AlgoParamsSetter(ParamsSetterAttr(
            params=presenter.get_algo_params(algo_run_results.config.algorithm_id),
            values=algo_run_results.config.params
        ))
        self.scores_widget = ScoresWidget(algo_run_results.scores)
        self.clustering_view = ClusteringView(
            points=presenter.get_dataset_points(algo_run_results.config.dataset_id),
            pred=algo_run_results.pred
        )
        self.rerun_button = QPushButton("Rerun algorithm")
        self.rerun_button.clicked.connect(self.rerun_algo_button_listener)
        self.export_button = QPushButton("Export to csv")
        self.export_button.clicked.connect(self.export_results_button_listener)
        layout = QGridLayout()
        layout.addWidget(self.add_title_to_widget("Clustering", self.clustering_view), 0, 0, 2, 3)
        layout.addWidget(self.add_title_to_widget("Scores", self.scores_widget), 0, 3, 1, 1)
        layout.addWidget(self.add_title_to_widget("Parameters", self.parameters_widget), 1, 3, 1, 1)
        layout.addWidget(self.export_button, 2, 0, 1, 3)
        layout.addWidget(self.rerun_button, 2, 3, 1, 1)
        self.setLayout(layout)

    def rerun_algo_button_listener(self):
        self.presenter.rerun_algo_pushed(
            algo_run_id=self.algo_run_id,
            params=self.parameters_widget.get_params()
        )

    def export_results_button_listener(self):
        self.presenter.export_algo_run_results(self.algo_run_id)

    def add_title_to_widget(self, title: str, widget: QWidget):
        result = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        result.setLayout(layout)
        return result

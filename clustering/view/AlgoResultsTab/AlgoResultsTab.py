import uuid

from PyQt5.QtWidgets import QWidget, QGridLayout, QFormLayout, QLabel, QGroupBox, QVBoxLayout

from clustering.view.AlgoResultsTab.ClusteringView import ClusteringView
from clustering.presenter.Presenter import Presenter


class ParametersWidget(QWidget):
    def __init__(self, params: dict):
        super().__init__()
        self.setMinimumSize(400, 300)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)
        for param_name in params.keys():
            layout.addRow(QLabel(f"{param_name}: "), QLabel(str(params[param_name])))


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

        algo_run_results = presenter.get_algo_run_results(algo_run_id)
        dataset_id = algo_run_results.config.dataset_id
        self.parameters_widget = ParametersWidget(algo_run_results.config.params)
        self.scores_widget = ScoresWidget(algo_run_results.scores)
        self.clustering_view = ClusteringView(
            points=presenter.get_dataset_points(dataset_id),
            pred=algo_run_results.pred
        )
        layout = QGridLayout()
        layout.addWidget(self.clustering_view, 0, 0, 2, 3)
        layout.addWidget(self.add_title_to_widget("Scores", self.scores_widget), 0, 3, 1, 1)
        layout.addWidget(self.add_title_to_widget("Parameters", self.parameters_widget), 1, 3, 1, 1)
        self.setLayout(layout)

    def add_title_to_widget(self, title: str, widget: QWidget):
        result = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        result.setLayout(layout)
        return result

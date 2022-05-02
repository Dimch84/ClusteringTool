import numpy as np
from dataclasses import dataclass

from PyQt5.QtWidgets import QWidget, QGridLayout, QFormLayout, QLabel

from clustering.view.AlgoResultsTab.ClusteringView import ClusteringView


@dataclass
class AlgoRun:
    algo_name: str
    dataset_name: str
    data: np.ndarray
    results: np.ndarray
    params: dict
    calculated_scores: dict


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
    def __init__(self, calculated_scores: dict):
        super().__init__()
        self.setMinimumSize(400, 300)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)
        for score_name in calculated_scores.keys():
            layout.addRow(QLabel(f"{score_name}: "), QLabel(str(calculated_scores[score_name])))


class AlgoResultsTab(QWidget):
    def __init__(self, algo_run: AlgoRun):
        super().__init__()
        self.algo_run = algo_run

        self.parameters_widget = ParametersWidget(algo_run.params)
        self.scores_widget = ScoresWidget(algo_run.calculated_scores)
        self.clustering_view = ClusteringView(algo_run.data, algo_run.results)

        layout = QGridLayout()
        layout.addWidget(self.clustering_view, 0, 0, 2, 3)
        layout.addWidget(self.scores_widget, 0, 3, 1, 1)
        layout.addWidget(self.parameters_widget, 1, 3, 1, 1)
        self.setLayout(layout)

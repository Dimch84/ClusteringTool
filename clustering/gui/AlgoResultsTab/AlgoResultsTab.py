from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QVBoxLayout
from clustering.gui.AlgoResultsTab.ParametersWidget import ParametersWidget

from clustering.algorithm import Algorithm
from clustering.dataset import Dataset
from clustering.gui.AlgoResultsTab.ClusteringView import ClusteringView
from clustering.gui.AlgoResultsTab.ScoresWidget import ScoresWidget


class AlgoResultsTab(QWidget):
    def __init__(self, algo: Algorithm, dataset: Dataset, params: dict, score_names: set[str], results=None,
                 parent=None):
        self.algo = algo
        self.dataset = dataset
        self.results = results
        self.params = params
        self.score_names = score_names

        super(AlgoResultsTab, self).__init__(parent)

        self.scores_widget = self.__create_scores(self.score_names)
        self.parameters_widget = self.__create_parameters(self.params)
        self.plot_widget = self.__create_plot()

        layout = QGridLayout()
        layout.addWidget(self.plot_widget, 0, 0, 2, 3)
        layout.addWidget(self.scores_widget, 0, 3, 1, 1)
        layout.addWidget(self.parameters_widget, 1, 3, 1, 1)
        self.setLayout(layout)

    def get_results(self):
        # TODO: check if self.results are up-to-date

        results = self.results if self.results is not None else \
            self.algo.run(self.dataset.data, self.params)
        self.results = results
        return results

    def __create_scores(self, score_names: set[str]):
        pred = self.get_results()
        target = self.dataset.target
        data = self.dataset.data
        res = QGroupBox("Scores")
        layout = QVBoxLayout()
        layout.addWidget(ScoresWidget(data, score_names, target, pred))
        res.setLayout(layout)
        return res

    def __create_parameters(self, params):
        res = QGroupBox("Parameters")
        layout = QVBoxLayout()
        layout.addWidget(ParametersWidget(params))
        res.setLayout(layout)
        return res

    def __create_plot(self):
        return ClusteringView(self.dataset.data, self.get_results())

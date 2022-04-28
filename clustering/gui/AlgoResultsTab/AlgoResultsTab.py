from PyQt5.QtWidgets import QWidget, QGridLayout

from clustering.algorithm import Algorithm
from clustering.dataset import Dataset
from clustering.gui.AlgoResultsTab.ClusteringView import ClusteringView
from clustering.gui.AlgoResultsTab.StatisticsWidget import StatisticsWidget


class AlgoResultsTab(QWidget):
    def __init__(self, algo: Algorithm, dataset: Dataset, num_of_clusters: int, metric_names: set[str], results=None, parent=None):
        self.algo = algo
        self.dataset = dataset
        self.results = results
        self.num_of_clusters = num_of_clusters
        self.metric_names = metric_names

        super(AlgoResultsTab, self).__init__(parent)

        self.statistics_widget = self.__create_statistics(self.metric_names)
        self.plot_widget = self.__create_plot()

        layout = QGridLayout()
        layout.addWidget(self.plot_widget, 1, 0, 2, 2)
        layout.addWidget(self.statistics_widget, 1, 2, 2, 1)
        self.setLayout(layout)

    def get_results(self):
        # TODO: check if self.results are up-to-date
        results = self.results if self.results is not None else \
            self.algo.run(self.dataset.data, self.num_of_clusters)
        self.results = results
        return results

    def __create_statistics(self, metric_names: set[str]):
        pred = self.get_results()
        target = self.dataset.target
        data = self.dataset.data
        return StatisticsWidget(data, metric_names, target, pred)

    def __create_plot(self):
        return ClusteringView(self.dataset.data, self.get_results())

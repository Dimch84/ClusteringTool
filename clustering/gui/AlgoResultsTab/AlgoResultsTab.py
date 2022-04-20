from PyQt5.QtWidgets import QWidget, QGridLayout

from clustering.algorithm import Algorithm
from clustering.dataset import Dataset
from clustering.gui.AlgoResultsTab.ClusteringView import ClusteringView
from clustering.gui.AlgoResultsTab.StatisticsWidget import StatisticsWidget


class AlgoResultsTab(QWidget):
    def __init__(self, algo: Algorithm, dataset: Dataset, parent=None):
        self.algo = algo
        self.dataset = dataset

        super(AlgoResultsTab, self).__init__(parent)

        self.statistics_widget = self.create_statistics()
        self.plot_widget = self.create_plot()

        layout = QGridLayout()
        layout.addWidget(self.plot_widget, 1, 0, 2, 2)
        layout.addWidget(self.statistics_widget, 1, 2, 2, 1)
        self.setLayout(layout)

    def create_statistics(self):
        pred = self.algo.run(self.dataset.data, self.dataset.num_of_classes)
        target = self.dataset.target
        data = self.dataset.data
        return StatisticsWidget(data, target, pred)

    def create_plot(self):
        return ClusteringView(self.dataset.data, list(self.algo.run(self.dataset.data, self.dataset.num_of_classes)))
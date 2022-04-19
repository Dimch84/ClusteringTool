from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox
from PyQt5.QtCore import QRect

from clustering.algorithm import Algorithm
from clustering.dataset import load_all_datasets
from clustering.gui.ClusteringView import ClusteringView
from clustering.gui.StatisticsWidget import StatisticsWidget


class AlgoResultsWidget(QWidget):
    def __init__(self, algo: Algorithm, parent=None):
        super(AlgoResultsWidget, self).__init__(parent)
        self.setGeometry(QRect(0, 0, 1200, 800))

        layout = QGridLayout()

        self.algo = algo
        self.datasets = {dataset.name: dataset for dataset in load_all_datasets()}

        self.dataset_selector = self.create_selector()
        self.current_dataset = self.dataset_selector.currentText()
        self.statistics_widget = self.create_statistics()
        self.plot_widget = self.create_plot()

        layout.addWidget(self.dataset_selector, 0, 0, 1, 2)
        layout.addWidget(self.plot_widget, 1, 0, 2, 2)
        layout.addWidget(self.statistics_widget, 1, 2, 2, 1)

        self.setLayout(layout)

    def create_statistics(self):
        dataset = self.datasets[self.current_dataset]
        pred = list(self.algo.run(dataset.data, dataset.num_of_classes))
        target = dataset.target
        data = dataset.data
        return StatisticsWidget(data, target, pred)

    def create_plot(self):
        dataset = self.datasets[self.current_dataset]
        return ClusteringView(dataset.data, self.algo.run(dataset.data, dataset.num_of_classes))

    def create_selector(self):
        selector = QComboBox()
        selector.addItems(self.datasets)
        selector.activated[str].connect(self.change_current_dataset)
        return selector

    def redraw_plot(self):
        prev_plot = self.plot_widget
        cur_plot = self.create_plot()
        prev_plot.close()
        self.layout().replaceWidget(prev_plot, cur_plot)
        self.plot_widget = cur_plot

        prev_statistics = self.statistics_widget
        cur_statistics = self.create_statistics()
        prev_statistics.close()
        self.layout().replaceWidget(prev_statistics, cur_statistics)
        self.statistics_widget = cur_statistics

    def change_current_dataset(self, dataset_name: str):
        self.current_dataset = dataset_name
        self.redraw_plot()

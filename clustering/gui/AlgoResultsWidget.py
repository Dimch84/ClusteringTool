from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QComboBox
from PyQt5.QtCore import QPointF, QRect
from sklearn.decomposition import PCA
import numpy as np

from clustering.algorithm import Algorithm
from clustering.dataset import load_all_datasets
from clustering.gui.ClusteringView import ClusteringView


def data_converse(data: np.ndarray) -> np.ndarray:
    if data.shape[1] == 2:
        return data
    return PCA(n_components=2).fit_transform(data)


class AlgoResultsWidget(QWidget):
    def __init__(self, algo: Algorithm, parent=None):
        super(AlgoResultsWidget, self).__init__(parent)
        layout = QGridLayout()

        self.algo = algo
        self.datasets = {dataset.name: dataset for dataset in load_all_datasets()}

        self.create_selector()
        self.create_plot()

        layout.addWidget(self.plot_widget, 1, 0, 2, 2)
        layout.addWidget(self.dataset_selector, 0, 0)

        self.setLayout(layout)

    def create_plot(self):
        dataset = self.datasets[self.current_dataset]
        points = data_converse(dataset.data)
        points = list(map(lambda point: QPointF(point[0], point[1]), points))

        self.plot_widget = ClusteringView(points, list(self.algo.run(dataset.data, dataset.num_of_classes)))
        self.setGeometry(QRect(0, 0, 900, 900))

    def redraw_plot(self):
        old_widget = self.plot_widget
        self.create_plot()
        self.layout().replaceWidget(old_widget, self.plot_widget)

    def change_current_dataset(self, dataset_name: str):
        self.current_dataset = dataset_name
        self.redraw_plot()

    def create_selector(self):
        selector = QComboBox()
        selector.addItems(self.datasets)
        selector.activated[str].connect(self.change_current_dataset)

        self.dataset_selector = selector
        self.current_dataset = selector.currentText()

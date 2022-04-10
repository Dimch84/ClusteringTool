from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from sklearn.decomposition import PCA
import numpy as np
import matplotlib

from clustering.algorithm import Algorithm
from clustering.dataset import load_all_datasets


matplotlib.use('Qt5Agg')


def data_converse(data: np.ndarray) -> np.ndarray:
    if data.shape[1] == 2:
        return data
    return PCA(n_components=2).fit_transform(data)


class AlgoResultsWidget(QWidget):
    def __init__(self, algo: Algorithm, parent=None):
        super(AlgoResultsWidget, self).__init__(parent)
        layout = QGridLayout()

        self.datasets = {dataset.name: dataset for dataset in load_all_datasets()}

        self.create_selector()
        self.create_plot()

        layout.addWidget(self.plot_widget, 0, 0, 2, 2)
        layout.addWidget(self.dataset_selector, 0, 0)

        self.setLayout(layout)

    def create_plot(self):
        fig = Figure(figsize=(100, 100), dpi=100)
        self.plot = fig.add_subplot()
        self.plot_widget = FigureCanvasQTAgg(fig)
        self.redraw_plot()

    def redraw_plot(self):
        # TODO: rewrite function so that it shows results of algorithm
        self.plot.cla()  # Clear axes
        dataset = self.datasets[self.current_dataset]
        d = data_converse(dataset.data)
        self.plot.scatter(d[:, 0], d[:, 1])
        self.plot_widget.draw()

    def change_current_dataset(self, dataset_name: str):
        self.current_dataset = dataset_name
        self.redraw_plot()

    def create_selector(self):
        selector = QComboBox()
        selector.addItems(self.datasets)
        selector.activated[str].connect(self.change_current_dataset)

        self.dataset_selector = selector
        self.current_dataset = selector.currentText()

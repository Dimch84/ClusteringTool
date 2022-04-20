from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QGridLayout, QComboBox

from clustering.algorithm import load_algorithms
from clustering.dataset import load_all_datasets
from clustering.gui.AddAlgoDialog import AddAlgoDialog
from clustering.gui.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('clustering')
        self.setGeometry(70, 100, 1800, 900)

        self.datasets = {dataset.name: dataset for dataset in load_all_datasets()}
        self.dataset_selector = self.create_selector()
        self.current_dataset = self.dataset_selector.currentText()
        self.tab_widget = QTabWidget()

        self.add_tab_button = QPushButton('Add algorithm')
        self.add_tab_button.clicked.connect(self.add_tab)

        layout = QGridLayout()
        layout.addWidget(self.dataset_selector, 0, 0, 1, 1)
        layout.addWidget(self.add_tab_button, 1, 0, 1, 1)
        layout.addWidget(self.tab_widget, 2, 0, 2, 10)
        self.setLayout(layout)

    def add_tab(self):
        dataset = self.datasets[self.current_dataset]
        dlg = AddAlgoDialog(self)
        if dlg.exec():
            algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
            self.tab_widget.addTab(AlgoResultsTab(algorithms[dlg.current_algorithm], dataset), dlg.current_algorithm)

    def create_selector(self):
        selector = QComboBox()
        selector.addItems(self.datasets)
        selector.activated[str].connect(self.change_current_dataset)
        return selector

    def change_current_dataset(self, dataset_name: str):
        self.current_dataset = dataset_name
        self.tab_widget.clear()
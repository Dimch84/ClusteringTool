from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from gui.AlgoResultsWidget import AlgoResultsWidget
import sys

import dataset
import algorithm


data = dataset.load_all_datasets()[1]
algos = algorithm.load_algorithms()

app = QApplication([])
tab = AlgoResultsWidget(algos[0])
tab.show()
sys.exit(app.exec())

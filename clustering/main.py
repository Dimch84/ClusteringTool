from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from gui.AlgoResultsWidget import *
import sys

import dataset
import algorithm


data = dataset.load_all_datasets()[1]
algos = algorithm.load_algorithms()

app = QApplication([])
tab = AlgoResultsWidget(algos[0])
tab.show()


for algo in algos:
    print(algo.run(data.data, data.num_of_classes))
sys.exit(app.exec())

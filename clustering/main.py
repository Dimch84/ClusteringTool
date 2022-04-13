from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from gui.AlgoResultsWidget import AlgoResultsWidget
from gui.StatisticsWidget import StatisticsWidget
from sklearn import datasets
import sklearn.metrics as sm
from sklearn.cluster import KMeans, AgglomerativeClustering
import sys

import dataset
import algorithm


data = dataset.load_all_datasets()[1]
algos = algorithm.load_algorithms()

app = QApplication(sys.argv)
tab = AlgoResultsWidget(algos[0])
tab.show()
sys.exit(app.exec())
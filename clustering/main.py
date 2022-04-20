from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

from sklearn import datasets
import sklearn.metrics as sm
from sklearn.cluster import KMeans, AgglomerativeClustering
import sys

import dataset
import algorithm

from clustering.gui.App import App

data = dataset.load_all_datasets()[1]
algos = algorithm.load_algorithms()

app = QApplication(sys.argv)
ex = App()
ex.show()
sys.exit(app.exec())
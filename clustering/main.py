from PyQt5.QtWidgets import QApplication
import sys

from clustering.presenter.Presenter import Presenter

app = QApplication(sys.argv)
presenter = Presenter()
sys.exit(app.exec())

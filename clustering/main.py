from PyQt5.QtWidgets import QApplication
import sys

from clustering.gui.App import App

app = QApplication(sys.argv)
ex = App()
ex.show()
sys.exit(app.exec())

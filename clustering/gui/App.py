from collections.abc import Callable

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QGridLayout, QComboBox, \
    QStackedWidget, QAction, QFileDialog, QDialog
from PyQt5.QtCore import QSettings

from clustering.algorithm import load_algorithms
from clustering.dataset import load_all_datasets
from clustering.gui.AddAlgoDialog import AddAlgoDialog
from clustering.gui.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('clustering')
        self.setGeometry(70, 100, 1800, 900)

        self.datasets = {dataset.name: dataset for dataset in load_all_datasets()}
        self.dataset_selector = self.__create_selector()
        self.current_dataset = self.dataset_selector.currentText()
        self.tab_widget = QStackedWidget()
        self.windows = {}
        self.__change_current_dataset(self.current_dataset)

        self.add_tab_button = QPushButton('Add algorithm')
        self.add_tab_button.clicked.connect(self.__add_tab_to_current_widget)

        layout = QGridLayout()
        layout.addWidget(self.dataset_selector, 0, 0, 1, 1)
        layout.addWidget(self.add_tab_button, 1, 0, 1, 1)
        layout.addWidget(self.tab_widget, 2, 0, 2, 10)
        self.setLayout(layout)

    def __add_tab_to_current_widget(self):
        dataset = self.datasets[self.current_dataset]
        add_algo_dialog = AddAlgoDialog(self)
        if add_algo_dialog.exec() == QDialog.Accepted:
            res = add_algo_dialog.get_result()
            algo_name = res.algo_name
            num_of_clusters = res.num_of_clusters
            algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
            self.tab_widget.currentWidget().addTab(
                AlgoResultsTab(algo=algorithms[algo_name], dataset=dataset, num_of_clusters=num_of_clusters), algo_name)

    def __create_selector(self):
        selector = QComboBox()
        selector.addItems(self.datasets)
        selector.activated[str].connect(self.__change_current_dataset)
        return selector

    def __change_current_dataset(self, dataset_name: str):
        self.current_dataset = dataset_name
        if self.current_dataset not in self.windows:
            new_widget = QTabWidget()
            new_widget.setMovable(True)
            new_widget.setTabsClosable(True)
            new_widget.tabCloseRequested.connect(lambda index: new_widget.removeTab(index))
            self.windows[self.current_dataset] = new_widget
            self.tab_widget.addWidget(new_widget)
        self.tab_widget.setCurrentWidget(self.windows[self.current_dataset])

    def save_session(self, file_name: str = "__last_run.ini"):
        session = QSettings(file_name, QSettings.IniFormat)
        data = {}
        for dataset in self.windows:
            window = self.windows[dataset]
            data[dataset] = []
            cnt = window.count()
            for i in range(0, cnt):
                tab = window.widget(i)
                data[dataset].append({
                    "name": tab.algo.name,
                    "num_of_clusters": tab.num_of_clusters,
                    "results": tab.results
                })
        session.setValue("data", data)
        session.sync()

    def reload_session(self, file_name: str = "__last_run.ini"):
        session = QSettings(file_name, QSettings.IniFormat)
        data = session.value("data")
        if data is None:
            return
        algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
        for dataset in data:
            self.__change_current_dataset(dataset)
            for tab in data[dataset]:
                algo_name = tab["name"]
                self.tab_widget.currentWidget().addTab(
                    AlgoResultsTab(algorithms[algo_name],
                                   self.datasets[dataset],
                                   num_of_clusters=tab["num_of_clusters"],
                                   results=tab["results"]),
                    algo_name)
        self.tab_widget.setCurrentWidget(self.windows[self.current_dataset])


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(CentralWidget())
        self.centralWidget().reload_session()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(self.create_new_action('&Save session', 'Ctrl+S', self.save_session))
        file_menu.addAction(self.create_new_action('&Load session', 'Ctrl+O', self.load_session))
        file_menu.addAction(self.create_new_action('&New session', 'Ctrl+N', self.new_session))

    def create_new_action(self, name: str, shortcut: str, handler: Callable):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    def save_session(self):
        name = QFileDialog.getSaveFileName(self, 'Save session', filter='*.ini')
        self.centralWidget().save_session(name[0])

    def load_session(self):
        name = QFileDialog.getOpenFileName(self, 'Load session', filter='*.ini')
        self.centralWidget().close()
        self.setCentralWidget(CentralWidget())
        self.centralWidget().reload_session(name[0])

    def new_session(self):
        self.centralWidget().close()
        self.setCentralWidget(CentralWidget())

    def closeEvent(self, e):
        self.centralWidget().save_session()

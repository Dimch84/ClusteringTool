from collections.abc import Callable
import shutil
import os
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QPushButton, QGridLayout, QComboBox, \
    QStackedWidget, QAction, QFileDialog, QDialog, QErrorMessage, QMessageBox
from PyQt5.QtCore import QSettings

from clustering.scores import scores
from clustering.algorithm import load_algorithms, load_algorithms_from_module
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
            extra_params = res.extra_params
            selected_scores = res.selected_scores
            algorithms = {algorithm.name: algorithm for algorithm in load_algorithms()}
            pos = self.tab_widget.currentWidget().addTab(
                AlgoResultsTab(algo=algorithms[algo_name],
                               dataset=dataset,
                               params={"k": num_of_clusters} | extra_params,
                               score_names=selected_scores), algo_name)
            self.tab_widget.currentWidget().setCurrentIndex(pos)

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
                    "params": tab.params,
                    "score_names": tab.score_names,
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
                                   params=tab["params"],
                                   score_names=tab["score_names"],
                                   results=tab["results"]),
                    algo_name)
        self.tab_widget.setCurrentWidget(self.windows[self.current_dataset])


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(CentralWidget())
        self.centralWidget().reload_session()
        self.setGeometry(70, 100, 1800, 900)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(self.create_new_action('&Save session', 'Ctrl+S', self.save_session))
        file_menu.addAction(self.create_new_action('&Load session', 'Ctrl+O', self.load_session))
        file_menu.addAction(self.create_new_action('&New session', 'Ctrl+N', self.new_session))

        library_menu = menu_bar.addMenu('&Library')
        library_menu.addAction(self.create_new_action('&Load new algorithm', 'Ctrl+Shift+A', self.add_new_algorithm))

    def create_new_action(self, name: str, shortcut: str, handler: Callable):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    @staticmethod
    def show_error(msg: str):
        error = QErrorMessage()
        error.showMessage(msg)
        error.exec_()

    def save_session(self):
        name = QFileDialog.getSaveFileName(self, 'Save session', filter='*.ini')[0]
        self.centralWidget().save_session(name)

    def load_session(self):
        name = QFileDialog.getOpenFileName(self, 'Load session', filter='*.ini')[0]
        if name:
            self.centralWidget().close()
            self.setCentralWidget(CentralWidget())
            self.centralWidget().reload_session(name)

    def new_session(self):
        self.centralWidget().close()
        self.setCentralWidget(CentralWidget())

    def add_new_algorithm(self):
        file = QFileDialog.getOpenFileName(self, 'Load session', filter='*.py')[0]
        if not file:
            return
        basename = os.path.basename(file)
        new_file = os.path.join('algorithms', basename)
        if os.path.exists(new_file):
            self.show_error(f"File with name {basename} is already added to algorithms!")
            return
        shutil.copy(file, new_file)
        try:
            new_algos = load_algorithms_from_module(basename)
        except AttributeError:
            self.show_error(f"Variable 'algorithms' was not found in file!")
            os.remove(new_file)
            return
        QMessageBox.information(self, "Info", f"Added new algorithms: {', '.join(it.name for it in new_algos)}")

    def closeEvent(self, e):
        self.centralWidget().save_session()

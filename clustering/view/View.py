from collections.abc import Callable
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QPushButton, QGridLayout, QComboBox, \
    QStackedWidget, QAction, QFileDialog, QErrorMessage, QMessageBox, QSizePolicy

from clustering.model.Model import Model
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoRun
from clustering.view.AddAlgoDialog import AddAlgoDialog
from clustering.view.AddDatasetDialog import AddDatasetDialog
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab
from clustering.view.GenerateDatasetDialog import GenerateDatasetDialog


class CentralWidget(QWidget):
    def __init__(self, presenter):
        super().__init__()
        self.setWindowTitle("Clustering")

        self.presenter = presenter

        self.dataset_selector = QComboBox()
        self.dataset_selector.currentTextChanged.connect(self.presenter.change_cur_dataset)

        self.tab_widget = QStackedWidget()
        self.windows = {}

        self.add_tab_button = QPushButton("Add algorithm")
        self.add_tab_button.clicked.connect(self.presenter.add_algo_run_pushed)

        layout = QGridLayout()
        layout.addWidget(self.dataset_selector, 0, 0, 1, 1)
        layout.addWidget(self.add_tab_button, 1, 0, 1, 1)
        layout.addWidget(self.tab_widget, 2, 0, 2, 10)
        self.setLayout(layout)

    def show_add_algo_run_dialog(self, algo_run_attr):
        add_algo_dialog = AddAlgoDialog(algo_run_dialog_attr=algo_run_attr)
        return None if not add_algo_dialog.exec() else add_algo_dialog.get_result()

    def add_dataset(self, dataset_name: str):
        self.dataset_selector.addItem(dataset_name)
        if dataset_name not in self.windows:
            new_widget = QTabWidget()
            new_widget.setMovable(True)
            new_widget.setTabsClosable(True)
            new_widget.tabCloseRequested.connect(lambda index, name=dataset_name:
                                                 self.presenter.remove_algo_run_pushed(self.windows[name]["tabs"][index]))
            self.windows[dataset_name] = {"widget": new_widget, "tabs": list([])}
            self.tab_widget.addWidget(new_widget)

    def add_results_tab(self, algo_run: AlgoRun):
        self.windows[algo_run.dataset_name]["tabs"].append(algo_run)
        # TODO check if tab was added
        self.windows[algo_run.dataset_name]["widget"].addTab(AlgoResultsTab(algo_run), algo_run.algo_name)

    def remove_results_tab(self, algo_run: AlgoRun):
        for idx, x in enumerate(self.windows[algo_run.dataset_name]["tabs"]):
            if x.algo_name == algo_run.algo_name and \
                    x.dataset_name == algo_run.dataset_name and \
                    x.params == algo_run.params and \
                    set(x.calculated_scores.keys()) == set(algo_run.calculated_scores.keys()):
                del self.windows[algo_run.dataset_name]["tabs"][idx]
                # TODO check if tab was removed
                self.windows[algo_run.dataset_name]["widget"].removeTab(idx)
                return


class View(QMainWindow):
    def __init__(self, presenter):
        super().__init__()
        self.setGeometry(70, 100, 1600, 900)
        self.presenter = presenter

        self.central_widget = CentralWidget(presenter)
        self.setCentralWidget(self.central_widget)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(self.create_new_action('&Save session', 'Ctrl+S', self.presenter.save_session_pushed))
        file_menu.addAction(self.create_new_action('&Load session', 'Ctrl+O', self.presenter.load_session_pushed))
        file_menu.addAction(self.create_new_action('&New session', 'Ctrl+N', self.presenter.new_session_pushed))

        library_menu = menu_bar.addMenu('&Library')
        library_menu.addAction(self.create_new_action('&Load new algorithm', 'Ctrl+Shift+A',
                                                      self.presenter.add_algo_pushed))
        library_menu.addAction(self.create_new_action('&Load new dataset', 'Ctrl+Shift+D',
                                                      self.presenter.add_dataset_pushed))
        library_menu.addAction(self.create_new_action('&Generate new dataset', 'Ctrl+Shift+G',
                                                      self.presenter.generate_new_dataset_pushed))

    def show_error(self, msg: str):
        error = QErrorMessage(self)
        error.showMessage(msg)
        error.exec_()

    def show_information(self, msg: str):
        QMessageBox.information(self, "Info", msg)

    def load_from_model(self, model: Model):
        self.central_widget.close()
        self.central_widget = CentralWidget(self.presenter)
        self.setCentralWidget(self.central_widget)

        for dataset in model.datasets:
            self.add_dataset(dataset.name)
        for algo_run in model.algo_runs:
            self.add_algo_run(AlgoRun(
                algo_name=algo_run.algo_run_attrs.algo.name,
                dataset_name=algo_run.algo_run_attrs.dataset.name,
                data=algo_run.algo_run_attrs.dataset.data,
                results=algo_run.results,
                params=algo_run.algo_run_attrs.params,
                calculated_scores=algo_run.calculated_scores
            ))

    def add_dataset(self, dataset_name: str):
        self.central_widget.add_dataset(dataset_name)

    def change_cur_dataset(self, dataset_name: str):
        if dataset_name in self.central_widget.windows:
            self.central_widget.tab_widget.setCurrentWidget(self.central_widget.windows[dataset_name]["widget"])

    def show_save_file_dialog(self, caption: str, filter: str):
        return QFileDialog.getSaveFileName(self, caption=caption, filter=filter)[0]

    def show_open_file_dialog(self, caption: str, filter: str):
        return QFileDialog.getOpenFileName(self, caption=caption, filter=filter)[0]

    def show_add_dataset_dialog(self, columns: list[str]):
        add_dataset_dialog = AddDatasetDialog(columns=columns)
        return None if not add_dataset_dialog.exec() else add_dataset_dialog.get_result()

    def show_generate_dataset_dialog(self):
        gen_dataset_dialog = GenerateDatasetDialog()
        return None if not gen_dataset_dialog.exec() else gen_dataset_dialog.get_result()

    def show_add_algo_run_dialog(self, algo_run_attr):
        return self.central_widget.show_add_algo_run_dialog(algo_run_attr=algo_run_attr)

    def add_algo_run(self, algo_run: AlgoRun):
        self.central_widget.add_results_tab(algo_run)

    def remove_algo_run(self, algo_run: AlgoRun):
        self.central_widget.remove_results_tab(algo_run)

    def create_new_action(self, name: str, shortcut: str, handler: Callable):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    def closeEvent(self, e):
        self.presenter.save_session()

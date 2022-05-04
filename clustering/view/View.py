import uuid
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QPushButton, QGridLayout, QComboBox, \
    QStackedWidget, QAction, QFileDialog, QErrorMessage, QMessageBox

from clustering.model.Model import Model
from clustering.view.AddAlgoRunDialog import AddAlgoRunDialog
from clustering.view.AddDatasetDialog import AddDatasetDialog
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab
from clustering.presenter.Presenter import Presenter
from clustering.view.GenerateDatasetDialog import GenerateDatasetDialog


class CentralWidget(QWidget):
    def __init__(self, presenter: Presenter):
        super().__init__()
        self.setWindowTitle("Clustering")

        self.presenter = presenter
        self.windows: dict[uuid, dict] = {}
        self.dataset_selector = QComboBox()
        self.tab_widget = QStackedWidget()
        self.add_tab_button = QPushButton("Add algorithm")
        self.dataset_selector.currentIndexChanged.connect(
            lambda index: presenter.change_cur_dataset(self.dataset_selector.itemData(index)))
        self.add_tab_button.clicked.connect(presenter.add_algo_run_pushed)
        layout = QGridLayout()
        layout.addWidget(self.dataset_selector, 0, 0, 1, 1)
        layout.addWidget(self.add_tab_button, 1, 0, 1, 1)
        layout.addWidget(self.tab_widget, 2, 0, 2, 10)
        self.setLayout(layout)

    @dataclass
    class AddAlgoDialogResult:
        dataset_id: uuid
        algo_id: uuid
        params: dict
        score_ids: list[uuid]

    def show_add_algo_run_dialog(self, algo_ids: [uuid], score_ids: [uuid]):
        add_algo_dialog = AddAlgoRunDialog(self.presenter, algo_ids, score_ids)
        if add_algo_dialog.exec():
            result = add_algo_dialog.get_result()
            return self.AddAlgoDialogResult(
                dataset_id=self.dataset_selector.currentData(),
                algo_id=result.algo_id,
                params=result.params,
                score_ids=result.score_ids)
        else:
            return None

    def add_dataset(self, dataset_id: uuid):
        dataset_name = self.presenter.get_dataset_name(dataset_id)
        new_widget = QTabWidget()
        new_widget.setMovable(True)
        new_widget.setTabsClosable(True)
        new_widget.tabCloseRequested.connect(partial(self.remove_results_tab_listener, dataset_id=dataset_id))
        self.windows[dataset_id] = {"widget": new_widget, "tabs": list([])}
        self.tab_widget.addWidget(new_widget)
        self.dataset_selector.addItem(dataset_name, dataset_id)

    def change_cur_dataset(self, dataset_id: uuid):
        self.tab_widget.setCurrentWidget(self.windows[dataset_id]["widget"])

    def remove_results_tab_listener(self, index: int, dataset_id: uuid):
        self.presenter.remove_algo_run_pushed(self.windows[dataset_id]["tabs"][index])

    def add_results_tab(self, algo_run_id: uuid):
        results = self.presenter.get_algo_run_results(algo_run_id)
        algo_name = self.presenter.get_algo_name(results.config.algorithm_id)
        dataset_id = results.config.dataset_id
        self.windows[dataset_id]["widget"].addTab(AlgoResultsTab(self.presenter, algo_run_id), algo_name)
        self.windows[dataset_id]["tabs"].append(algo_run_id)

    def remove_results_tab(self, algo_run_id: uuid):
        for dataset_id in self.windows.keys():
            if algo_run_id in self.windows[dataset_id]["tabs"]:
                index = self.windows[dataset_id]["tabs"].index(algo_run_id)
                self.windows[dataset_id]["widget"].removeTab(index)
                del self.windows[dataset_id]["tabs"][index]


class View(QMainWindow):
    def __init__(self, presenter: Presenter):
        super().__init__()

        self.setGeometry(70, 100, 1600, 900)
        self.presenter = presenter
        self.central_widget = CentralWidget(presenter)
        self.setCentralWidget(self.central_widget)
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(self.create_new_action('&Save session', 'Ctrl+S', presenter.save_session_pushed))
        file_menu.addAction(self.create_new_action('&Load session', 'Ctrl+O', presenter.load_session_pushed))
        file_menu.addAction(self.create_new_action('&New session', 'Ctrl+N', presenter.new_session_pushed))
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

        for dataset_id in model.datasets.keys():
            self.add_dataset(dataset_id)
        for algo_run_result in model.algo_run_results:
            self.add_algo_run_results(algo_run_result)

    def add_dataset(self, dataset_id: uuid):
        self.central_widget.add_dataset(dataset_id)

    def change_cur_dataset(self, dataset_id: uuid):
        self.central_widget.change_cur_dataset(dataset_id)

    def add_algo_run_results(self, algo_run_id: uuid):
        self.central_widget.add_results_tab(algo_run_id)

    def remove_algo_run_results(self, algo_run_id: uuid):
        self.central_widget.remove_results_tab(algo_run_id)

    def show_save_file_dialog(self, caption: str, filter: str):
        return QFileDialog.getSaveFileName(self, caption, filter)[0]

    def show_open_file_dialog(self, caption: str, filter: str):
        return QFileDialog.getOpenFileName(self, caption, filter)[0]

    def show_add_dataset_dialog(self, columns: list[str]):
        add_dataset_dialog = AddDatasetDialog(columns=columns)
        return None if not add_dataset_dialog.exec() else add_dataset_dialog.get_result()

    def show_generate_dataset_dialog(self):
        gen_dataset_dialog = GenerateDatasetDialog()
        return None if not gen_dataset_dialog.exec() else gen_dataset_dialog.get_result()

    def show_add_algo_run_dialog(self, algo_ids: [uuid], score_ids: [uuid]):
        return self.central_widget.show_add_algo_run_dialog(algo_ids, score_ids)

    def create_new_action(self, name: str, shortcut: str, handler: Callable):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    def closeEvent(self, e):
        self.presenter.close_listener()

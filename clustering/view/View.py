import uuid
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QPushButton, QGridLayout, QComboBox, \
    QStackedWidget, QAction, QFileDialog, QErrorMessage, QMessageBox, QGroupBox, QCheckBox, QVBoxLayout, QListWidget

from clustering.model.Model import Model, AlgoRunConfig
from clustering.view.AddAlgoRunDialog import AddAlgoRunDialog
from clustering.view.AddDatasetDialog import AddDatasetDialog
from clustering.view.AlgoCompareWidget import AlgoCompareWidget
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab
from clustering.presenter.Presenter import Presenter
from clustering.view.GenerateDatasetDialog import GenerateDatasetDialog


@dataclass
class AddAlgoDialogResult:
    name: str
    config: AlgoRunConfig


@dataclass()
class _Window:
    algo_run_ids: list[uuid]
    tab_widget: QTabWidget


class CentralWidget(QWidget):
    def __init__(self, presenter: Presenter):
        super().__init__()

        self.presenter = presenter
        self.windows: dict[uuid, _Window] = {}
        self.dataset_selector = QComboBox()
        self.stacked_widget = QStackedWidget()
        self.add_tab_button = QPushButton("Add algorithm")
        self.dataset_selector.currentIndexChanged.connect(
            lambda index: presenter.change_cur_dataset(self.dataset_selector.itemData(index)))
        self.add_tab_button.clicked.connect(presenter.add_algo_run_pushed)
        layout = QGridLayout()
        layout.addWidget(self.dataset_selector, 0, 0, 1, 1)
        layout.addWidget(self.add_tab_button, 1, 0, 1, 1)
        layout.addWidget(self.stacked_widget, 2, 0, 2, 10)
        self.setLayout(layout)

    def show_add_algo_run_dialog(self, algo_ids: [uuid], score_ids: [uuid]):
        add_algo_dialog = AddAlgoRunDialog(self, self.presenter, algo_ids, score_ids)
        if add_algo_dialog.exec():
            result = add_algo_dialog.get_result()
            return AddAlgoDialogResult(
                name=result.name,
                config=AlgoRunConfig(
                    dataset_id=self.dataset_selector.currentData(),
                    algorithm_id=result.algo_id,
                    params=result.params,
                    score_ids=result.score_ids
                )
            )
        else:
            return None

    def add_dataset(self, dataset_id: uuid):
        dataset_name = self.presenter.get_dataset_name(dataset_id)
        new_widget = QTabWidget()
        new_widget.setMovable(True)
        new_widget.setTabsClosable(True)
        new_widget.tabCloseRequested.connect(partial(self.remove_results_tab_listener, dataset_id=dataset_id))
        self.windows[dataset_id] = _Window(list([]), new_widget)
        self.stacked_widget.addWidget(new_widget)
        self.dataset_selector.addItem(dataset_name, dataset_id)

    def change_cur_dataset(self, dataset_id: uuid):
        self.stacked_widget.setCurrentWidget(self.windows[dataset_id].tab_widget)

    def remove_results_tab_listener(self, index: int, dataset_id: uuid):
        self.presenter.remove_algo_run_pushed(self.windows[dataset_id].algo_run_ids[index])

    def add_results_tab(self, algo_run_id: uuid):
        results = self.presenter.get_algo_run_results(algo_run_id)
        tab = AlgoResultsTab(self.presenter, algo_run_id)
        self.windows[results.config.dataset_id].tab_widget.addTab(tab, results.name)
        self.windows[results.config.dataset_id].algo_run_ids.append(algo_run_id)

    def remove_results_tab(self, algo_run_id: uuid):
        for dataset_id in self.windows.keys():
            if algo_run_id in self.windows[dataset_id].algo_run_ids:
                index = self.windows[dataset_id].algo_run_ids.index(algo_run_id)
                self.windows[dataset_id].tab_widget.removeTab(index)
                del self.windows[dataset_id].algo_run_ids[index]

    def change_algo_run_results_tab(self, algo_run_id: uuid, next_algo_run_id: uuid):
        results = self.presenter.get_algo_run_results(next_algo_run_id)
        dataset_id = results.config.dataset_id
        index = self.windows[dataset_id].algo_run_ids.index(algo_run_id)
        next_tab = AlgoResultsTab(self.presenter, next_algo_run_id)
        prev_index = self.windows[dataset_id].tab_widget.currentIndex()
        self.windows[dataset_id].tab_widget.removeTab(index)
        self.windows[dataset_id].tab_widget.insertTab(index, next_tab, results.name)
        self.windows[dataset_id].algo_run_ids[index] = next_algo_run_id
        self.windows[dataset_id].tab_widget.setCurrentIndex(prev_index)


class OtherCentralWidget(QWidget):
    def __init__(self, presenter: Presenter):
        super().__init__()
        self.presenter = presenter
        self.datasets = []
        self.included_datasets = set()
        self.algo_configs = QListWidget()
        self.algo_configs_list = []
        self.dataset_selector = QGroupBox()
        self.dataset_selector.setLayout(QVBoxLayout())
        self.score_selector = self.__create_score_selector()
        self.score_selector.currentIndexChanged.connect(self.__change_score)

        self.add_algo_button = QPushButton("Add algorithm configuration")
        self.add_algo_button.clicked.connect(self.presenter.add_algo_config_pushed)
        self.go_btn = QPushButton("Show results")
        self.go_btn.clicked.connect(self.launch_all)

        layout = QVBoxLayout()
        layout.addWidget(self.dataset_selector)
        layout.addWidget(self.score_selector)
        layout.addWidget(self.add_algo_button)
        layout.addWidget(self.algo_configs)
        layout.addWidget(self.go_btn)
        self.setLayout(layout)

    def __create_score_selector(self):
        result = QComboBox()
        for id in self.presenter.get_score_ids():
            result.addItem(self.presenter.get_score_name(id), id)
        self.use_score = result.itemData(0)
        return result

    def __change_score(self, ind: int):
        self.use_score = self.score_selector.itemData(ind)

    def add_dataset(self, dataset_id: uuid):
        self.datasets.append(dataset_id)
        checkBox = QCheckBox(self.presenter.get_dataset_name(dataset_id))
        checkBox.stateChanged.connect(lambda x, id=dataset_id:
                                      self.included_datasets.add(id) if x else self.included_datasets.remove(id))
        self.dataset_selector.layout().addWidget(checkBox)

    def add_algo_config(self, algo_ids: [uuid]):
        add_algo_dialog = AddAlgoRunDialog(self, self.presenter, algo_ids, [])
        if add_algo_dialog.exec():
            result = add_algo_dialog.get_result()
            self.algo_configs.addItem(result.name)
            self.algo_configs_list.append(result)

    def add_results_tab(self, algo_run_id):
        pass

    def launch_all(self):
        dialog = AlgoCompareWidget(self.presenter, self.included_datasets, self.algo_configs_list, self.use_score)
        dialog.exec()

    def change_algo_run_results_tab(self, algo_run_id: uuid, next_algo_run_id: uuid):
        pass


class View(QMainWindow):
    def __init__(self, presenter: Presenter, compare_mode: bool = False):
        super().__init__()
        self.setWindowTitle("ClusteringTool")
        self.setGeometry(70, 100, 1600, 900)
        self.presenter = presenter
        self.compare_mode = compare_mode
        self.central_widget = OtherCentralWidget(presenter) if compare_mode else CentralWidget(presenter)
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
        self.central_widget = OtherCentralWidget(self.presenter) if self.compare_mode else CentralWidget(self.presenter)
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

    def change_algo_run_results(self, algo_run_id: uuid, next_algo_run_id: uuid):
        self.central_widget.change_algo_run_results_tab(algo_run_id, next_algo_run_id)

    def show_save_file_dialog(self, caption: str, filter: str):
        return QFileDialog.getSaveFileName(self, caption=caption, filter=filter)[0]

    def show_open_file_dialog(self, caption: str, filter: str):
        return QFileDialog.getOpenFileName(self, caption=caption, filter=filter)[0]

    def show_add_dataset_dialog(self, feature_cols: list[str], title_cols: list[str]):
        add_dataset_dialog = AddDatasetDialog(feature_cols=feature_cols, title_cols=title_cols)
        return None if not add_dataset_dialog.exec() else add_dataset_dialog.get_result()

    def show_generate_dataset_dialog(self):
        gen_dataset_dialog = GenerateDatasetDialog(self)
        return None if not gen_dataset_dialog.exec() else gen_dataset_dialog.get_result()

    def show_add_algo_run_dialog(self, algo_ids: [uuid], score_ids: [uuid]):
        return self.central_widget.show_add_algo_run_dialog(algo_ids, score_ids)

    def add_algo_config(self, algo_ids: [uuid]):
        self.central_widget.add_algo_config(algo_ids)

    def create_new_action(self, name: str, shortcut: str, handler: Callable):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    def closeEvent(self, e):
        self.presenter.close_listener()

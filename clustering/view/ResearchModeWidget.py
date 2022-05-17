import uuid
from functools import partial

from PyQt5.QtWidgets import QWidget, QComboBox, QStackedWidget, QPushButton, QGridLayout, QTabWidget

from clustering.model.Model import AlgoRunConfig, AlgoConfig
from clustering.presenter.Presenter import Presenter
from clustering.view.AddAlgoRunDialog import AddAlgoRunDialog
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab
from dataclasses import dataclass


@dataclass()
class _Window:
    algo_run_ids: list[uuid]
    tab_widget: QTabWidget


class ResearchModeWidget(QWidget):
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

    def show_add_algo_run_dialog(self, algo_ids: [uuid]) -> AlgoRunConfig | None:
        add_algo_dialog = AddAlgoRunDialog(self, self.presenter, algo_ids)
        if add_algo_dialog.exec():
            algo_config = add_algo_dialog.get_result()
            return AlgoRunConfig(
                    algo_config=algo_config,
                    dataset_id=self.dataset_selector.currentData(),
                    score_ids=self.presenter.get_score_ids()
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

    def add_algo_config(self, algo_config: AlgoConfig):
        pass

    def add_results_tab(self, algo_run_id: uuid):
        algo_run_results = self.presenter.get_algo_run_results(algo_run_id)
        config = algo_run_results.config
        tab = AlgoResultsTab(self.presenter, algo_run_id)
        self.windows[config.dataset_id].tab_widget.addTab(tab, config.algo_config.name)
        self.windows[config.dataset_id].algo_run_ids.append(algo_run_id)

    def remove_results_tab(self, algo_run_id: uuid):
        for dataset_id in self.windows.keys():
            if algo_run_id in self.windows[dataset_id].algo_run_ids:
                index = self.windows[dataset_id].algo_run_ids.index(algo_run_id)
                self.windows[dataset_id].tab_widget.removeTab(index)
                del self.windows[dataset_id].algo_run_ids[index]

    def change_algo_run_results_tab(self, algo_run_id: uuid, next_algo_run_id: uuid):
        results = self.presenter.get_algo_run_results(next_algo_run_id)
        config = results.config
        dataset_id = config.dataset_id
        index = self.windows[dataset_id].algo_run_ids.index(algo_run_id)
        next_tab = AlgoResultsTab(self.presenter, next_algo_run_id)
        prev_index = self.windows[dataset_id].tab_widget.currentIndex()
        self.windows[dataset_id].tab_widget.removeTab(index)
        self.windows[dataset_id].tab_widget.insertTab(index, next_tab, config.algo_config.name)
        self.windows[dataset_id].algo_run_ids[index] = next_algo_run_id
        self.windows[dataset_id].tab_widget.setCurrentIndex(prev_index)
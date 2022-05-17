import uuid

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QPushButton, QVBoxLayout, QFrame, QListWidget, \
    QListWidgetItem, QComboBox, QCheckBox

from clustering.model.Model import AlgoConfig
from clustering.presenter.Presenter import Presenter
from clustering.view.AddAlgoRunDialog import AddAlgoRunDialog
from clustering.view.AlgoCompareWidget import AlgoCompareWidget
from clustering.view.WidgetHelper import WidgetHelper


class CompareModeWidget(QWidget, WidgetHelper):
    def __init__(self, presenter: Presenter):
        super().__init__()
        self.presenter = presenter
        self.datasets = []
        self.included_datasets = set()
        self.dataset_selector = QGroupBox("Select datasets:")
        self.dataset_selector.setLayout(QHBoxLayout())
        self.score_selector = self.__create_score_selector()

        self.go_btn = QPushButton("Show results")
        self.go_btn.clicked.connect(self.launch_all)

        layout = QVBoxLayout()
        layout.addWidget(self.dataset_selector)
        layout.addWidget(self.add_title_to_widget("Select scoring:", self.score_selector))
        layout.addWidget(self.add_title_to_widget("Added configurations:", self.__create_algo_configs()))
        layout.addWidget(self.go_btn)
        self.setLayout(layout)

    def __create_algo_configs(self):
        widget = QFrame()
        widget.setLayout(QVBoxLayout())
        self.algo_configs = QListWidget()
        self.algo_configs.setLayout(QVBoxLayout())
        self.algo_configs.itemDoubleClicked.connect(self.__algo_config_clicked)
        buttons = QFrame()
        buttons.setLayout(QHBoxLayout())
        add_button = QPushButton('+')
        add_button.setMaximumSize(40, 40)
        add_button.clicked.connect(self.presenter.add_algo_config_pushed)
        remove_button = QPushButton('-')
        remove_button.setMaximumSize(40, 40)
        remove_button.clicked.connect(self.__remove_algo_config)
        buttons.layout().addWidget(add_button)
        buttons.layout().addWidget(remove_button)
        widget.layout().addWidget(self.algo_configs)
        widget.layout().addWidget(buttons)
        return widget

    def __get_algo_configs(self):
        algo_configs = []
        for ind in range(self.algo_configs.count()):
            algo_configs.append(self.algo_configs.item(ind).data(Qt.UserRole))
        return algo_configs

    def __algo_config_clicked(self, item: QListWidgetItem):
        config = item.data(Qt.UserRole)
        add_algo_dialog = AddAlgoRunDialog(self, self.presenter, [config.algo_id], config)
        if add_algo_dialog.exec():
            result = add_algo_dialog.get_result()
            item.setData(Qt.UserRole, result)
            item.setText(result.name)
        self.presenter.update_algo_configs(self.__get_algo_configs())

    def __remove_algo_config(self):
        for item in self.algo_configs.selectedItems():
            self.algo_configs.takeItem(self.algo_configs.row(item))
        self.presenter.update_algo_configs(self.__get_algo_configs())

    def __create_score_selector(self):
        result = QComboBox()
        for id in self.presenter.get_score_ids():
            result.addItem(self.presenter.get_score_name(id), id)
        self.use_score = result.itemData(0)
        result.currentIndexChanged.connect(self.__change_score)
        return result

    def __change_score(self, ind: int):
        self.use_score = self.score_selector.itemData(ind)

    def add_dataset(self, dataset_id: uuid):
        self.datasets.append(dataset_id)
        checkBox = QCheckBox(self.presenter.get_dataset_name(dataset_id))
        checkBox.stateChanged.connect(lambda x, id=dataset_id:
                                      self.included_datasets.add(id) if x else self.included_datasets.remove(id))
        self.dataset_selector.layout().addWidget(checkBox)

    def add_algo_config(self, config: AlgoConfig):
        item = QListWidgetItem(config.name)
        item.setData(Qt.UserRole, config)
        self.algo_configs.addItem(item)

    def show_add_algo_config(self, algo_ids: [uuid]):
        add_algo_dialog = AddAlgoRunDialog(self, self.presenter, algo_ids)
        if add_algo_dialog.exec():
            result = add_algo_dialog.get_result()
            item = QListWidgetItem(result.name)
            item.setData(Qt.UserRole, result)
            self.algo_configs.addItem(item)
        self.presenter.update_algo_configs(self.__get_algo_configs())

    def launch_all(self):
        algo_configs_list = []
        for ind in range(0, self.algo_configs.count()):
            algo_configs_list.append(self.algo_configs.item(ind).data(Qt.UserRole))
        dialog = AlgoCompareWidget(self.presenter, self.included_datasets, algo_configs_list, self.use_score)
        dialog.exec()

    def add_results_tab(self, algo_run_id):
        pass

    def change_algo_run_results_tab(self, algo_run_id: uuid, next_algo_run_id: uuid):
        pass
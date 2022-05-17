import uuid
from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView

from clustering.model.Model import AlgoRunConfig
from clustering.presenter.Presenter import Presenter
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoResultsTab
from clustering.view.WidgetHelper import WidgetHelper
from PyQt5.QtCore import Qt


class NumericItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem):
        lhs, rhs = self.data(Qt.UserRole), other.data(Qt.UserRole)
        if rhs is None:
            return False
        if lhs is None:
            return True
        return lhs < rhs


class AlgoCompareWidget(QDialog, WidgetHelper):
    def __init__(self, presenter: Presenter, dataset_ids: [uuid], algo_configs: [AlgoRunConfig], score_id: uuid):
        super().__init__()
        self.presenter = presenter
        self.dataset_ids = dataset_ids
        self.algo_configs = algo_configs
        self.score_id = score_id

        layout = QVBoxLayout()
        for dataset_id in self.dataset_ids:
            layout.addWidget(self.__generate_table(dataset_id))
        self.setLayout(layout)

    def __generate_table(self, dataset_id: uuid):
        score_name = self.presenter.get_score_name(self.score_id)
        table = QTableWidget(len(self.algo_configs), 2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem('Algorithm'))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(f'Score ({score_name}):'))
        for i, algo_config in enumerate(self.algo_configs):
            algo_run_id = self.presenter.launch_algo_run(
                AlgoRunConfig(
                    algo_config=algo_config,
                    dataset_id=dataset_id,
                    score_ids=[self.score_id]
                )
            )
            score = None if algo_run_id is None else self.presenter.get_algo_run_results(algo_run_id).scores[score_name]
            item = QTableWidgetItem(algo_config.name)
            item.setData(Qt.UserRole, algo_run_id)
            table.setItem(i, 0, item)
            item = NumericItem('None' if score is None else '{:.4f}'.format(score))
            item.setData(Qt.UserRole, score)
            table.setItem(i, 1, item)
        table.sortItems(1, Qt.DescendingOrder)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.itemDoubleClicked.connect(self.__cell_clicked)
        return self.add_title_to_widget(self.presenter.get_dataset_name(dataset_id), table)

    def __cell_clicked(self, item):
        if item.column() == 0:
            algo_run_id = item.data(Qt.UserRole)
            if algo_run_id is not None:
                dialog = QDialog()
                dialog.setLayout(QVBoxLayout())
                dialog.layout().addWidget(AlgoResultsTab(self.presenter, algo_run_id))
                dialog.exec()

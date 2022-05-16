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
        if (lhs is None) != (rhs is None):
            return (lhs is None) > (rhs is None)
        return lhs < rhs


class AlgoCompareWidget(QDialog, WidgetHelper):
    def __init__(self, presenter: Presenter, dataset_ids: [uuid], algo_run_configs: [uuid], score_id: uuid):
        super().__init__()
        self.presenter = presenter
        self.dataset_ids = dataset_ids
        self.algo_run_configs = algo_run_configs
        self.score_id = score_id

        layout = QVBoxLayout()
        for dataset_id in self.dataset_ids:
            layout.addWidget(self.__generate_table(dataset_id))
        self.setLayout(layout)

    def __generate_table(self, dataset_id: uuid):
        score_name = self.presenter.get_score_name(self.score_id)
        table = QTableWidget(len(self.algo_run_configs), 2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem('Algorithm'))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(f'Score ({score_name}):'))
        for i, algo_config in enumerate(self.algo_run_configs):
            algo_run_id = self.presenter.launch_algo_run(
                AlgoRunConfig(
                    name=algo_config.name,
                    dataset_id=dataset_id,
                    algorithm_id=algo_config.algo_id,
                    params=algo_config.params,
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
        table.itemDoubleClicked.connect(lambda item, table=table: self.cell_clicked(table, item))
        return self.add_title_to_widget(self.presenter.get_dataset_name(dataset_id), table)

    def cell_clicked(self, table, item):
        if item.column() == 0:
            algo_run_id = item.data(Qt.UserRole)
            if algo_run_id is not None:
                dialog = QDialog()
                dialog.setLayout(QVBoxLayout())
                dialog.layout().addWidget(AlgoResultsTab(self.presenter, algo_run_id))
                dialog.exec()

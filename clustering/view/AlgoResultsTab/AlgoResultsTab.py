import uuid

from PyQt5.QtWidgets import QWidget, QGridLayout, QFormLayout, QLabel, QGroupBox, QVBoxLayout, QPushButton, QDialog, \
    QTableWidget, QTableWidgetItem, QScrollArea

from clustering.view.AlgoResultsTab.ClusteringView import ClusteringView
from clustering.presenter.Presenter import Presenter
from clustering.view.AlgoParamsSetter import AlgoParamsSetter


class ScoresWidget(QScrollArea):
    def __init__(self, scores: dict):
        super().__init__()
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)
        for score_name in scores.keys():
            layout.addRow(QLabel(f"{score_name}: "), QLabel(str(scores[score_name])))
        self.setWidget(widget)


class AlgoResultsTab(QWidget):
    def __init__(self, presenter: Presenter, algo_run_id: uuid):
        super().__init__()
        self.presenter = presenter
        self.algo_run_id = algo_run_id

        algo_run_results = presenter.get_algo_run_results(algo_run_id)
        self.points = presenter.get_dataset_points(algo_run_results.config.dataset_id)
        self.feature_names = presenter.get_dataset_feature_names(algo_run_results.config.dataset_id)
        self.pred = algo_run_results.pred
        self.parameters_widget = AlgoParamsSetter(
            params=presenter.get_algo_params(algo_run_results.config.algo_config.algo_id),
            values=algo_run_results.config.algo_config.params
        )
        self.scores_widget = ScoresWidget(algo_run_results.scores)
        self.clustering_view = ClusteringView(self.points, self.pred, self.presenter, algo_run_results.config.dataset_id)
        self.show_in_analytic_mode_button = QPushButton("Show table")
        self.show_in_analytic_mode_button.clicked.connect(self.show_in_analytic_mode_listener)
        self.rerun_button = QPushButton("Rerun algorithm")
        self.rerun_button.clicked.connect(self.rerun_algo_button_listener)
        layout = QGridLayout()
        layout.addWidget(self.add_title_to_widget("Clustering", self.clustering_view), 0, 0, 2, 3)
        layout.addWidget(self.add_title_to_widget("Scores", self.scores_widget), 0, 3, 1, 1)
        layout.addWidget(self.add_title_to_widget("Parameters", self.parameters_widget), 1, 3, 1, 1)
        layout.addWidget(self.show_in_analytic_mode_button, 2, 0, 1, 3)
        layout.addWidget(self.rerun_button, 2, 3, 1, 1)
        self.setLayout(layout)

    def rerun_algo_button_listener(self):
        self.presenter.rerun_algo_pushed(
            algo_run_id=self.algo_run_id,
            params=self.parameters_widget.get_params()
        )

    def export_results_button_listener(self):
        self.presenter.export_algo_run_results(self.algo_run_id)

    def show_in_analytic_mode_listener(self):
        dialog = QDialog()
        dialog.setWindowTitle("Results")
        dialog.setMinimumSize(800, 700)
        layout = QVBoxLayout()
        table = QTableWidget(len(self.points), len(self.feature_names) + 1)
        for i, title in enumerate(self.feature_names):
            table.setHorizontalHeaderItem(i, QTableWidgetItem(title))
        table.setHorizontalHeaderItem(len(self.feature_names), QTableWidgetItem("Cluster"))
        for i, point in enumerate(self.points):
            for j, val in enumerate(point):
                table.setItem(i, j, QTableWidgetItem("{:.4f}".format(val)))
            table.setItem(i, len(point), QTableWidgetItem(str(self.pred[i])))
        export_button = QPushButton("Export to csv")
        export_button.clicked.connect(self.export_results_button_listener)
        layout.addWidget(table)
        layout.addWidget(export_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_title_to_widget(self, title: str, widget: QWidget):
        result = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        result.setLayout(layout)
        return result

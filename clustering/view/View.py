import uuid
from collections.abc import Callable

from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QErrorMessage, QMessageBox

from clustering.model.Model import Model, AlgoRunConfig, AppMode, AlgoConfig
from clustering.view.AddDatasetDialog import AddDatasetDialog
from clustering.presenter.Presenter import Presenter
from clustering.view.CompareModeWidget import CompareModeWidget
from clustering.view.GenerateDatasetDialog import GenerateDatasetDialog
from clustering.view.ResearchModeWidget import ResearchModeWidget


class View(QMainWindow):
    def __init__(self, presenter: Presenter):
        super().__init__()
        self.setWindowTitle("ClusteringTool")
        self.setGeometry(70, 100, 1600, 900)
        self.presenter = presenter
        self.mode = self.central_widget = None
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
        if self.central_widget is not None:
            self.central_widget.close()
        self.mode = model.mode
        self.central_widget = CompareModeWidget(self.presenter) if self.mode == AppMode.CompareMode\
            else ResearchModeWidget(self.presenter)
        self.setCentralWidget(self.central_widget)
        for dataset_id in model.datasets.keys():
            self.add_dataset(dataset_id)
        for algo_run_result in model.algo_run_results:
            self.add_algo_run_results(algo_run_result)
        for algo_config in model.algo_configs:
            self.add_algo_config(algo_config)

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

    def show_add_algo_run_dialog(self, algo_ids: [uuid]) -> AlgoRunConfig:
        return self.central_widget.show_add_algo_run_dialog(algo_ids)

    def show_add_algo_config(self, algo_ids: [uuid]):
        self.central_widget.show_add_algo_config(algo_ids)

    def add_algo_config(self, algo_config: AlgoConfig):
        self.central_widget.add_algo_config(algo_config)

    def create_new_action(self, name: str, shortcut: str, handler: Callable):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(handler)
        return action

    def closeEvent(self, e):
        self.presenter.close_listener()

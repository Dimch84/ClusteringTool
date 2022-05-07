from PyQt5.QtWidgets import QDialog, QFormLayout, QWidget
from dataclasses import dataclass

from clustering.view.DialogHelper import DialogHelper, PositiveIntValidator, NonNegativeDoubleValidator


@dataclass
class GenerateDatasetDialogResults:
    name: str = "Unnamed"
    n_samples: int = 100
    num_of_classes: int = 5
    n_features: int = 2
    cluster_std: float = 0.2


class GenerateDatasetDialog(QDialog, DialogHelper):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.result = GenerateDatasetDialogResults()

        self.setWindowTitle("Dataset editor")
        self.setMinimumSize(600, 300)

        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_dataset_name_input())
        self.layout.addWidget(self.__create_nsamples_input())
        self.layout.addWidget(self.__create_numofclasses_input())
        self.layout.addWidget(self.__create_nfeatures_input())
        self.layout.addWidget(self.__create_clusterstd_input())
        self.layout.addWidget(self.create_button_box())
        self.setLayout(self.layout)

    def __create_dataset_name_input(self):
        return self.create_named_text_field("Dataset's name:", self.__change_dataset_name,
                                            self.result.name, set_title_horizontally=True)

    def __create_nsamples_input(self):
        return self.create_named_text_field("Number of samples:", self.__change_nsamples,
                                            self.result.n_samples, PositiveIntValidator(), True)

    def __create_numofclasses_input(self):
        return self.create_named_text_field("Number of clusters:", self.__change_numofclasses,
                                            self.result.num_of_classes, PositiveIntValidator(), True)

    def __create_nfeatures_input(self):
        return self.create_named_text_field("Number of features (dimensions):", self.__change_nfeatures,
                                            self.result.n_features, PositiveIntValidator(), True)

    def __create_clusterstd_input(self):
        return self.create_named_text_field("Standard deviation:", self.__change_clusterstd,
                                            self.result.cluster_std, NonNegativeDoubleValidator(), True)

    def __change_dataset_name(self, name: str):
        self.result.name = name

    def __change_nsamples(self, n_samples: str):
        self.result.n_samples = int(n_samples)

    def __change_numofclasses(self, num_of_classes: str):
        self.result.num_of_classes = int(num_of_classes)

    def __change_nfeatures(self, n_features: str):
        self.result.n_features = int(n_features)

    def __change_clusterstd(self, cluster_std: str):
        self.result.cluster_std = int(cluster_std)

    def get_result(self):
        return self.result

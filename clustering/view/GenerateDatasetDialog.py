from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QCheckBox, QGroupBox, QDialogButtonBox, QLineEdit
from dataclasses import dataclass


@dataclass
class GenerateDatasetDialogResults:
    name: str = "Unnamed"
    n_samples: int = 100
    num_of_classes: int = 5
    n_features: int = 2
    cluster_std: float = 0.2


class GenerateDatasetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.result = GenerateDatasetDialogResults()

        self.setWindowTitle("Dataset editor")
        self.setMinimumSize(600, 300)

        self.layout = QFormLayout()
        self.layout.addWidget(self.__create_dataset_name_input())
        self.layout.addWidget(self.__create_nsamples_input())
        self.layout.addWidget(self.__create_numofclasses_input())
        self.layout.addWidget(self.__create_nfeatures_input())
        self.layout.addWidget(self.__create_clusterstd_input())
        #self.layout.addWidget(self.__create_cols_selector())
        #self.layout.addWidget(self.__create_normalise_box())
        self.layout.addWidget(self.__create_button_box())
        self.setLayout(self.layout)

    def __create_named_field(self, name: str, widget):
        res = QGroupBox(name)
        res.setLayout(QVBoxLayout())
        res.layout().addWidget(widget)
        return res

    def __create_named_text_field(self, name: str, default_value, action):
        res = QLineEdit()
        res.setText(str(default_value))
        res.textChanged.connect(action)
        return self.__create_named_field(name, res)

    def __create_button_box(self):
        QBtn = QDialogButtonBox.Ok
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    def __create_dataset_name_input(self):
        return self.__create_named_text_field("Dataset's name", self.result.name,
                                              self.__change_dataset_name)

    def __create_nsamples_input(self):
        return self.__create_named_text_field("Number of samples", self.result.n_samples,
                                              self.__change_nsamples)

    def __create_numofclasses_input(self):
        return self.__create_named_text_field("Number of clusters", self.result.num_of_classes,
                                              self.__change_numofclasses)

    def __create_nfeatures_input(self):
        return self.__create_named_text_field("Number of features (dimensions)", self.result.n_features,
                                              self.__change_nfeatures)

    def __create_clusterstd_input(self):
        return self.__create_named_text_field("Standard deviation", self.result.cluster_std,
                                              self.__change_clusterstd)

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

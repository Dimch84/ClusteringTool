from functools import partial
from dataclasses import dataclass

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QComboBox, QLineEdit, QFormLayout, QWidget, QVBoxLayout, \
    QCheckBox, QSizePolicy, QHBoxLayout, QLabel, QGroupBox


@dataclass
class AddAlgoDialogResults:
    algo_name: str
    params: dict
    selected_scores: list


class AlgoSelector(QComboBox):
    def __init__(self, algo_attrs):
        super().__init__()
        for algo in algo_attrs:
            self.addItem(algo.name, algo)


class AlgoParamsSetter(QWidget):
    def __init__(self, algo_attr):
        super().__init__()
        self.params: dict = {}
        layout = QVBoxLayout()

        for param in algo_attr.int_params:
            line_edit = QLineEdit()
            line_edit.textChanged.connect(partial(self.change_int_param_value, param_name=param.name))
            layout.addWidget(self.add_title_to_widget(param.name, line_edit))

        for param in algo_attr.selectable_params:
            box = QComboBox()
            box.addItems(param.items)
            box.currentTextChanged.connect(partial(self.change_selectable_param_value, param_name=param.name))
            self.change_selectable_param_value(box.currentText(), param.name)
            layout.addWidget(self.add_title_to_widget(param.name, box))
        self.setLayout(layout)

    def add_title_to_widget(self, title: str, widget: QWidget):
        result = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(widget)
        result.setLayout(layout)
        return result

    def change_int_param_value(self, value: str, param_name: str):
        if value.isdecimal():
            self.params |= {param_name: int(value)}
        else:
            self.params |= {param_name: None}

    def change_selectable_param_value(self, value: str, param_name: str):
        self.params |= {param_name: value}

    def get_params(self):
        return self.params


class ScoresSelector(QWidget):
    def __init__(self, scores: [str]):
        super().__init__()
        self.selected_scores = list([])

        layout = QVBoxLayout()
        for score in scores:
            checkBox = QCheckBox(score.name)
            checkBox.stateChanged.connect(partial(self.change_score_state, score_name=score.name))
            layout.addWidget(checkBox)
        self.setLayout(layout)

    def change_score_state(self, checked: bool, score_name: str):
        if checked:
            self.selected_scores.append(score_name)
        else:
            self.selected_scores.remove(score_name)

    def get_selected_scores(self):
        return self.selected_scores


class AddAlgoDialog(QDialog):
    def __init__(self, algo_run_dialog_attr):
        super().__init__()
        self.setWindowTitle("Algorithm settings")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.setMinimumSize(600, 0)

        self.algo_run_dialog_attr = algo_run_dialog_attr

        self.algo_selector = AlgoSelector(algo_run_dialog_attr.algo_attrs)
        self.algo_selector.currentIndexChanged.connect(
            lambda idx: self.change_cur_algo(self.algo_selector.itemData(idx))
        )

        self.cur_algo = self.algo_selector.currentData()

        self.algo_params_setter = AlgoParamsSetter(self.cur_algo)
        self.algo_params_titled_setter = self.add_title_to_widget("Parameters", self.algo_params_setter)

        self.scores_selector = ScoresSelector(algo_run_dialog_attr.score_attrs)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QFormLayout()
        self.layout.addWidget(self.add_title_to_widget("Algorithm", self.algo_selector))
        self.layout.addWidget(self.algo_params_titled_setter)
        self.layout.addWidget(self.add_title_to_widget("Scores", self.scores_selector))
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def add_title_to_widget(self, title: str, widget: QWidget):
        result = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        result.setLayout(layout)
        return result

    def change_cur_algo(self, algo_attr):
        new_algo_param_setter = AlgoParamsSetter(algo_attr)
        new_algo_param_titled_setter = self.add_title_to_widget("Parameters", new_algo_param_setter)
        self.layout.replaceWidget(self.algo_params_titled_setter, new_algo_param_titled_setter)
        self.algo_params_setter.close()
        self.algo_params_titled_setter.close()
        self.algo_params_setter = new_algo_param_setter
        self.algo_params_titled_setter = new_algo_param_titled_setter

    def get_result(self):
        return AddAlgoDialogResults(
            algo_name=self.algo_selector.currentText(),
            params=self.algo_params_setter.get_params(),
            selected_scores=self.scores_selector.get_selected_scores()
        )

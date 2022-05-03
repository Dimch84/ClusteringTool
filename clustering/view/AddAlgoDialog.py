from functools import partial
from dataclasses import dataclass

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QComboBox, QFormLayout, QWidget, QVBoxLayout, \
    QCheckBox, QSizePolicy

from clustering.view.DialogHelper import DialogHelper


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


class AlgoParamsSetter(QWidget, DialogHelper):
    def __init__(self, algo_attr):
        super().__init__()
        self.params: dict = {}
        layout = QVBoxLayout()

        for param in algo_attr.int_params:
            line_edit = self.create_named_text_field(param.name,
                                                     partial(self.change_int_param_value, param_name=param.name),
                                                     validator=QIntValidator(),
                                                     set_title_horizontally=True
                                                     )
            layout.addWidget(line_edit)

        for param in algo_attr.selectable_params:
            box = QComboBox()
            box.addItems(param.items)
            box.currentTextChanged.connect(partial(self.change_selectable_param_value, param_name=param.name))
            self.change_selectable_param_value(box.currentText(), param.name)
            layout.addWidget(self.add_title_to_widget(param.name, box, True))
        self.setLayout(layout)

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


class AddAlgoDialog(QDialog, DialogHelper):
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

        self.layout = QFormLayout()
        self.layout.addWidget(self.add_title_to_widget("Algorithm", self.algo_selector))
        self.layout.addWidget(self.algo_params_titled_setter)
        self.layout.addWidget(self.add_title_to_widget("Scores", self.scores_selector))
        self.layout.addWidget(self.create_button_box())
        self.setLayout(self.layout)

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

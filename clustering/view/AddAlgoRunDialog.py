import uuid
from functools import partial
from dataclasses import dataclass

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QComboBox, QFormLayout, QWidget, QVBoxLayout, \
    QCheckBox, QSizePolicy

from clustering.view.DialogHelper import DialogHelper

from clustering.presenter.Presenter import Presenter


class AlgoSelector(QComboBox):
    def __init__(self, presenter: Presenter, algorithms: [uuid]):
        super().__init__()
        for algo_id in algorithms:
            algo_name = presenter.get_algo_name(algo_id)
            self.addItem(algo_name, algo_id)


class AlgoParamsSetter(QWidget, DialogHelper):
    def __init__(self, presenter: Presenter, algo_id: uuid):
        super().__init__()
        self.params: dict = {}
        layout = QVBoxLayout()

        algo_params = presenter.get_algo_params(algo_id)

        for param in algo_params.int_params:
            line_edit = self.create_named_text_field(param.name,
                                                     partial(self.change_int_param_value, param_name=param.name),
                                                     validator=QIntValidator(),
                                                     set_title_horizontally=True
                                                     )
            layout.addWidget(line_edit)

        for param in algo_params.selectable_params:
            box = QComboBox()
            box.addItems(param.items)
            box.currentTextChanged.connect(partial(self.change_selectable_param_value, param_name=param.name))
            self.change_selectable_param_value(box.currentText(), param.name)
            layout.addWidget(self.add_title_to_widget(param.name, box))
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
    def __init__(self, presenter: Presenter, score_ids: [uuid]):
        super().__init__()
        self.selected_scores: list[uuid] = []

        layout = QVBoxLayout()
        for score_id in score_ids:
            score_name = presenter.get_score_name(score_id)
            checkBox = QCheckBox(score_name)
            checkBox.stateChanged.connect(partial(self.change_score_state, score_id=score_id))
            layout.addWidget(checkBox)
        self.setLayout(layout)

    def change_score_state(self, checked: bool, score_id: uuid):
        if checked:
            self.selected_scores.append(score_id)
        else:
            self.selected_scores.remove(score_id)

    def get_selected_scores(self):
        return self.selected_scores


class AddAlgoRunDialog(QDialog, DialogHelper):
    @dataclass
    class AddAlgoDialogResult:
        algo_id: uuid
        params: dict
        score_ids: list[uuid]

    def __init__(self, presenter: Presenter, algo_ids: [uuid], score_ids: [uuid]):
        super().__init__()
        self.setWindowTitle("Algorithm settings")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.setMinimumSize(600, 0)

        self.presenter = presenter

        self.algo_selector = AlgoSelector(presenter, algo_ids)
        self.algo_selector.currentIndexChanged.connect(self.change_cur_algo_listener)

        self.algo_params_setter = AlgoParamsSetter(presenter, self.algo_selector.currentData())
        self.algo_params_titled_setter = self.add_title_to_widget("Parameters", self.algo_params_setter)

        self.scores_selector = ScoresSelector(presenter, score_ids)

        self.layout = QFormLayout()
        self.layout.addWidget(self.add_title_to_widget("Algorithm", self.algo_selector))
        self.layout.addWidget(self.algo_params_titled_setter)
        self.layout.addWidget(self.add_title_to_widget("Scores", self.scores_selector))
        self.layout.addWidget(self.create_button_box())
        self.setLayout(self.layout)

    def change_cur_algo_listener(self, index: int):
        self.change_cur_algo(self.algo_selector.itemData(index))

    def change_cur_algo(self, algo_id: uuid):
        new_algo_param_setter = AlgoParamsSetter(self.presenter, algo_id)
        new_algo_param_titled_setter = self.add_title_to_widget("Parameters", new_algo_param_setter)
        if self.algo_params_titled_setter is not None:
            self.layout.replaceWidget(self.algo_params_titled_setter, new_algo_param_titled_setter)
            self.algo_params_setter.close()
            self.algo_params_titled_setter.close()
        self.algo_params_setter = new_algo_param_setter
        self.algo_params_titled_setter = new_algo_param_titled_setter

    def get_result(self):
        return self.AddAlgoDialogResult(
            algo_id=self.algo_selector.currentData(),
            params=self.algo_params_setter.get_params(),
            score_ids=self.scores_selector.get_selected_scores())

from copy import copy
from dataclasses import dataclass
from functools import partial

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout

from clustering.model.Algorithm import AlgoParams
from clustering.view.DialogHelper import DialogHelper


@dataclass
class ParamsSetterAttr:
    params: AlgoParams
    values: dict


class AlgoParamsSetter(QWidget, DialogHelper):
    def __init__(self, attr: ParamsSetterAttr):
        super().__init__()
        self.params: dict = copy(attr.values)
        algo_params = copy(attr.params)

        layout = QVBoxLayout()
        for param in algo_params.int_params:
            line_edit = self.create_named_text_field(
                name=param.name,
                action=partial(self.change_int_param_value, param_name=param.name),
                default_value=copy(self.params[param.name]),
                validator=QIntValidator(),
                set_title_horizontally=True
            )
            layout.addWidget(line_edit)

        for param in algo_params.selectable_params:
            box = QComboBox()
            box.addItems(param.items)
            box.currentTextChanged.connect(partial(self.change_selectable_param_value, param_name=param.name))
            box.setCurrentIndex(param.items.index(copy(self.params[param.name])))
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

from copy import copy

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGroupBox, QSizePolicy

from clustering.model.Algorithm import AlgoParams
from clustering.view.CheckBoxParamEditor import CheckBoxParamEditor
from clustering.view.LineParamEditor import LineParamEditor
from clustering.view.SelectableParamEditor import SelectableParamEditor


def add_title_to_widget(title: str, widget: QWidget):
    result = QGroupBox(title)
    layout = QVBoxLayout()
    layout.addWidget(widget)
    result.setLayout(layout)
    return result


class AlgoParamsSetter(QScrollArea):
    def __init__(self, params: AlgoParams, values: dict):
        super().__init__()

        self.params: dict = copy(values)
        self.int_param_editors: dict = {}
        self.float_param_editors: dict = {}
        self.bool_param_editors: dict = {}
        self.selectors: dict = {}

        widget = QWidget()
        layout = QVBoxLayout(widget)

        for param_name in params.int_params:
            specified = param_name in values.keys()
            value = None if not specified else None if values[param_name] is None else str(values[param_name])
            editor = LineParamEditor(specified, value)
            self.int_param_editors[param_name] = editor
            layout.addWidget(add_title_to_widget(param_name, editor))

        for param_name in params.float_params:
            specified = param_name in values.keys()
            value = None if not specified else None if values[param_name] is None else str(values[param_name])
            editor = LineParamEditor(specified, value)
            self.float_param_editors[param_name] = editor
            layout.addWidget(add_title_to_widget(param_name, editor))

        for param_name in params.bool_params:
            specified = param_name in values.keys()
            value = None if not specified else None if values[param_name] is None else bool(values[param_name])
            editor = CheckBoxParamEditor(specified, value)
            self.bool_param_editors[param_name] = editor
            layout.addWidget(add_title_to_widget(param_name, editor))

        for param in params.selectable_params:
            specified = param.name in values.keys()
            value = None if not specified else None if values[param.name] is None else str(values[param.name])
            editor = SelectableParamEditor(param.items, specified, value)
            self.selectors[param.name] = editor
            layout.addWidget(add_title_to_widget(param.name, editor))
        self.setWidget(widget)

    def get_params(self):
        res: dict = {}
        for param_name in self.int_param_editors:
            if self.int_param_editors[param_name].is_specified():
                value = self.int_param_editors[param_name].get_value()
                res[param_name] = None if value is None else int(value)
        for param_name in self.float_param_editors:
            if self.float_param_editors[param_name].is_specified():
                value = self.float_param_editors[param_name].get_value()
                res[param_name] = None if value is None else float(value)
        for param_name in self.bool_param_editors:
            if self.bool_param_editors[param_name].is_specified():
                value = self.bool_param_editors[param_name].get_value()
                res[param_name] = None if value is None else bool(value)
        for param_name in self.selectors:
            if self.selectors[param_name].is_specified():
                value = self.selectors[param_name].get_value()
                res[param_name] = None if value is None else str(value)
        return res

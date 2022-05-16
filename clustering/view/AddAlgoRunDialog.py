import uuid

from PyQt5.QtWidgets import QDialog, QComboBox, QFormLayout, QWidget, QSizePolicy, QLineEdit

from clustering.model.Algorithm import AlgoParams
from clustering.model.Model import AlgoConfig
from clustering.view.WidgetHelper import WidgetHelper
from clustering.presenter.Presenter import Presenter
from clustering.view.AlgoParamsSetter import AlgoParamsSetter, ParamsSetterAttr


class AlgoSelector(QComboBox):
    def __init__(self, presenter: Presenter, algorithms: [uuid]):
        super().__init__()
        for algo_id in algorithms:
            algo_name = presenter.get_algo_name(algo_id)
            self.addItem(algo_name, algo_id)


class AddAlgoRunDialog(QDialog, WidgetHelper):
    def __init__(self, parent: QWidget, presenter: Presenter, algo_ids: [uuid], init_value: AlgoConfig = None):
        super().__init__(parent)
        self.setWindowTitle("Algorithm settings")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.setMinimumSize(600, 0)

        self.presenter = presenter
        self.name_input = QLineEdit("")
        self.algo_selector = AlgoSelector(presenter, algo_ids)
        self.algo_selector.currentIndexChanged.connect(self.change_cur_algo_listener)
        self.algo_params_setter = self.__create_param_setter(self.algo_selector.currentData())
        self.algo_params_titled_setter = self.add_title_to_widget("Parameters", self.algo_params_setter)

        self.layout = QFormLayout()
        self.layout.addWidget(self.add_title_to_widget("Name", self.name_input))
        self.layout.addWidget(self.add_title_to_widget("Algorithm", self.algo_selector))
        self.layout.addWidget(self.algo_params_titled_setter)
        self.layout.addWidget(self.create_button_box())
        self.setLayout(self.layout)

        if init_value is not None:
            self.name_input.setText(init_value.name)
            for ind in range(self.algo_selector.count()):
                if self.algo_selector.itemData(ind) == init_value.algo_id:
                    self.algo_selector.setCurrentIndex(ind)
                    break
            self.change_cur_algo(init_value.algo_id, init_value.params)

    def change_cur_algo_listener(self, index: int):
        self.change_cur_algo(self.algo_selector.itemData(index))

    def change_cur_algo(self, algo_id: uuid, param_values: dict = None):
        new_algo_param_setter = self.__create_param_setter(algo_id, param_values)
        new_algo_param_titled_setter = self.add_title_to_widget("Parameters", new_algo_param_setter)
        if self.algo_params_titled_setter is not None:
            self.layout.replaceWidget(self.algo_params_titled_setter, new_algo_param_titled_setter)
            self.algo_params_setter.close()
            self.algo_params_titled_setter.close()
        self.algo_params_setter = new_algo_param_setter
        self.algo_params_titled_setter = new_algo_param_titled_setter

    def __create_param_setter(self, algo_id: uuid, values: dict = None):
        params: AlgoParams = self.presenter.get_algo_params(algo_id)
        return AlgoParamsSetter(ParamsSetterAttr(
            params=params,
            values=values if values is not None else {p.name: "0" for p in params.int_params} |
                                                     {p.name: p.items[0] for p in params.selectable_params},
        ))

    def get_result(self):
        return AlgoConfig(
            name=self.name_input.text(),
            algo_id=self.algo_selector.currentData(),
            params=self.algo_params_setter.get_params(),
        )

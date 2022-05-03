import os
import shutil
from dataclasses import dataclass

from clustering.model.Dataset import load_all_datasets, DuplicatedDatasetNameError, generate_random_dataset
from clustering.algorithms.default_algorithms import algorithms
from clustering.scores.default_scores import scores
from clustering.view.AlgoResultsTab.AlgoResultsTab import AlgoRun
from clustering.model.Model import Model, DuplicatedAlgoRunError
from clustering.view.View import View
from clustering.model.Algorithm import load_algorithms, load_algorithms_from_module
from clustering.model.Model import AlgoRunAttrs
from clustering.model.Dataset import load_from_csv, normalise_dataset, Dataset


@dataclass
class IntParam:
    name: str
    min_bound: int
    max_bound: int


@dataclass
class SelectableParam:
    name: str
    items: [str]


@dataclass
class AlgoAttr:
    name: str
    int_params: [IntParam]
    selectable_params: [SelectableParam]


@dataclass
class ScoreAttr:
    name: str


@dataclass
class AlgoRunDialogAttr:
    algo_attrs: [AlgoAttr]
    score_attrs: [ScoreAttr]


class Presenter:
    def __init__(self):
        self.model = Model(
            datasets=load_all_datasets(),
            algorithms=load_algorithms(),
            scores=scores
        )
        self.load_session()
        self.view = View(self)
        self.view.load_from_model(self.model)
        self.scores = scores
        self.view.show()

    def add_algo_run_pushed(self):
        algo_run_dialog_attr = AlgoRunDialogAttr(
            algo_attrs=[AlgoAttr(
                name=algo.name,
                int_params=algo.params.int_params,
                selectable_params=algo.params.selectable_params)
                for algo in self.model.algorithms],
            score_attrs=[ScoreAttr(name=score.name) for score in self.scores])

        result = self.view.show_add_algo_run_dialog(algo_run_attr=algo_run_dialog_attr)
        if result is None:
            return

        score_dict = {score.name: score for score in self.model.scores}
        algorithms_dict = {algo.name: algo for algo in self.model.algorithms}

        algo_run_attrs = AlgoRunAttrs(
            dataset=self.model.current_dataset,
            algo=algorithms_dict[result.algo_name],
            params=result.params,
            scores=list([score_dict[score_name] for score_name in result.selected_scores])
        )

        try:
            algo_run = self.model.add_algo_run(algo_run_attrs)
            self.view.add_algo_run(AlgoRun(
                algo_name=algo_run.algo_run_attrs.algo.name,
                dataset_name=self.model.current_dataset.name,
                data=self.model.current_dataset.data,
                results=algo_run.results,
                params=algo_run.algo_run_attrs.params,
                calculated_scores=algo_run.calculated_scores
            ))
        except DuplicatedAlgoRunError:
            self.view.show_error(str("Algorithm with such parameters has already been launched"))
        except KeyError:
            self.view.show_error(str("Some parameters weren't configured"))
        except ValueError:
            self.view.show_error(str("Invalid parameters"))

    def remove_algo_run_pushed(self, algo_run_attr):
        algo_run = next(algo_run for algo_run in self.model.algo_runs
                        if algo_run.algo_run_attrs.algo.name == algo_run_attr.algo_name and
                        algo_run.algo_run_attrs.dataset.name == algo_run_attr.dataset_name and
                        algo_run.algo_run_attrs.params == algo_run_attr.params and
                        set([score.name for score in algo_run.algo_run_attrs.scores]) ==
                            set(algo_run_attr.calculated_scores.keys())
        )
        self.model.remove_algo_run(algo_run)
        self.view.remove_algo_run(algo_run_attr)

    def add_algo_pushed(self):
        file = self.view.show_open_file_dialog(
            caption="Load new algorithm",
            filter="*.py"
        )
        if not file:
            return
        basename = os.path.basename(file)
        new_file = os.path.join('algorithms', basename)
        shutil.copy(file, new_file)
        try:
            new_algorithms = load_algorithms_from_module(basename)
        except AttributeError:
            self.view.show_error(f"Variable 'algorithms' was not found in file!")
            os.remove(new_file)
            return
        for algorithm in new_algorithms:
            self.model.add_algorithm(algorithm)
        self.view.show_information(f"Added new algorithms: {', '.join(it.name for it in new_algorithms)}")

    def __add_dataset(self, dataset: Dataset):
        try:
            self.model.add_dataset(dataset)
            self.view.add_dataset(dataset.name)
        except DuplicatedDatasetNameError:
            self.view.show_error("Dataset with this name already exists; please, try again with another name")

    def add_dataset_pushed(self):
        file = self.view.show_open_file_dialog(
            caption="Load new dataset",
            filter="*.csv"
        )
        if not file:
            return

        df = load_from_csv(file)
        result = self.view.show_add_dataset_dialog(df.columns.tolist())
        if result is None:
            return

        df = df[result.included_cols]
        data = df.to_numpy()
        if result.normalise:
            data = normalise_dataset(data)
        dataset = Dataset(
            data=data,
            num_of_classes=None,
            target=None,
            feature_names=df.columns.tolist(),
            name=result.name
        )
        self.__add_dataset(dataset)

    def generate_new_dataset_pushed(self):
        params = self.view.show_generate_dataset_dialog()
        if params is None:
            return
        dataset = generate_random_dataset(name=params.name,
                                          n_samples=params.n_samples,
                                          num_of_classes=params.num_of_classes,
                                          n_features=params.n_features,
                                          cluster_std=params.cluster_std)
        self.__add_dataset(dataset)

    def change_cur_dataset(self, dataset_name):
        datasets_dict = {dataset.name: dataset for dataset in self.model.datasets}
        self.model.change_cur_dataset(datasets_dict[dataset_name])
        self.view.change_cur_dataset(dataset_name)

    def save_session_pushed(self):
        file = self.view.show_save_file_dialog(
            caption="Save session",
            filter="*.ini"
        )
        self.save_session(file)

    def save_session(self, file="__last_run.ini"):
        if file:
            self.model.save(file)

    def load_session(self, file="__last_run.ini"):
        if file:
            self.model.load(file)

    def load_session_pushed(self):
        file = self.view.show_open_file_dialog(
            caption="Load session",
            filter="*.ini"
        )
        if not file:
            return

        self.save_session()
        self.model = Model(
            datasets=load_all_datasets(),
            algorithms=self.model.algorithms,
            scores=self.scores
        )
        self.model.load(file)
        self.view.load_from_model(self.model)
        self.view.show()

    def new_session_pushed(self):
        self.save_session()
        self.model = Model(
            datasets=load_all_datasets(),
            algorithms=algorithms,
            scores=scores
        )
        self.view.load_from_model(self.model)
        self.view.show()

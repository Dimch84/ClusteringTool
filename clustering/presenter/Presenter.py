import os
import shutil
import uuid

from clustering.model.Algorithm import load_algorithms_from_module, load_algorithms
from clustering.model.Dataset import DuplicatedDatasetNameError, add_dataset
from clustering.model.Model import AlgoRunConfig
from clustering.model.Dataset import load_from_csv, normalise_dataset, Dataset


class DuplicatedAlgoNameError(Exception):
    pass


class Presenter:
    def __init__(self):
        self.model = None
        self.view = None

    def set_model(self, model):
        self.model = model

    def set_view(self, view):
        self.view = view

    def get_algo_name(self, algo_id: uuid):
        return self.model.algorithms[algo_id].name

    def get_algo_params(self, algo_id: uuid):
        return self.model.algorithms[algo_id].params

    def get_dataset_name(self, dataset_id: uuid):
        return self.model.datasets[dataset_id].name

    def get_score_name(self, score_id: uuid):
        return self.model.scores[score_id].name

    def get_algo_run_results(self, algo_run_id: uuid):
        return self.model.algo_run_results[algo_run_id]

    def get_dataset_points(self, dataset_id: uuid):
        return self.model.datasets[dataset_id].data

    def add_algo_run_pushed(self):
        result = self.view.show_add_algo_run_dialog(
            algo_ids=self.model.algorithms.keys(),
            score_ids=self.model.scores.keys()
        )
        if result is None:
            return
        try:
            algo_run_id = self.model.add_algo_run(AlgoRunConfig(
                dataset_id=result.dataset_id,
                algorithm_id=result.algo_id,
                params=result.params,
                score_ids=result.score_ids
            ))
            self.view.add_algo_run_results(algo_run_id)
        except KeyError:
            self.view.show_error(str("Some parameters weren't configured"))
        except ValueError:
            self.view.show_error(str("Invalid parameters"))

    def remove_algo_run_pushed(self, algorithm_id: uuid):
        if self.model.remove_algo_run_results(algorithm_id):
            self.view.remove_algo_run_results(algorithm_id)

    def add_algo_pushed(self):
        file = self.view.show_open_file_dialog("Load new algorithm", "*.py")
        if not file:
            return
        basename = os.path.basename(file)
        new_file = os.path.join('algorithms', basename)
        all_saved_algo_names = set([algo.name for algo in load_algorithms()])
        shutil.copy(file, new_file)

        try:
            new_algos = load_algorithms_from_module(basename)
            new_algo_names = set([algo.name for algo in new_algos])
            if all_saved_algo_names.intersection(new_algo_names):
                raise DuplicatedAlgoNameError

            for algorithm in new_algos:
                self.model.add_algorithm(algorithm)
            self.view.show_information(f"Added new algorithms: {', '.join(it.name for it in new_algos)}")
        except DuplicatedAlgoNameError:
            os.remove(new_file)
            self.view.show_error(f"Algorithm with this name already exists; please, try again with another name")
        except AttributeError:
            os.remove(new_file)
            self.view.show_error(f"Variable 'algorithms' was not found in file!")
            return

    def add_dataset_pushed(self):
        file = self.view.show_open_file_dialog("Load new dataset", "*.csv")
        if not file:
            return
        df = load_from_csv(file)
        result = self.view.show_add_dataset_dialog(df.columns.tolist())
        df = df[result.included_cols]
        data = df.to_numpy()
        if result.normalise:
            data = normalise_dataset(data)
        dataset = Dataset(data, None, None, df.columns.tolist(), result.name)
        try:
            add_dataset(dataset)
            dataset_id = self.model.add_dataset(dataset)
            self.view.add_dataset(dataset_id)
        except DuplicatedDatasetNameError:
            self.view.show_error("Dataset with this name already exists; please, try again with another name")

    def change_cur_dataset(self, dataset_id):
        self.view.change_cur_dataset(dataset_id)

    def save_session_pushed(self):
        file = self.view.show_save_file_dialog("Save session", "*.ini")
        self.model.save(file)

    def load_session_pushed(self):
        file = self.view.show_open_file_dialog("Load session", "*.ini")
        if not file:
            return

        self.model.save()
        self.model.algo_run_results.clear()
        self.model.load(file)
        self.view.load_from_model(self.model)

    def new_session_pushed(self):
        self.model.save()
        self.model.algo_run_results.clear()
        self.view.load_from_model(self.model)

    def close_listener(self):
        self.model.save()

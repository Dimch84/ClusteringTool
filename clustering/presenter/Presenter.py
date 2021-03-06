import os
import shutil
import uuid
import numpy as np
import pandas
from copy import copy

from clustering.model.Dataset import get_cols_with_type, get_feature_cols
from clustering.model.Model import AlgoRunConfig, AlgoRunResults, AlgoConfig
from clustering.model.Dataset import DuplicatedDatasetNameError, add_dataset, generate_random_dataset
from clustering.model.Algorithm import load_algorithms, load_algorithms_from_module
from clustering.model.Dataset import load_from_csv, normalise_dataset, Dataset
from clustering.view.SelectModeDialog import SelectModeDialog


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

    def get_dataset_points(self, dataset_id: uuid):
        return self.model.datasets[dataset_id].data

    def get_dataset_titles(self, dataset_id: uuid):
        return self.model.datasets[dataset_id].titles

    def get_dataset_feature_names(self, dataset_id: uuid):
        return self.model.datasets[dataset_id].feature_names

    def get_score_name(self, score_id: uuid):
        return self.model.scores[score_id].name

    def get_algo_run_results(self, algo_run_id: uuid) -> AlgoRunResults:
        return self.model.algo_run_results[algo_run_id]

    def get_score_ids(self):
        return self.model.scores.keys()

    def update_algo_configs(self, algo_configs: [AlgoConfig]):
        self.model.algo_configs = algo_configs

    def rerun_algo_pushed(self, algo_run_id: uuid, params: dict):
        try:
            prev_results: AlgoRunResults = self.get_algo_run_results(algo_run_id)
            next_algo_run_id = self.model.add_algo_run(AlgoRunConfig(
                algo_config=AlgoConfig(
                    name=prev_results.config.algo_config.name,
                    algo_id=prev_results.config.algo_config.algo_id,
                    params=params
                ),
                dataset_id=prev_results.config.dataset_id,
                score_ids=prev_results.config.score_ids
            ))
            self.model.remove_algo_run_results(algo_run_id)
            self.view.change_algo_run_results(algo_run_id, next_algo_run_id)
        except (KeyError, ValueError, TypeError, OverflowError) as err:
            self.view.show_error(str(err))

    def add_algo_run_pushed(self):
        algo_run_config = self.view.show_add_algo_run_dialog(algo_ids=self.model.algorithms.keys())
        if algo_run_config is None:
            return
        try:
            algo_run_id = self.model.add_algo_run(algo_run_config)
            self.view.add_algo_run_results(algo_run_id)
        except (KeyError, ValueError, TypeError, OverflowError) as err:
            self.view.show_error(str(err))

    def add_algo_config_pushed(self) -> uuid:
        self.view.show_add_algo_config(self.model.algorithms.keys())

    def launch_algo_run(self, algo_run_config):
        try:
            return self.model.add_algo_run(algo_run_config)
        except:
            return None

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

    def __add_dataset(self, dataset: Dataset):
        try:
            add_dataset(dataset)
            dataset_id = self.model.add_dataset(dataset)
            self.view.add_dataset(dataset_id)
        except DuplicatedDatasetNameError:
            self.view.show_error("Dataset with this name already exists; please, try again with another name")

    def add_dataset_pushed(self):
        file = self.view.show_open_file_dialog("Load new dataset", "*.csv")
        if not file:
            return

        df = load_from_csv(file)
        result = self.view.show_add_dataset_dialog(get_feature_cols(df).columns.tolist(),
                                                   get_cols_with_type(df, ['object']).columns.tolist())
        if result is None:
            return

        data = df[result.included_cols].to_numpy()
        if result.normalise:
            data = normalise_dataset(data)
        titles = None if result.title_col is None else df[result.title_col].to_numpy()

        dataset = Dataset(
            data=data,
            num_of_classes=None,
            target=None,
            feature_names=result.included_cols,
            name=result.name,
            titles=titles
        )
        self.__add_dataset(dataset)

    def generate_new_dataset_pushed(self):
        params = self.view.show_generate_dataset_dialog()
        if params is None:
            return
        dataset = generate_random_dataset(
            name=params.name,
            n_samples=params.n_samples,
            num_of_classes=params.num_of_classes,
            n_features=params.n_features,
            cluster_std=params.cluster_std
        )
        self.__add_dataset(dataset)

    def change_cur_dataset(self, dataset_id):
        self.view.change_cur_dataset(dataset_id)

    def save_session_pushed(self):
        file = self.view.show_save_file_dialog("Save session", "*.ini")
        if not file:
            return
        self.model.save(file)

    def load_session_pushed(self):
        file = self.view.show_open_file_dialog("Load session", "*.ini")
        if not file:
            return
        self.model.save()
        self.model.algo_run_results.clear()
        self.model.load_from_file(file)
        self.view.load_from_model(self.model)

    def new_session_pushed(self):
        self.model.save()
        dialog = SelectModeDialog()
        if dialog.exec():
            self.model.reload(dialog.get_result())
            self.view.load_from_model(self.model)
        else:
            self.view.close()

    def export_algo_run_results(self, algo_run_id: uuid):
        file = self.view.show_save_file_dialog("Export results", "*.csv")
        if not file:
            return
        results = self.get_algo_run_results(algo_run_id)
        dataset = self.model.datasets[results.config.dataset_id]

        #print(np.shape(dataset.data)[1])
        data = np.append(np.array(dataset.titles)[np.newaxis].T, dataset.data, 1)
        data = np.append(data, np.array(results.pred)[np.newaxis].T, 1)
        col_names = ["Name"] + copy(dataset.feature_names) + ["Cluster"]
        df = pandas.DataFrame(data=data, columns=col_names)
        df.to_csv(file, index=False)

    def close_listener(self):
        self.model.save()

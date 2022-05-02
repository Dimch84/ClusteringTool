import numpy as np
from dataclasses import dataclass

from PyQt5.QtCore import QSettings

from clustering.model.Algorithm import Algorithm
from clustering.model.Dataset import Dataset, add_dataset
from clustering.model.Score import Score


@dataclass()
class AlgoRunAttrs:
    dataset: Dataset
    algo: Algorithm
    params: dict
    scores: list[Score]


@dataclass()
class AlgoRun:
    algo_run_attrs: AlgoRunAttrs
    results: np.ndarray
    calculated_scores: dict


class DuplicatedAlgoRunError(Exception):
    pass


class Model:
    def __init__(self, datasets: list[Dataset], algorithms: list[Algorithm], scores: list[Score]):
        self.datasets = datasets
        self.current_dataset = datasets[0]
        self.algorithms = algorithms
        self.scores = scores
        self.algo_runs = list([])

    def add_algo_run(self, algo_run_attrs: AlgoRunAttrs):
        result = algo_run_attrs.algo.run(algo_run_attrs.dataset.data, algo_run_attrs.params)
        calculated_scores = {}
        for score in algo_run_attrs.scores:
            score = score
            calculated_scores.update({score.name: score.calc_score(
                data=algo_run_attrs.dataset.data,
                target=algo_run_attrs.dataset.target,
                pred=result
            )})
        algo_run = AlgoRun(
            algo_run_attrs=algo_run_attrs,
            results=result,
            calculated_scores=calculated_scores
        )
        for x in self.algo_runs:
            if x.algo_run_attrs.algo.name == algo_run.algo_run_attrs.algo.name and \
                    x.algo_run_attrs.dataset.name == algo_run.algo_run_attrs.dataset.name and \
                    x.algo_run_attrs.params == algo_run.algo_run_attrs.params and \
                    set(x.algo_run_attrs.scores) == set(algo_run.algo_run_attrs.scores):
                raise DuplicatedAlgoRunError
        self.algo_runs.append(algo_run)
        return algo_run

    def remove_algo_run(self, algo_run: AlgoRun):
        self.algo_runs.remove(algo_run)
        # TODO check if item was removed
        return True

    def change_cur_dataset(self, dataset: Dataset):
        if dataset in self.datasets:
            self.current_dataset = dataset
        # TODO check if item was added
        return True

    def add_dataset(self, dataset: Dataset):
        add_dataset(dataset)  # able to raise DuplicatedDatasetNameError
        self.datasets.append(dataset)
        # TODO check if item was added
        return True

    def add_algorithm(self, algorithm):
        self.algorithms.append(algorithm)
        # TODO check if item was added
        return True

    def save(self, file):
        session = QSettings(file, QSettings.IniFormat)
        data = {}

        for algo_run in self.algo_runs:
            if algo_run.algo_run_attrs.dataset.name not in data.keys():
                data[algo_run.algo_run_attrs.dataset.name] = []
            data[algo_run.algo_run_attrs.dataset.name].append({
                "algo_name": algo_run.algo_run_attrs.algo.name,
                "params": algo_run.algo_run_attrs.params,
                "calculated_scores": algo_run.calculated_scores,
                "results": algo_run.results
            })
        session.setValue("data", data)
        session.sync()

    def load(self, file):
        session = QSettings(file, QSettings.IniFormat)
        data = session.value("data")
        if data is None:
            return

        scores_dict = {score.name: score for score in self.scores}
        datasets_dict = {dataset.name: dataset for dataset in self.datasets}
        algorithms_dict = {algo.name: algo for algo in self.algorithms}

        for dataset_name in data:
            if dataset_name not in datasets_dict.keys():
                continue
            for algo_run in data[dataset_name]:
                self.algo_runs.append(AlgoRun(
                    algo_run_attrs=AlgoRunAttrs(
                        dataset=datasets_dict[dataset_name],
                        algo=algorithms_dict[algo_run["algo_name"]],
                        params=algo_run["params"],
                        scores=list([scores_dict[score_name] for score_name in algo_run["calculated_scores"].keys()])
                    ),
                    results=algo_run["results"],
                    calculated_scores=algo_run["calculated_scores"]
                ))

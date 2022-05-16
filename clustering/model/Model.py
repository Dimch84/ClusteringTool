import numpy as np
import uuid
from dataclasses import dataclass

from PyQt5.QtCore import QSettings

from clustering.model.Algorithm import Algorithm
from clustering.model.Dataset import Dataset
from clustering.model.Score import Score


@dataclass
class AlgoConfig:
    name: str
    algo_id: uuid
    params: dict


@dataclass()
class AlgoRunConfig:
    algo_config: AlgoConfig
    dataset_id: uuid
    score_ids: list[uuid]


@dataclass()
class AlgoRunResults:
    config: AlgoRunConfig
    pred: np.ndarray
    scores: dict
    dataset: uuid


class Model:
    def __init__(self, datasets: list[Dataset], algorithms: list[Algorithm], scores: list[Score], compare_mode: bool = False):
        self.datasets: dict[uuid, Dataset] = {
            uuid.uuid4(): dataset for dataset in datasets
        }
        self.algorithms: dict[uuid, Algorithm] = {
            uuid.uuid4(): algorithm for algorithm in algorithms
        }
        self.scores: dict[uuid, Score] = {
            uuid.uuid4(): score for score in scores
        }
        self.algo_run_results: dict[uuid, AlgoRunResults] = {}
        self.compare_mode = compare_mode

    def add_algo_run(self, config: AlgoRunConfig) -> uuid:
        dataset = self.datasets[config.dataset_id]
        algorithm = self.algorithms[config.algo_config.algo_id]
        pred = algorithm.run(dataset.data, config.algo_config.params)
        scores = self.calc_scores(pred, dataset, [self.scores[score_id] for score_id in config.score_ids])
        algo_run_result_id = uuid.uuid4()
        algo_run_result = AlgoRunResults(config, pred, scores, dataset)
        self.algo_run_results[algo_run_result_id] = algo_run_result
        return algo_run_result_id

    @staticmethod
    def calc_scores(pred: np.ndarray, dataset: [Dataset], scores: [Score]):
        result = {}
        for score in scores:
            result.update({score.name: score.calc_score(
                data=dataset.data,
                target=dataset.target,
                pred=pred
            )})
        return result

    def remove_algo_run_results(self, algo_run_results_id: uuid):
        self.algo_run_results.pop(algo_run_results_id, None)
        # TODO check if item was removed
        return True

    def add_dataset(self, dataset: Dataset):
        dataset_id = uuid.uuid4()
        self.datasets[dataset_id] = dataset
        # TODO check if item was added
        return dataset_id

    def add_algorithm(self, algorithm: Algorithm):
        algorithm_id = uuid.uuid4()
        self.algorithms[algorithm_id] = algorithm
        # TODO check if item was added
        return algorithm_id

    def save(self, file="__last_run.ini"):
        session = QSettings(file, QSettings.IniFormat)
        data = {}

        for algo_run_id in self.algo_run_results.keys():
            algo_run = self.algo_run_results[algo_run_id]
            algo_name = self.algorithms[algo_run.config.algo_config.algo_id].name
            dataset_name = self.datasets[algo_run.config.dataset_id].name
            if dataset_name not in data.keys():
                data[dataset_name] = []
            data[dataset_name].append({
                "run_name": algo_run.config.algo_config.name,
                "algo_name": algo_name,
                "params": algo_run.config.algo_config.params,
                "scores": algo_run.scores,
                "pred": algo_run.pred
            })
        session.setValue("data", data)
        session.sync()

    def load(self, file="__last_run.ini"):
        session = QSettings(file, QSettings.IniFormat)
        data = session.value("data")
        if data is None:
            return

        algorithms_dict = {self.algorithms[algo_id].name: algo_id for algo_id in self.algorithms.keys()}
        datasets_dict = {self.datasets[dataset_id].name: dataset_id for dataset_id in self.datasets.keys()}
        scores_dict = {self.scores[score_id].name: score_id for score_id in self.scores.keys()}

        for dataset_name in data:
            if dataset_name not in datasets_dict.keys():
                continue
            for algo_run in data[dataset_name]:
                algo_run_result_id = uuid.uuid4()
                self.algo_run_results[algo_run_result_id] = AlgoRunResults(
                    config=AlgoRunConfig(
                        AlgoConfig(
                            name=algo_run["run_name"],
                            algo_id=algorithms_dict[algo_run["algo_name"]],
                            params=algo_run["params"]
                        ),
                        dataset_id=datasets_dict[dataset_name],
                        score_ids=list([scores_dict[score_name] for score_name in algo_run["scores"].keys()])
                    ),
                    pred=algo_run["pred"],
                    scores=algo_run["scores"],
                    dataset=datasets_dict[dataset_name]
                )

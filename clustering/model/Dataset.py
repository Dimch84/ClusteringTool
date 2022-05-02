from sklearn import preprocessing
import numpy as np
import pandas
import os
import json


class Dataset:
    """
    This class is used to represent an instance of clustering problem

    Attributes:
        data: 2d-array of float with shape (n_samples, n_features),where n_samples is number of elements, and n_features is number of features.
        target: expected partition into clusters (could be None)
        num_of_classes: number of clusters to which data should be divided
        feature_names: array with title for each feature
        name: title for the dataset
    """
    data: np.ndarray
    target: np.ndarray
    num_of_classes: int
    feature_names: [str]
    name: str

    def __init__(self, data: np.ndarray, num_of_classes: int = None,
                 target: np.ndarray = None, feature_names: [str] = None, name: str = "Unnamed"):
        """
        When function is called, at least one of (num_of_classes, target) should be specified (preferably, exactly one).
        """
        self.data = data
        self.target = target
        self.num_of_classes = num_of_classes
        self.name = name

        if target is not None:
            self.num_of_classes = len(set(target))

        if feature_names is None:
            feature_names = np.array([f"Feature {i}" for i in range(1, data.shape[1] + 1)])
        self.feature_names = feature_names

    def __str__(self):
        return f"data = {self.data}\nfeature_names = {self.feature_names}\n" \
               f"target = {self.target}\nnum_of_classes = {self.num_of_classes},\nname = {self.name}"


class DuplicatedDatasetNameError(Exception):
    pass


_json_file = os.path.join('datasets', 'datasets.json')


def _dataset_filename(name: str) -> str:
    return os.path.join('datasets', name + '.csv')


def normalise_dataset(data: np.ndarray) -> np.ndarray:
    return preprocessing.MinMaxScaler().fit_transform(data)


def load_from_csv(file_name: str) -> pandas.DataFrame:
    """
    Reads dataset from csv file and returns it with all numeric features
    """
    df = pandas.read_csv(file_name)
    groups = df.columns.to_series().groupby(df.dtypes).groups
    groups = {str(k): list(v) for k, v in groups.items()}
    numeric_cols = groups.get('int64', []) + groups.get('float64', [])
    return df[numeric_cols]


def _save_to_csv(data: Dataset, file_name: str = None):
    if file_name is None:
        file_name = _dataset_filename(data.name)
    df = pandas.DataFrame(data=data.data, columns=data.feature_names)
    df.to_csv(file_name, index=False)


def _serialize_dataset(dataset: Dataset) -> dict:
    return {
        'name': dataset.name,
        'num_of_classes': dataset.num_of_classes,
        'target': None if dataset.target is None else list(map(int, dataset.target))
    }


def _deserialize_dataset(dataset: dict) -> Dataset:
    name = dataset['name']
    num_of_classes = dataset['num_of_classes']
    target = None if dataset['target'] is None else np.array(dataset['target'])
    df = load_from_csv(_dataset_filename(name))
    data = df.to_numpy()
    return Dataset(data, num_of_classes=num_of_classes, target=target, feature_names=df.columns.tolist(), name=name)


def _write_to_json(datasets: [dict]):
    with open(_json_file, 'w') as json_file:
        json.dump(datasets, json_file)


def _read_from_json() -> [dict]:
    with open(_json_file, 'r') as json_file:
        return json.load(json_file)


def add_dataset(dataset: Dataset):
    """
    The function creates a csv-file with dataset and record in json, so that this dataset will be included in
    `load_all_datasets()` during the next launch.
    Should be called each time you want a dataset to be saved
    """
    _save_to_csv(dataset)
    dump = _read_from_json()
    if dump is None:
        dump = []
    if dataset.name in [d['name'] for d in dump]:
        raise DuplicatedDatasetNameError()
    dump.append(_serialize_dataset(dataset))
    _write_to_json(dump)


def delete_dataset(name: str):
    """
    This function deletes dataset with specified name, so that it will not appear in `load_all_datasets()`
    during next launch.
    """
    dump = _read_from_json()
    if os.path.exists(_dataset_filename(name)):
        os.remove(_dataset_filename(name))
    dump = list(filter(lambda d: d['name'] != name, dump))
    _write_to_json(dump)


def load_all_datasets() -> [Dataset]:
    """
    :return: list of all datasets, information about which is stored in json and corresponding csv-files.
    """
    result = []
    for dataset in _read_from_json():
        try:
            result.append(_deserialize_dataset(dataset))
        except FileNotFoundError:
            delete_dataset(dataset['name'])
    return result
import numpy as np
from sklearn import preprocessing
import pandas
import os


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
    feature_names: np.ndarray
    name: str

    def __init__(self, data: np.ndarray, num_of_classes: int = None,
                 target: np.ndarray = None, feature_names: np.ndarray = None, name: str = "Unnamed"):
        """
        When function is called, at least one of (num_of_classes, target) should be specified (preferably, exactly one).
        """
        self.data = data
        self.target = target
        self.num_of_classes = num_of_classes
        self.name = name

        if (target is None) and (num_of_classes is None):
            raise Exception("Either num_of_classes or target should be specified")

        if target is not None:
            self.num_of_classes = len(set(target))

        if feature_names is None:
            feature_names = np.ndarray([f"Feature {i}" for i in range(1, data.shape[1] + 1)])
        self.feature_names = feature_names

    def __str__(self):
        return f"data = {self.data}\nfeature_names = {self.feature_names}\n" \
               f"target = {self.target}\nnum_of_classes = {self.num_of_classes},\nname = {self.name}"


def load_from_csv(file_name: str, num_of_classes: int = None, target: np.ndarray = None, normalise: bool = False) -> Dataset:
    """
    Reads data from csv file. At least one of (target, num_of_classes) should be specified explicitly.

    If normalise is set to True, for each feature values will be scaled to fit in [0, 1]
    """
    df = pandas.read_csv(file_name)
    groups = df.columns.to_series().groupby(df.dtypes).groups
    groups = {str(k): list(v) for k, v in groups.items()}
    numeric_cols = groups.get('int64', []) + groups.get('float64', [])

    data = df[numeric_cols].to_numpy()
    if normalise:
        data = preprocessing.MinMaxScaler().fit_transform(data)

    return Dataset(data, num_of_classes=num_of_classes, target=target, feature_names=numeric_cols,
                   name=os.path.splitext(os.path.basename(file_name))[0])


def save_to_csv(file_name: str, data: Dataset):
    df = pandas.DataFrame(data=data.data, columns=data.feature_names)
    df.to_csv(file_name, index=False)

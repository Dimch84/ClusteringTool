import numpy as np
from sklearn import preprocessing
import pandas
import os


class Dataset:
    data: np.array
    target: np.array
    num_of_classes: int
    feature_names: np.array
    name: str

    def __init__(self, data: np.array, num_of_classes: int = None,
                 target: np.array = None, feature_names: np.array = None, name: str = "Unnamed"):
        self.data = data
        self.target = target
        self.num_of_classes = num_of_classes
        self.name = name

        if (target is None) and (num_of_classes is None):
            raise Exception("Either num_of_classes or target should be specified")

        if target is not None:
            self.num_of_classes = len(set(target))

        if feature_names is None:
            feature_names = np.array([f"Feature {i}" for i in range(1, data.shape[1] + 1)])
        self.feature_names = feature_names

    def __str__(self):
        return f"data = {self.data}\nfeature_names = {self.feature_names}\n" \
               f"target = {self.target}\nnum_of_classes = {self.num_of_classes},\nname = {self.name}"


def load_from_csv(file_name: str, num_of_classes: int, normalise: bool = False) -> Dataset:
    df = pandas.read_csv(file_name)
    groups = df.columns.to_series().groupby(df.dtypes).groups
    groups = {str(k): list(v) for k, v in groups.items()}
    numeric_cols = groups.get('int64', []) + groups.get('float64', [])

    data = df[numeric_cols].to_numpy()
    if normalise:
        data = preprocessing.MinMaxScaler().fit_transform(data)

    return Dataset(data, feature_names=numeric_cols, num_of_classes=num_of_classes,
                   name=os.path.splitext(os.path.basename(file_name))[0])


def save_to_csv(file_name: str, data: Dataset):
    df = pandas.DataFrame(data=data.data, columns=data.feature_names)
    df.to_csv(file_name, index=False)

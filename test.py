from sklearn.datasets import *
from matplotlib import use
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn import preprocessing
import pandas


class Dataset:
    data: np.array
    feature_names: np.array
    target: np.array
    num_of_classes: int

    def __init__(self, data: np.array, num_of_classes: int = None, target: np.array = None, feature_names: np.array = None):
        self.data = data
        self.target = target
        self.num_of_classes = num_of_classes

        if target is not None:
            self.num_of_classes = len(set(target))

        if feature_names is None:
            feature_names = np.empty(data.shape[1], dtype=object)
            for i in range(0, data.shape[1]):
                feature_names[i] = f"Feature {i+1}"
        self.feature_names = feature_names

    def __str__(self):
        return f"data = {self.data}\n feature_names = {self.feature_names}\n target = {self.target}\n num_of_classes = {self.num_of_classes}"


def load_from_csv(file_name: str, num_of_classes: int, normalise: bool = False) -> Dataset:
    # TODO: ignore features with non-real values
    df = pandas.read_csv(file_name)
    data = df.to_numpy()
    if normalise:
        data = preprocessing.MinMaxScaler().fit_transform(data)
    return Dataset(data, feature_names=df.columns, num_of_classes=num_of_classes)


def save_to_csv(file_name: str, data: Dataset) -> None:
    df = pandas.DataFrame(data=data.data, columns=data.feature_names)
    df.to_csv(file_name, index=False)


def data_converse(data: np.array) -> np.array:
    if data.shape[1] == 2:
        return data
    return PCA(n_components=2).fit_transform(data)


def main():
    use('TkAgg')
    data1, ans1 = make_blobs(n_samples=200, centers=7, n_features=8, cluster_std=0.1, random_state=0)
    data2, ans2 = make_blobs(n_samples=200, centers=5, n_features=2, cluster_std=0.7, random_state=0)
    data3, ans3 = make_circles(n_samples=200, factor=0.5, noise=0.05)
    data4, ans4 = make_moons(n_samples=200, noise=0.1)
    iris = load_iris()
    data5, ans5 = (iris.data, iris.target)
    data6 = load_from_csv('data/generated-data.csv', 7, normalise=True)

    data = [Dataset(data1, ans1), Dataset(data2, ans2), Dataset(data3, ans3),
            Dataset(data4, ans4), Dataset(data5, ans5), data6]

    plt.figure(figsize=(2, 3))

    for i in range(len(data)):
        plt.subplot(2, 3, i + 1)
        d = data_converse(data[i].data)
        plt.scatter(
            d[:, 0],
            d[:, 1],
        )
        plt.axis('scaled')

    plt.show()

    save_to_csv('data/generated-data.csv', data[0])


if __name__ == "__main__":
    main()

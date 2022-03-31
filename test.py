from sklearn.datasets import *
from matplotlib import use
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA


def data_converse(data: np.array) -> np.array:
    if data.shape[1] == 2:
        return data
    return PCA(n_components=2).fit_transform(data)


def main():
    use('TkAgg')
    data1, _ = make_blobs(n_samples=200, centers=7, n_features=8, cluster_std = 0.1, random_state=0)
    data2, _ = make_blobs(n_samples=200, centers=5, n_features=2, cluster_std = 0.7, random_state=0)
    data3, _ = make_circles(n_samples=200, factor=0.5, noise=0.05)
    data4, _ = make_moons(n_samples=200, noise=0.1)
    data5, _, _ = make_checkerboard(shape=(200, 2), n_clusters=8, noise=1, shuffle=False, random_state=0)
    data6 = load_iris().data

    data = [data1, data2, data3, data4, data5, data6]

    plt.figure(figsize=(2, 3))

    for i in range(len(data)):
        d = data_converse(data[i])
        plt.subplot(2, 3, i + 1)
        plt.scatter(
            d[:,0],
            d[:,1],
        )
        plt.axis('scaled')

    plt.title("Title")
    plt.show()

if __name__ == "__main__":
    main()
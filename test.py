from sklearn.datasets import *
from matplotlib import use
import matplotlib.pyplot as plt

use('TkAgg')
data1, _ = make_blobs(n_samples=200, centers=7, n_features=2, cluster_std = 0.1, random_state=0)
data2, _ = make_blobs(n_samples=200, centers=5, n_features=2, cluster_std = 0.7, random_state=0)
data3, _ = make_circles(n_samples=200, factor=0.5, noise=0.05)
data4, _ = make_moons(n_samples=200, noise=0.1)
data5, _, _ = make_checkerboard(shape=(200, 2), n_clusters=8, noise=1, shuffle=False, random_state=0)

data = [data1, data2, data3, data4, data5]

plt.figure(figsize=(1, 5))

for i in range(len(data)):
    d = data[i]
    plt.subplot(1, 5, i + 1)
    plt.scatter(
        d[:,0],
        d[:,1],
    )
    plt.axis('scaled')

plt.title("Title")
plt.show()

"""centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(
    n_samples=750, centers=centers, cluster_std=0.4, random_state=0
)"""

"""kmeans = KMeans(eps = 0.2, metric="euclidean").fit(X)
print(type(kmeans))
print(kmeans.labels_)
labels = kmeans.labels_"""
#X = np.array([[1, 1], [1, 4], [1, 2],
#[-3, -3], [-3, -4], [-3, -2]])

import sklearn.cluster as algos

from clustering.algorithm import Algorithm

kmeans = Algorithm("K-means", lambda data, k: algos.KMeans(n_clusters=k).fit(data).labels_)
agglo = Algorithm("Agglomerative clustering", lambda data, k: algos.
                  AgglomerativeClustering(n_clusters=k, affinity='euclidean', linkage='ward').fit(data).labels_)
# TODO: add other algorithms from sklearn

algorithms = [kmeans, agglo]

import sklearn.cluster as algos
from clustering.metrics import metrics
from clustering.algorithm import Algorithm
import sklearn.metrics.pairwise as sm
import numpy as np

kmeans = Algorithm(name="K-means",
                   extra_params={},
                   run=lambda data, params:
                   algos.KMeans(
                       n_clusters=params["k"])
                   .fit(data).labels_)
agglo = Algorithm(name="Agglomerative clustering",
                  extra_params={"affinity": ["euclidean", "l1", "l2", "manhattan", "cosine"],
                                "linkage": ["ward", "complete", "average", "single"]},
                  run=lambda data, params:
                  algos.AgglomerativeClustering(
                      n_clusters=params["k"],
                      affinity=params["affinity"],
                      linkage=params["linkage"]
                  ).fit(data).labels_)
# TODO: add other algorithms from sklearn

algorithms = [kmeans, agglo]

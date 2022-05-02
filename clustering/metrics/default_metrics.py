import sklearn.metrics as sm

from clustering.model.Metric import Metric


metrics = [
    Metric("Euclidean", sm._dist_metrics.EuclideanDistance),
    Metric("Manhattan", sm._dist_metrics.ManhattanDistance),
    Metric("Hamming", sm._dist_metrics.HammingDistance),
    Metric("Jaccard", sm._dist_metrics.JaccardDistance),
    Metric("Minkowski", sm._dist_metrics.MinkowskiDistance)
]

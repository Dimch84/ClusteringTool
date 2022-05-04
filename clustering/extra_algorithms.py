import sklearn.cluster as algos
from clustering.model.Algorithm import Algorithm

from clustering.model.Algorithm import AlgoParams
from clustering.model.Algorithm import IntParam
from clustering.model.Algorithm import SelectableParam

kmeans = Algorithm(name="K-mean",
                   params=AlgoParams(
                       int_params=[IntParam(name="k", min_bound=2, max_bound=20)],
                       selectable_params=[]
                   ),
                   run=lambda data, params:
                   algos.KMeans(
                       n_clusters=params["k"])
                   .fit(data).labels_)

agglo = Algorithm(name="Agglomerative clusterin",
                  params=AlgoParams(
                      int_params=[IntParam(name="k", min_bound=2, max_bound=20)],
                      selectable_params=[
                          SelectableParam(name="affinity", items=["euclidean", "l1", "l2", "manhattan", "cosine"]),
                          SelectableParam(name="linkage", items=["ward", "complete", "average", "single"])
                      ]
                  ),
                  run=lambda data, params:
                    algos.AgglomerativeClustering(
                        n_clusters=params["k"],
                        affinity=params["affinity"],
                        linkage=params["linkage"])
                  .fit(data).labels_)

# TODO: add other algorithms from sklearn
algorithms = [kmeans, agglo]

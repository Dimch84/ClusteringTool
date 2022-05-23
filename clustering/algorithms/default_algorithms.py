import sklearn.cluster as sk

from clustering.model.Algorithm import Algorithm
from clustering.model.Algorithm import AlgoParams
from clustering.model.Algorithm import SelectableParam

k_means = Algorithm(name="K-means",
                    params=AlgoParams(
                        bool_params=[],
                        float_params=["tol"],
                        int_params=["n_clusters", "n_init", "max_iter", "verbose"],
                        selectable_params=[SelectableParam(name="algorithm",
                                                           items=["elkan", "auto", "full"])]
                    ),
                    run=lambda data, params:
                    sk.KMeans(**params)
                    .fit(data).labels_)

agglomerative = Algorithm(name="Agglomerative clustering",
                          params=AlgoParams(
                              bool_params=["compute_full_tree"],
                              float_params=["distance_threshold"],
                              int_params=["n_clusters"],
                              selectable_params=[
                                  SelectableParam(name="affinity",
                                                  items=["euclidean", "l1", "l2", "manhattan", "cosine"]),
                                  SelectableParam(name="linkage",
                                                  items=["ward", "complete", "average", "single"])
                              ]
                          ),
                          run=lambda data, params:
                          sk.AgglomerativeClustering(**params)
                          .fit(data).labels_)

dbscan = Algorithm(name="DBSCAN",
                   params=AlgoParams(
                       bool_params=[],
                       float_params=["eps", "p"],
                       int_params=["min_samples", "leaf_size", "n_jobs"],
                       selectable_params=[
                           SelectableParam(name="metric",
                                           items=["euclidean", "l1", "l2", "manhattan", "cosine"]),
                           SelectableParam(name="algorithm",
                                           items=["auto", "ball_tree", "kd_tree", "brute"])]
                   ),
                   run=lambda data, params:
                   sk.DBSCAN(**params)
                   .fit(data).labels_)

birch = Algorithm(name="BIRCH",
                  params=AlgoParams(
                       bool_params=[],
                       float_params=["threshold"],
                       int_params=["n_clusters", "branching_factor"],
                       selectable_params=[]
                  ),
                   run=lambda data, params:
                   sk.Birch(**params)
                   .fit(data).labels_)

affinity = Algorithm(name="Affinity propagation",
                  params=AlgoParams(
                       bool_params=[],
                       float_params=["damping"],
                       int_params=["max_iter", "convergence_iter", "random_state"],
                       selectable_params=[SelectableParam(name="affinity",
                                                         items=["euclidean", "precomputed"]) ]
                   ),
                   run=lambda data, params:
                   sk.AffinityPropagation(**params)
                   .fit(data).labels_)

algorithms = [k_means, agglomerative, dbscan, birch, affinity]

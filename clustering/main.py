import dataset
import algorithm


data = dataset.load_all_datasets()[1]
algos = algorithm.load_algorithms()
for algo in algos:
    print(algo.run(data.data, data.num_of_classes))
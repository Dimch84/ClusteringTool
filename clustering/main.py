import dataset
import algorithm


data = dataset.load_from_csv('datasets/healthy_lifestyle_city_2021.csv', 8, normalise=True)
algorithm.load_algorithms()
algos = algorithm.load_algorithms()
for algo in algos:
    print(algo.run(data.data, data.num_of_classes))

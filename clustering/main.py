import dataset
import algorithm


#data = dataset.load_from_csv('datasets/healthy_lifestyle_city_2021.csv', 8, normalise=True)
data = dataset.load_from_json('datasets/datasets.json')[0]
algos = algorithm.load_algorithms()
for algo in algos:
    print(algo.run(data.data, data.num_of_classes))

dataset.save_to_csv('datasets/' + data.name + '.csv', data)
dataset.save_to_json('datasets/datasets.json', [data])
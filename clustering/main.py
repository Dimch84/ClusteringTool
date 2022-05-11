from PyQt5.QtWidgets import QApplication
import sys

from clustering.model.Algorithm import load_algorithms
from clustering.model.Dataset import load_all_datasets
from clustering.model.Model import Model
from clustering.view.View import View
from clustering.presenter.Presenter import Presenter
from clustering.scores.default_scores import scores

app = QApplication(sys.argv)

all_saved_algo_names = [algo.name for algo in load_algorithms()]
if len(all_saved_algo_names) > len(set(all_saved_algo_names)):
    print("Algorithms in clustering/algorithms are not distinct")
    raise Exception
all_saved_dataset_names = [dataset.name for dataset in load_all_datasets()]
if len(all_saved_dataset_names) > len(set(all_saved_dataset_names)):
    print("Datasets in clustering/datasets are not distinct")
    raise Exception

presenter = Presenter()
model = Model(
    datasets=load_all_datasets(),
    algorithms=load_algorithms(),
    scores=scores
)
model.load()
presenter.set_model(model)

view = View(presenter, True)
presenter.set_view(view)

view.load_from_model(presenter.model)
view.show()
sys.exit(app.exec())

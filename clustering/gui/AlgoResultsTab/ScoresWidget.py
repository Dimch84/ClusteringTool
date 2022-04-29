from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout
import numpy as np

from clustering.scores import scores


class ScoresWidget(QWidget):
    def __init__(self, data: np.ndarray, score_names: set[str], target: np.ndarray, pred: np.ndarray):
        super().__init__()
        self.setMinimumSize(400, 300)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)
        scores_dict = {score.name: score for score in scores}

        if data is not None:
            for score_name in filter(lambda m: not scores_dict[m].needs_target, score_names):
                score = scores_dict[score_name]
                layout.addRow(QLabel(score_name), QLabel(str(score.calc_score(data=data, pred=pred))))

        if target is not None:
            for score_name in filter(lambda m: scores_dict[m].needs_target, score_names):
                score = scores_dict[score_name]
                layout.addRow(QLabel(score_name), QLabel(str(score.calc_score(target=target, pred=pred))))
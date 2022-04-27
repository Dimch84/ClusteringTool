import random
import numpy as np
from PyQt5.QtCore import Qt, QPointF, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QSizePolicy
from PyQt5.QtGui import QTransform
from sklearn.decomposition import PCA


class ScalableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.zoom = 1

    def wheelEvent(self, event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        if event.angleDelta().y() > 0:
            self.zoom = min(5.0, self.zoom * 1.12)
        else:
            self.zoom = max(0.2, self.zoom / 1.12)
        self.__update_view()

    def __update_view(self):
        self.setTransform(QTransform().scale(self.zoom, self.zoom))


class ClusteringView(QWidget):
    zoom_signal = pyqtSignal(bool)

    def __init__(self, points: np.ndarray, pred: list[int]):
        super().__init__()
        scene = QGraphicsScene()
        if points.shape[1] != 2:
            points = PCA(n_components=2).fit_transform(points)
        self.points = list(map(lambda point: QPointF(point[0], point[1]), points))
        self.pred = pred
        self.graphicView = ScalableGraphicsView(scene, self)
        self.graphicView.setMinimumSize(800, 600)
        self.colors = dict((x, QColor(random.randint(1, 1000000000))) for x in list(set(pred)))
        self.graphicView.setScene(self.__get_scene_with_points())

    def __get_scene_with_points(self):
        scene = QGraphicsScene()
        points = self.__resize_points()
        for idx, point in enumerate(points):
            scene.addEllipse(point.x(), point.y(), 10, 10,
                             QPen(self.colors[self.pred[idx]], 3, Qt.SolidLine),
                             QBrush(self.colors[self.pred[idx]])).setFlag(QGraphicsItem.ItemIsSelectable)
        return scene

    def __resize_points(self):
        minW = min(x.x() for x in self.points)
        maxW = max(x.x() for x in self.points)
        minH = min(x.y() for x in self.points)
        maxH = max(x.y() for x in self.points)
        width = self.graphicView.width()
        height = self.graphicView.height()
        k = min(width / (maxW - minW), height / (maxH - minH))
        return (QPointF(k * (x.x() - minW), k * (x.y() - minH)) for x in self.points)

    def setGeometry(self, a0: QRect):
        super().setGeometry(a0)
        self.graphicView.setGeometry(0, 0, a0.width(), a0.height())
        self.graphicView.setScene(self.__get_scene_with_points())
import cmapy
import random
import uuid

import numpy as np
from PyQt5.QtCore import Qt, QPointF, QRect
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QSizePolicy, QGraphicsEllipseItem, \
    QGraphicsTextItem
from PyQt5.QtGui import QTransform
from sklearn.decomposition import PCA

from clustering.presenter.Presenter import Presenter


class ScalableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.zoom = 1
        self.info = self.hint_bg = None

    def wheelEvent(self, event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        if event.angleDelta().y() > 0:
            self.zoom = min(5.0, self.zoom * 1.12)
        else:
            self.zoom = max(0.2, self.zoom / 1.12)
        self.__update_view()

    def __update_view(self):
        self.setTransform(QTransform().scale(self.zoom, self.zoom))

    def __reset_info(self):
        if self.info is not None:
            self.scene().removeItem(self.info)
            self.scene().removeItem(self.hint_bg)
        self.info = self.hint_bg = None

    def add_info(self, text: str, x: float, y: float):
        self.__reset_info()
        self.info = QGraphicsTextItem(text)
        self.info.setPos(x, y)
        rect = self.info.boundingRect()
        rect.moveTo(x, y)
        self.hint_bg = self.scene().addRect(rect, brush=QBrush(QColor("lightGray")))
        self.scene().addItem(self.info)

    def mousePressEvent(self, event) -> None:
        self.__reset_info()
        super().mousePressEvent(event)


class EllipseWithInfo(QGraphicsEllipseItem):
    def __init__(self, view: ScalableGraphicsView, x: float, y: float, w: float, h: float, pen: QPen, brush: QBrush, info: str):
        super().__init__(x, y, w, h)
        self.ax = x
        self.ay = y
        self.view = view
        self.setPen(pen)
        self.setBrush(brush)
        self.info = info

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.view.add_info(self.info, self.ax + 10, self.ay + 10)


class ClusteringView(QWidget):
    def __init__(self, points: np.ndarray, pred: np.ndarray, presenter: Presenter, dataset_id: uuid):
        super().__init__()
        scene = QGraphicsScene()
        if points.shape[1] != 2:
            points = PCA(n_components=2).fit_transform(points)
        self.points = list(map(lambda point: QPointF(point[0], point[1]), points))
        self.presenter = presenter
        self.dataset_id = dataset_id
        self.pred = pred
        self.graphicView = ScalableGraphicsView(scene, self)
        self.setMinimumSize(800, 600)
        self.graphicView.setMinimumSize(800, 600)
        self.colors = {x: QColor(*cmapy.color('hsv', random.randrange(0, 256), rgb_order=True)) for x in set(pred)}

        self.graphicView.setScene(self.get_scene_with_points())

    def get_scene_with_points(self):
        scene = QGraphicsScene()
        points = self.resize_points()
        for idx, point in enumerate(points):
            ellipse = EllipseWithInfo(self.graphicView, point.x(), point.y(), 10, 10,
                                      QPen(self.colors[self.pred[idx]], 3, Qt.SolidLine),
                                      QBrush(self.colors[self.pred[idx]]), self.get_point_info(idx))
            ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            scene.addItem(ellipse)

        rect = scene.sceneRect()
        width = self.graphicView.width()
        height = self.graphicView.height()
        rect.adjust(-1.5 * width, -1.5 * height, 1.5 * width, 1.5 * height)
        scene.setSceneRect(rect)
        return scene

    def get_point_info(self, idx: int) -> str:
        info = self.presenter.get_dataset_titles(self.dataset_id)[idx] + "\n\n"
        feature_names = self.presenter.get_dataset_feature_names(self.dataset_id)
        data = self.presenter.get_dataset_points(self.dataset_id)
        for feature_id in range(len(feature_names)):
            info += f"{feature_names[feature_id]} = {data[idx][feature_id]}\n"
        return info

    def resize_points(self):
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

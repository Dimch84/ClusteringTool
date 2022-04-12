import random
from PyQt5.QtCore import Qt, QPointF, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem, QSizePolicy
from PyQt5.QtGui import QTransform


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
        self.updateView()

    def updateView(self):
        self.setTransform(QTransform().scale(self.zoom, self.zoom))


class ClusteringView(QWidget):
    zoom_signal = pyqtSignal(bool)

    def __init__(self, points: list[QPointF], target: list[int]):
        super().__init__()
        scene = QGraphicsScene()
        self.points = points
        self.target = target
        self.graphicView = ScalableGraphicsView(scene, self)
        self.graphicView.setMinimumSize(800, 600)
        self.colors = dict((x, QColor(random.randint(1, 1000000000))) for x in list(set(target)))
        self.graphicView.setScene(self.__getSceneWithPoints())
        self.show()

    def __getSceneWithPoints(self):
        scene = QGraphicsScene()
        points = self.__resizePoints()
        for idx, point in enumerate(points):
            scene.addEllipse(point.x(), point.y(), 10, 10,
                             QPen(self.colors[self.target[idx]], 3, Qt.SolidLine),
                             QBrush(self.colors[self.target[idx]])).setFlag(QGraphicsItem.ItemIsSelectable)
        return scene

    def __resizePoints(self):
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
        self.graphicView.setScene(self.__getSceneWithPoints())
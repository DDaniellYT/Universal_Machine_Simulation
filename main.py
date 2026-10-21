import sys

import trimesh
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QSplitter, QWidget
from pyqtgraph.opengl import *


def main():
    app = QApplication(sys.argv)

    mesh = trimesh.load("./Simulation_STL/Head_Simulation.STL")

    left = QWidget()    # controls will go here
    right = GLViewWidget()   # 3D view will go here
    right.setCameraPosition(distance=500, elevation=30, azimuth=45)

    grid = GLGridItem()
    grid.setSize(300, 300)  # 300 x 300 mm floor
    grid.setSpacing(10, 10)  # a line every 10 mm
    right.addItem(grid)

    axes = GLAxisItem()
    axes.setSize(100, 100, 100)  # 100 mm arrows: X red, Y green, Z blue
    right.addItem(axes)

    item = GLMeshItem(
        vertexes=mesh.vertices,  # N x 3 array of points
        faces=mesh.faces,  # M x 3 array of vertex indexes
        color=(0.7, 0.7, 0.8, 1),
        smooth=False,
        drawEdges=False,
    )
    right.addItem(item)





    split = QSplitter(Qt.Orientation.Horizontal)
    split.addWidget(left)
    split.addWidget(right)
    split.setSizes([500, 500])   # equal halves to start; the user can drag the divider

    split.setWindowTitle("Machine")
    split.resize(1000, 600)
    split.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
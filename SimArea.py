from PyQt6.QtCore import QTimer
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np

class SimArea(QtInteractor):

    head = ...

    def __init__(self):
        super().__init__()

        self.set_background("white")
        self.show_grid()
        self.add_axes()

        volume = pv.Box(bounds=(0, 300, 0, 300, 0, 300))  # build volume, in mm
        self.add_mesh(volume, style="wireframe", color="gray")

        self.seg = []  # flat list: start, end, start, end, ...
        self.last = None  # the previous head position
        self.dirty = False
        self.redraw_timer = QTimer(self)
        self.redraw_timer.setInterval(50)  # redraw the path at most 20 times a second
        self.redraw_timer.timeout.connect(self.redraw_path)
        self.redraw_timer.start()

    def add_head(self,head):
        xmin, xmax, ymin, ymax, zmin, zmax = head.bounds
        head.translate((-(xmin + xmax) / 2, -(ymin + ymax) / 2, -zmin), inplace=True)
        self.head = self.add_mesh(head)

    def move_head(self,info):
        x, y, z, e = info
        pos = (x, y, z)
        self.head.position = pos
        if self.last is not None and e > 0:  # extruding: add one segment last -> now
            self.seg.append(self.last)
            self.seg.append(pos)
            self.dirty = True
        self.last = pos  # always update, even on travel
        self.render()

    def redraw_path(self):
        if not self.dirty:
            return
        self.dirty = False
        pts = np.array(self.seg, dtype=np.float32)  # shape (2 * nseg, 3)
        nseg = len(pts) // 2
        idx = np.arange(nseg * 2).reshape(nseg, 2)
        lines = np.column_stack([np.full(nseg, 2), idx]).ravel()  # [2,0,1, 2,2,3, ...]
        mesh = pv.PolyData(pts, lines=lines)
        self.add_mesh(mesh, color="red", line_width=3, name="path",
                      reset_camera=False, render=False)
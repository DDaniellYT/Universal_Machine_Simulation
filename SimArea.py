from PyQt6.QtCore import QTimer
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np

class SimArea(QtInteractor):


    def __init__(self):
        super().__init__()

        self.head = None
        self.bed = None

        self.max_z = 300
        self.max_x = 300
        self.max_y = 300
        self.tip_z = 0

        self.path_actor = None
        self.bed_z = 0

        self.beams = []

        self.enable_fly_to_right_click()

        self.set_background("white")
        self.show_grid()
        self.add_axes()

        volume = pv.Box(bounds=(0, self.max_x, 0, self.max_y, 0, self.max_z))  # build volume
        self.add_mesh(volume, style="wireframe", color="gray")

        self.seg = []
        self.last = None
        self.dirty = False
        self.redraw_timer = QTimer(self)
        self.redraw_timer.setInterval(100)  # 50 is 20 times a sec, 100 is 10 times a sec for eff
        self.redraw_timer.timeout.connect(self.redraw_path)
        self.redraw_timer.start()

    def add_head(self,head):
        xmin, xmax, ymin, ymax, zmin, zmax = head.bounds
        head.translate((-(xmin + xmax) / 2, -(ymin + ymax) / 2, self.max_z-zmax), inplace=True)
        self.head = self.add_mesh(head)
        self.tip_z = head.bounds[4]

    def add_beam(self,beam,axis):
        xmin, xmax, ymin, ymax, zmin, zmax = self.head.bounds
        if axis == "x":
            beam.translate((-(xmin + xmax) / 2 - 40/2 ,0, self.max_z-80/2-45/2), inplace=True)
            self.beams.append(self.add_mesh(beam))
        if axis == "y":
            beam.rotate_z(-90,inplace=True)
            beam.translate((0,-(ymin + ymax) / 2 + 40 / 2, self.max_z-80/2-45/2), inplace=True)
            self.beams.append(self.add_mesh(beam))
    def add_bed(self,bed):
        bed.rotate_z(90,inplace=True)
        bed.rotate_y(90,inplace=True)
        bed.translate((0,0,self.max_z - 80 - 11),inplace=True)
        self.bed = self.add_mesh(bed)

    def move_head(self,info):
        x, y, z, e = info
        pos = (x, y, z)

        if z > 300:
            z = 300

        self.head.position = [pos[0],pos[1],0]
        self.beams[0].position = [pos[0],0,0]
        self.beams[1].position = [0,pos[1],0]
        self.bed.position = [0,0,-z]
        self.bed_z = z

        bed_pt = (x, y, self.tip_z + z)

        if self.last is not None and e > 0:
            self.seg.append(self.last)
            self.seg.append(bed_pt)
            self.dirty = True
        self.last = bed_pt

        if self.path_actor is not None:
            self.path_actor.position = (0, 0, -z)
        self.render()

    def redraw_path(self):
        if not self.dirty:
            return
        self.dirty = False
        pts = np.array(self.seg, dtype=np.float32)
        nseg = len(pts) // 2
        idx = np.arange(nseg * 2).reshape(nseg, 2)
        lines = np.column_stack([np.full(nseg, 2), idx]).ravel()
        mesh = pv.PolyData(pts, lines=lines)
        self.path_actor = self.add_mesh(mesh, color="red", line_width=3, name="path",
                                        reset_camera=False, render=False)
        self.path_actor.position = (0, 0, -self.bed_z)
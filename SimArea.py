from pyvistaqt import QtInteractor
import pyvista as pv

class SimArea(QtInteractor):

    head = ...

    def __init__(self):
        super().__init__()

        self.set_background("white")
        self.show_grid()
        self.add_axes()

        head_mesh = pv.read("./Simulation_STL/Head_Simulation.STL")


        volume = pv.Box(bounds=(0, 300, 0, 300, 0, 300))  # build volume, in mm
        self.add_mesh(volume, style="wireframe", color="gray")

    def add_head(self,head):
        self.head = self.add_mesh(head)
    def move_head(self,x,y,z):
        print("got here",x,y,z)
        self.head.position = (x,y,z)
        self.render()


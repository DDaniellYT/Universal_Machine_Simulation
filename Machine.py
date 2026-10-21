import math

import pyvista as pv
from PyQt6.QtCore import pyqtSignal, QObject, QElapsedTimer, QTimer


class Machine(QObject):
    position_changed = pyqtSignal(list)
    move_finished = pyqtSignal()

    speed = 1000

    view_handler = ...
    head_mesh = pv.read("./Simulation_STL/Head_Simulation.STL")

    def stop(self):
        print("stopped")
        self.timer.stop()
        self.target = list(self.pos)

    def _step(self):
        print("stepped")
        dt = self.clock.restart() / 1000.0                        # seconds since last tick
        delta = [t - p for t, p in zip(self.target_queue[0], self.pos)]
        dist = math.sqrt(sum(d * d for d in delta))
        step = self.speed * dt                                    # mm we may travel this tick

        if step >= dist:                                          # close enough: arrive exactly
            self.pos = list(self.target_queue[0])
            self.timer.stop()
            self.position_changed.emit(self.pos)
            del self.target_queue[0]
            self.move_finished.emit()
            print("finished timerd")

            if len(self.target_queue) > 0:
                print("started timer after end")
                self.clock.start()
                self.timer.start()
            else:
                self.target = list(self.pos)
        else:                                                     # move toward the target
            self.pos = [p + d / dist * step for p, d in zip(self.pos, delta)]
            self.position_changed.emit(self.pos)

    def jog(self, axis, step):  # key presses connect here
        t = list(self.target)
        t["XYZ".index(axis)] += step  # add to the TARGET, not the current position
        self.move_to(t)

    def home_axis(self, axis):  # axis reset
        t = list(self.target)
        print(axis)
        t["XYZ".index(axis)] = 0.0
        print("hit reset in home_axis func")
        print(t)
        self.move_to(t)

    def move_to(self,info):
        new_target = info
        self.target_queue.append(new_target)
        self.target = list(new_target)
        if not self.timer.isActive():
            print("started timer first")
            self.clock.start()
            self.timer.start()
        print("emmit move to", self.target_queue[0], len(self.target_queue))


    def __init__(self):
        self.clock = QElapsedTimer()
        self.timer = QTimer()

        self.target_queue = []
        self.target = [0, 0, 0]
        self.pos = [0, 0, 0]

        self.timer.setInterval(16)  # about 60 updates a second
        self.timer.timeout.connect(self._step)
        super().__init__()
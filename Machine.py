import math

import pyvista as pv
from PyQt6.QtCore import pyqtSignal, QObject, QElapsedTimer, QTimer


class Machine(QObject):
    position_changed = pyqtSignal(list)
    move_finished = pyqtSignal()


    def stop(self):
        print("stopped")
        self.timer.stop()
        self.target = list(self.pos)

    def _step(self):
        dt = self.clock.restart() / 1000.0                        # seconds since last tick
        delta = [t - p for t, p in zip(self.target_queue[0], self.pos)]
        dist = math.sqrt(sum(d * d for d in delta))
        step = self.pos[4] * dt                                   # mm we may travel this tick

        if step >= dist:                                          # close enough: arrive exactly
            self.pos = list(self.target_queue[0])
            self.timer.stop()
            self.position_changed.emit(self.pos)
            del self.target_queue[0]
            self.move_finished.emit()

            if len(self.target_queue) > 0:
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
        print(t)
        self.move_to(t)

    def move_to(self,info):
        new_target = info
        self.target_queue.append(new_target)
        self.target = list(new_target)
        if not self.timer.isActive():
            self.clock.start()
            self.timer.start()


    def __init__(self):
        self.clock = QElapsedTimer()
        self.timer = QTimer()

        self.speed = 100

        self.target_queue = []
        self.target = [0, 0, 0, 0, 100]
        self.pos = [0, 0, 0, 0, 100]

        self.timer.setInterval(16)  # 16 is about 60 updates a second
        self.timer.timeout.connect(self._step)
        super().__init__()
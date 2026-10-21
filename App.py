import shutil

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QApplication, QSplitter, QWidget

import pyvista as pv

from ControlArea import ControlArea
from Machine import Machine
from Parser import Parser
from SimArea import SimArea
from Terminal import Terminal


class App(QApplication):
    machine = ...
    control_area = ...
    simulation_area = ...
    terminal = ...
    split_horizontal = ...
    split_vertical = ...

    def start(self):
        self.exec()

    def __init__(self,args):
        super().__init__(args)


        self.machine = Machine()
        self.control_area = ControlArea()
        self.simulation_area = SimArea()
        self.terminal = Terminal()
        self.parser = Parser()
        self.parse_thread = QThread()

        self.control_area.jog_requested.connect(self.machine.jog)
        self.control_area.reset_requested.connect(self.machine.home_axis)
        self.control_area.move_requested.connect(self.machine.move_to)
        self.machine.position_changed.connect(self.simulation_area.move_head)
        self.machine.position_changed.connect(self.control_area.set_position)
        self.control_area.send_file.connect(self.parser.start_parse)
        self.parser.label_update.connect(self.control_area.update_loading_label)
        self.parser.finished_parse.connect(self.control_area.handle_parsed_data)
        self.control_area.stop_requested.connect(self.machine.stop)


        head_mesh = pv.read("./Simulation_STL/Head_Simulation.STL")
        self.simulation_area.add_head(head_mesh)


        self.split_horizontal = QSplitter(Qt.Orientation.Horizontal)
        self.split_horizontal.addWidget(self.control_area)
        self.split_horizontal.addWidget(self.simulation_area)
        self.split_horizontal.setSizes([300, 700])

        self.split_horizontal.setHandleWidth(6)  # thickness in pixels
        self.split_horizontal.setStyleSheet("""
               QSplitter::handle {
                   background-color: #888888;
               }
               QSplitter::handle:hover {
                   background-color: #4a90d9;
               }
           """)

        self.split_vertical = QSplitter(Qt.Orientation.Vertical)
        self.split_vertical.addWidget(self.split_horizontal)
        self.split_vertical.addWidget(self.terminal)
        self.split_vertical.setSizes([700, 300])
        self.split_vertical.setWindowTitle("UM")
        self.split_vertical.resize(1000, 600)
        self.split_vertical.show()

        self.parser.moveToThread(self.parse_thread)
        self.parse_thread.start()

        self.aboutToQuit.connect(self.clean_up)

        self.split_vertical.setHandleWidth(6)  # thickness in pixels
        self.split_vertical.setStyleSheet("""
               QSplitter::handle {
                   background-color: #888888;
               }
               QSplitter::handle:hover {
                   background-color: #4a90d9;
               }
           """)
    def clean_up(self):
        self.parse_thread.quit()
        shutil.rmtree(
            self.control_area.import_folder,
            ignore_errors=True
        )


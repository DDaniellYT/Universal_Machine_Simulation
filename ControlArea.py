import shutil
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QElapsedTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout


class ControlArea(QWidget):
    jog_requested = pyqtSignal(str, float)
    reset_requested = pyqtSignal(str)
    move_requested = pyqtSignal(float,float,float)
    send_file = pyqtSignal(str)
    stop_requested = pyqtSignal()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_W:
            print("emmited x , -5")
            self.jog_requested.emit("X", -5)
        if event.key() == Qt.Key.Key_S:
            print("emmited s , +5")
            self.jog_requested.emit("X", 5)
        if event.key() == Qt.Key.Key_A:
            print("emmited a , -5")
            self.jog_requested.emit("Y", -5)
        if event.key() == Qt.Key.Key_D:
            print("emmited d , +5")
            self.jog_requested.emit("Y", 5)
        if event.key() == Qt.Key.Key_Q:
            print("emmited q , -5")
            self.jog_requested.emit("Z", -5)
        if event.key() == Qt.Key.Key_E:
            print("emmited e , +5")
            self.jog_requested.emit("Z", 5)
        if event.key() == Qt.Key.Key_R:
            print("emmited reset ")
            self.move_requested.emit(self.pos[0],self.pos[1],100)
            self.reset_requested.emit("X")
            self.reset_requested.emit("Y")
            self.reset_requested.emit("Z")
        if event.key() == Qt.Key.Key_Escape:
            self.stop_requested.emit()

    def set_position(self,x,y,z):
        self.pos = (x,y,z)
        print("setted pos")

    def __init__(self):
        super().__init__()
        self.pos = [0,0,0]
        self.timer = QTimer(self)
        self.clock = QElapsedTimer()

        self.import_folder = Path.cwd() / "GCODE_Folder"
        self.import_folder.mkdir(parents=True,exist_ok=True)

        self.file_label = QLabel("No file selected")

        self.button_upload = QPushButton("Upload GCODE to follow")
        self.button_upload.clicked.connect(self.import_file)
        self.button_start = QPushButton("Start sequence")
        self.button_start.clicked.connect(self.queue_gcode)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_upload)
        layout.addWidget(self.button_start)
        layout.addWidget(self.file_label)
        layout.addStretch()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def file_parsed(self,str):
        print(str[0])
        if len(str) > 3:
            self.gcode = str[0]
            self.file_label.setText("can start sequence")
        else:
            self.file_label.setText(f"processing {str[0]}")

    def queue_gcode(self):
        print("emmited reset ")
        self.move_requested.emit(self.pos[0], self.pos[1], 100)
        self.reset_requested.emit("X")
        self.reset_requested.emit("Y")
        self.reset_requested.emit("Z")
        print("started gcode")
        for pos in self.gcode:
            self.move_requested.emit(pos[0],pos[1],pos[2])

    def import_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a file",
            str(Path.home()),
            "All files (*.*)"
        )

        # User cancelled the dialog
        if not file_path:
            return

        source = Path(file_path)
        destination = self.import_folder / source.name

        try:
            shutil.copy2(source, destination)
            self.file_label.setText(f"Imported: {source.name}")
            print(f"File saved to: {destination}")
            self.send_file.emit(file_path)

        except OSError as error:
            self.file_label.setText("File import failed")
            print(f"Could not import file: {error}")

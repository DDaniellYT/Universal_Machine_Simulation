from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread


class Parser(QObject):
    finished_parse = pyqtSignal(list)
    label_update = pyqtSignal(str)

    def start_parse(self, path):
        self.file_path = path
        self.parse_file()

    def parse_file(self):
        self.command_queue.clear() # Clear out old runs
        print("inside parse")
        try:
            with open(self.file_path, "r") as file:
                for i,line in enumerate(file):
                    dots = "." * ((i % 4) + 1)
                    self.label_update.emit(dots)
                    if line[0] == ';':
                        continue
                    if line[0] == "G" and line[1] == "1":
                        commands = line.split()
                        for command in commands:
                            if command[0] == "X":
                                self.pos[0] = float(command[1:])
                            if command[0] == "Y":
                                self.pos[1] = float(command[1:])
                            if command[0] == "Z":
                                self.pos[2] = float(command[1:])
                            if command[0] == "E":
                                self.pos[3] = float(command[1:])
                        self.command_queue.append(self.pos.copy())
            print(f"Parsing complete. Sending {len(self.command_queue)} commands to UI.")
            self.finished_parse.emit(self.command_queue)
        except OSError as error:
            print(f"Could not import file: {error}")


    def __init__(self):
        super().__init__()
        self.file_path = None
        self.command_queue = []
        self.pos = [0.0,0.0,0.0,0.0]
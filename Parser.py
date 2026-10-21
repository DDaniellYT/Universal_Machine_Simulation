from PyQt6.QtCore import QObject, pyqtSignal


class Parser(QObject):
    finished_parse = pyqtSignal(list)

    def parse_file(self,str):
        print("inside parse")
        try:
            with open(str, "r") as file:
                for i,line in enumerate(file):
                    self.finished_parse.emit(["."*(i+1%3)])
                    if line[0] == ';':
                        continue
                    print(line.strip())
                    if line[0] == "G" and line[1] == "1":
                        commands = line.split()
                        if commands[1][0] == "X":
                            self.pos[0] = float(commands[1][1:])
                        if commands[1][0] == "Y":
                            self.pos[1] = float(commands[1][1:])
                        if commands[1][0] == "Z":
                            self.pos[2] = float(commands[1][1:])
                        self.command_queue.append(self.pos)
            self.finished_parse.emit(self.command_queue)
        except OSError as error:
            print(f"Could not import file: {error}")


    def __init__(self):
        super().__init__()
        self.command_queue = []
        self.pos = [0.0,0.0,0.0]
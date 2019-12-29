PARAMETER_TYPES = ["X", "Y", "Z"]


class NCCommand:

    def __init__(self, address):
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.spindle_speed = 0
        self.tool_name = ""
        self.address = None
        self.initialize_command(address)

    def initialize_command(self, address):
        if address[0] == "T":
            self.tool_name = address[1:]
        elif address[0] == "S":
            self.spindle_speed = address[1:]
        else:
            self.address = address

    def set_parameters(self, param):
        if param[0] == "X":
            self.X = param[1:]
        elif param[0] == "Y":
            self.Y = param[1:]
        elif param[0] == "Z":
            self.Z = param[1:]

    def set_function(self, address):
        self.address = address

    def in_relation(self, address):
        # Only relations that are in the task code
        if address == "M06" and self.tool_name != "":
            return True
        elif address == "M03" and self.spindle_speed != 0:
            return True
        elif address[0] in PARAMETER_TYPES and (self.address == "G01" or self.address == "G00" or self.address == "G28"):
            return True
        else:
            return False


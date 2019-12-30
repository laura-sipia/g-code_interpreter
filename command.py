PARAMETER_TYPES = ["X", "Y", "Z"]


# Command's purpose is to handle one executable command
# One Command can include several NC-words e.g. G01 X-12.00 Y-12.00 is included in one Command since
# X and Y NC-words are linked to G01 NC-word.
# Variables X, Y and Z are for NC-words starting with X, Y and Z.
# Variable spindle_speed is for NC-word starting with S.
# Variable tool_name is for NC-word starting with T.
# All other NC-words are saved to address variable e.g. G00, M03. These describe a function.
class Command:

    def __init__(self, word):
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.spindle_speed = 0.0
        self.tool_name = ""
        self.address = None
        self.__initialize_command(word)

    # Decides where to save given address
    def __initialize_command(self, word):
        if word[0] == "T":
            self.tool_name = word[1:]
        elif word[0] == "S":
            self.spindle_speed = word[1:]
        else:
            self.address = word

    # Sets parameter for command
    def set_parameters(self, param):
        if param[0] == "X":
            self.X = float(param[1:])
        elif param[0] == "Y":
            self.Y = float(param[1:])
        elif param[0] == "Z":
            self.Z = float(param[1:])

    # Sets address/function for command
    def set_function(self, word):
        self.address = word

    # Decides whether given word (e.g. M03, G00, X-12.00) is linked/in relation to this command
    def is_related_to(self, word):
        # Only relations that are in the task code
        if word == "M06" and self.tool_name != "":
            return True
        elif word == "M03" and self.spindle_speed != 0:
            return True
        elif word[0] in PARAMETER_TYPES and (self.address == "G01" or self.address == "G00" or self.address == "G28"):
            return True
        else:
            return False


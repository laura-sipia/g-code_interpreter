from command import Command
from machineclient import MachineClient

PARAMETER_TYPE = ["X", "Y", "Z"]
NO_REACTION = ["%", "O", "("]


# Interpreter's task is to handle Commands: initialize them, execute them and remove them,
# read NC-lines and determine how to react to given line.
# Decides how each Command is being executed.
# Interpreter gets NC-lines from main program and handles the rest.
class Interpreter:

    def __init__(self):
        self.current_command = None
        self.machine_client = MachineClient()
        self.__M_ADDRESS_SWITCHER = {
            "06": self.__change_tool,
            "03": self.__set_spindle_speed,
            "09": self.__coolant_off,
            "05": self.__stop_spindle,
            "30": self.__go_home,
        }

        self.__G_ADDRESS_SWITCHER = {
            "00": dict(function=self.__move_xyz, parameters=None),
            "01": dict(function=self.__move_xyz, parameters=None),
            "17": dict(function=self.__print, parameters="LOG. XY plane selection."),
            "21": dict(function=self.__print, parameters="LOG. Programming in millimeters."),
            "40": dict(function=self.__radius_compensation, parameters=False),
            "49": dict(function=self.__length_offset_compensation, parameters=False),
            "80": dict(function=self.__print, parameters="LOG. Cancel canned cycle."),
            "94": dict(function=self.__print, parameters="LOG. Feedrate per minute."),
            "90": dict(function=self.__print,
                       parameters="LOG. Fixed cycle, simple cycle, for roughing (Z-axis emphasis)."),
            "54": dict(function=self.__print, parameters="LOG. Work coordinate systems (WCSs)."),
            "91": dict(function=self.__print, parameters="LOG. Incremental programming."),
            "28": dict(function=self.__move_home, parameters=None)
        }

    def read_line(self, line, line_nmbr):
        # Check if line needs a reaction
        if line[0] not in NO_REACTION:
            # Parse one NC-line
            self.__parse_line(line)
        else:
            if line[0] == "%":
                if line_nmbr == 0:
                    print("LOG. Program has started.")
                else:
                    # Execute the last command of the interpreter
                    self.__execute_current()
                    print("LOG. Program has ended")
            elif line[0] == "O":
                print("LOG. Running program number is {}.".format(line[1:]))
            elif line[0] == "(":
                # Line was a comment
                pass

    # Parses line to NC-words
    def __parse_line(self, line):
        nc_words = line.split(" ")

        for word in nc_words[1:]:
            self.__read_new_word(word)

    def __read_new_word(self, word):
        if self.current_command is None:
            self.current_command = Command(word)
        elif not self.current_command.is_related_to(word):
            # Next nc-word is not connected to current_command
            # Current command is executed and next nc-word is set to current command with new Command
            self.__execute_current()
            self.current_command = Command(word)
        elif self.current_command.is_related_to(word) and word[0] not in PARAMETER_TYPE:
            self.current_command.set_function(word)
        elif self.current_command.is_related_to(word) and word[0] in PARAMETER_TYPE:
            self.current_command.set_parameters(word)
        else:
            print("Error! NC-word {} could not be processed.".format(word))
            return

    def __execute_current(self):
        if self.current_command is not None:
            if self.current_command.address[0] == "M":
                self.__execute_m_command()
            elif self.current_command.address[0] == "G":
                self.__execute_g_command()
            elif self.current_command.address[0] == "F":
                self.__execute_f_command()
            else:
                # Command was not found
                print(f"Error! Command type was not recognized. Command was {self.current_command.address}.")
            del self.current_command
            self.current_command = None
        else:
            print("Error! No current command to execute.")
            return

    def __execute_f_command(self):
        if self.current_command.address is None:
            print("Error! Cannot execute command type of None.")
        feed_rate = self.current_command.address[1:]
        self.machine_client.set_feed_rate(float(feed_rate))

    def __execute_m_command(self):
        if self.current_command.address is None:
            print("Error! Cannot execute command type of None.")
        address_value = self.current_command.address[1:]
        # Get the function from switcher dictionary
        func = self.__M_ADDRESS_SWITCHER.get(
            address_value,
            lambda: "Error! Command {} was not recognized.".format(self.current_command.address)
        )
        func()

    def __execute_g_command(self):
        if self.current_command.address is None:
            print("Error! Cannot execute command type of None.")
        address_value = self.current_command.address[1:]
        # Get the function from switcher dictionary
        val = self.__G_ADDRESS_SWITCHER.get(
            address_value,
            dict(function=self.__print,
                 parameters="Error! Command {} was not recognized.".format(self.current_command.address))
        )
        func = val["function"]
        if val["parameters"] is not None:
            params = val["parameters"]
            func(params)
        else:
            func()

# ------------------------- HELPER FUNCTIONS ------------------------------
    def __change_tool(self):
        self.machine_client.change_tool(self.current_command.tool_name)

    def __set_spindle_speed(self):
        self.machine_client.set_spindle_speed(self.current_command.spindle_speed)

    def __coolant_off(self):
        self.machine_client.coolant_off()

    def __stop_spindle(self):
        self.machine_client.set_spindle_speed(0)
        self.machine_client.set_feed_rate(0)

    def __go_home(self):
        self.machine_client.home()

    def __move_xyz(self):
        if self.current_command.X is not None:
            x_value = float(self.current_command.X)
            self.machine_client.move_x(x_value)
        if self.current_command.Y is not None:
            y_value = float(self.current_command.Y)
            self.machine_client.move_y(y_value)
        if self.current_command.Z is not None:
            z_value = float(self.current_command.Z)
            self.machine_client.move_z(z_value)
        if self.current_command.X is None and self.current_command.Y is None and self.current_command.Z is None:
            self.machine_client.home()

    def __move_home(self):
        x_value = 0.0
        y_value = 0.0
        z_value = 0.0
        if self.current_command.X is not None:
            x_value = float(self.current_command.X)
        if self.current_command.Y is not None:
            y_value = float(self.current_command.Y)
        if self.current_command.Z is not None:
            z_value = float(self.current_command.Z)
        self.machine_client.move(x_value, y_value, z_value)

    def __print(self, message):
        print(message)

    def __radius_compensation(self, power):
        if power:
            self.machine_client.radius_compensation_on()
        else:
            self.machine_client.radius_compensation_off()

    def __length_offset_compensation(self, power):
        if power:
            self.machine_client.length_offset_compensation_on()
        else:
            self.machine_client.length_offset_compensation_off()

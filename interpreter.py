from command import NCCommand
from machineclient import MachineClient

PARAMETER_TYPE = ["X", "Y", "Z"]


class Interpreter:

    def __init__(self):
        self.current_command = None
        self.machine_client = MachineClient()
        self.machine_client.home()

    def execute_current(self):
        if self.current_command is not None:
            if self.current_command.address[0] == "M":
                # Handle M type of commands
                self.handle_m_command()
            elif self.current_command.address[0] == "G":
                # Handle G type of commands
                self.handle_g_command()
            elif self.current_command.address[0] == "F":
                # Handle F type of commands
                self.handle_f_command()
            else:
                # Command was not found
                print("Error! Command type was not recognized. Command was {}.".format(self.current_command.address))
            del self.current_command
            self.current_command = None
        else:
            # There is no current commant to execute
            print("Error! No current command to execute.")
            return

    def read_new_command(self, address):
        if self.current_command is None:
            # This is a new command
            self.current_command = NCCommand(address)
        elif not self.current_command.in_relation(address):
            # Next command is not connected to current_command
            # Current command is executed and next command is set to current command
            # This is a parameter that is attached to current command
            self.execute_current()
            self.current_command = NCCommand(address)

        elif self.current_command.in_relation(address) and address[0] not in PARAMETER_TYPE:
            # Next command is attached to current command and it is type of function
            self.current_command.set_function(address)
        elif self.current_command.in_relation(address) and address[0] in PARAMETER_TYPE:
            # Next command is attached to current command and is type of parameter
            self.current_command.set_parameters(address)
        else:
            # There is an error
            # Next command is neither in relation nor not in relation with current command
            print("Command {} could not be processed.".format(address))
            return

    def handle_f_command(self):
        if self.current_command.address is None:
            print("Error! Cannot execute command type of None.")
        feed_rate = self.current_command.address[1:]
        self.machine_client.set_feed_rate(float(feed_rate))

    def handle_m_command(self):
        if self.current_command.address is None:
            print("Error! Cannot execute command type of None.")
        address_value = self.current_command.address[1:]
        if address_value == "06":
            self.machine_client.change_tool(self.current_command.tool_name)
        elif address_value == "03":
            self.machine_client.set_spindle_speed(self.current_command.spindle_speed)
        elif address_value == "09":
            self.machine_client.coolant_off()
        elif address_value == "05":
            self.machine_client.set_spindle_speed(0)
            self.machine_client.set_feed_rate(0)
        elif address_value == "30":
            self.machine_client.home()
        else:
            # Command was not recognized
            print("Error! Command {} was not recognized.".format(self.current_command.address))
            return

    def handle_g_command(self):
        if self.current_command.address is None:
            print("Error! Cannot execute command type of None.")
        address_value = self.current_command.address[1:]
        if address_value == "00" or address_value == "01":
            # Rapid movement
            if self.current_command.X != 0:
                x_value = float(self.current_command.X)
                self.machine_client.move_x(x_value)
            if self.current_command.Y != 0:
                y_value = float(self.current_command.Y)
                self.machine_client.move_y(y_value)
            if self.current_command.Z != 0:
                z_value = float(self.current_command.Z)
                self.machine_client.move_z(z_value)
        elif address_value == "17":
            pass
        elif address_value == "21":
            pass
        elif address_value == "40":
            pass
        elif address_value == "49":
            pass
        elif address_value == "80":
            pass
        elif address_value == "94":
            pass
        elif address_value == "90":
            pass
        elif address_value == "54":
            pass
        elif address_value == "91":
            pass
        elif address_value == "28":
            z_value = float(self.current_command.Z)
            self.machine_client.move(0, 0, z_value)
        else:
            # Command was not recognized
            print("Error! Command {} was not recognized.".format(self.current_command.address))
            return


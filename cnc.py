import sys
from interpreter import Interpreter

NO_REACTION = ["%", "O", "("]


def parse_line(line, interpreter):
    commands = line.split(" ")

    for command in commands[1:]:
        interpreter.read_new_command(command)


def readfile(file, interpreter):
    f = open(file, "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        # Strip whitespaces from start
        line = line.lstrip()
        line = line.rstrip()
        # Check if line needs a reaction
        if line[0] not in NO_REACTION:
            # Parse one NC-line
            parse_line(line, interpreter)
        else:
            if line[0] == "%":
                if i == 0:
                    print("LOG. Program has started.")
                else:
                    print("LOG. Program has ended")
            elif line[0] == "O":
                print("LOG. Running program number is {}.".format(line[1:]))
            elif line[0] == "(":
                print("LOG. This is a comment line.")


def main():
    interpreter = Interpreter()
    filename = sys.argv[-1]
    # Get file from args
    readfile(filename, interpreter)


if __name__ == "__main__":
    main()


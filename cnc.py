import sys
from interpreter import Interpreter

NO_REACTION = ["%", "O", "("]


# Reads given file line by line and transmits the line to interpreter
def readfile(file, interpreter):
    # Read file line by line
    f = open(file, "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        # Strip whitespaces from start
        line = line.lstrip()
        line = line.rstrip()
        interpreter.read_line(line, i)


# Initialize interpreter and start file read
def main():
    interpreter = Interpreter()
    filename = sys.argv[-1]
    readfile(filename, interpreter)


if __name__ == "__main__":
    main()


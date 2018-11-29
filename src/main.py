from ics import ICSParser
from editor import Window

import argparse

parser = argparse.ArgumentParser(description="Create an image from cli")
parser.add_argument("--file", type=str, nargs=1, default=None)

if __name__ == "__main__":
    args = parser.parse_args()
    window = Window()  # Create a Canvas instance, but don't show it
    if args.file:
        # Don't start gui, read file
        actions = ICSParser(args.file[0]).parse()
        results = [window.do_action(action) for action in actions]
    else:
        window.show()


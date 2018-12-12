from ics import ICSParser
from editor import Window

import argparse
# Argparse is a built-in library for easy argument parsing from commandline
parser = argparse.ArgumentParser(description="Create an image from cli")
parser.add_argument("--file", type=str, nargs=1, default=None)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.file:  # If we specified a file, run in console mode
        window = Window(console=True)  # Create a Canvas instance, but don't show it
        # Don't start gui, read file
        actions = ICSParser(args.file[0]).parse()  # Parse file
        results = [window.do_action(action) for action in actions]  # Run action plan

    else:  # Otherwise we run the gui
        window = Window()  # Create a Canvas instance, but don't show it
        window.show()

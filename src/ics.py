# Author: Spencer Hanson
# Image Creation Syntax Parser
from editor import Action, ActionPlan
from editor.math import *
from editor.tools import *


class ICSValidationException(Exception):
    # Base exception thrown in parsing
    pass


class ImageArg(object):
    # Argument passed for a tool
    def __init__(self, name, arg_type):
        self.name = name
        self.arg_type = arg_type

    def __str__(self):
        # String representation of the argument
        return "{name}[{typ}]".format(name=self.name, typ=self.arg_type.__name__)

    def process(self, value):
        # Attempt to create the object given the value of the arg type
        return self.arg_type(value)

    def validate(self, value):
        # Validate the value to the arg type, returning errors as well to preserve stack trace
        try:
            self.process(value)
        except ValueError as e:
            return False, e
        else:
            return True, None


class ImageCommand(object):
    # Entire command, list of image args applied to a tool
    def __init__(self, clss, name, args=None):
        self.name = name
        self.args = args
        self.clss = clss

    def process(self, command, args):
        # Process args and command
        if self.name != command:
            raise ICSValidationException
        if not self.args:
            return Action(self.clss, {})
        arg_dict = {}

        for i in range(0, len(self.args)):  # For each arg
            if i >= len(args):  # Make sure number of args isn't too small
                raise ICSValidationException("Error processing command '{cmd}' not enough arguments given!\n"
                                             "Expected {expect}".format(cmd=command,
                                                                        expect=str([str(arg) for arg in self.args[i:]]))
                                             )
            valid, error = self.args[i].validate(args[i])  # Validate
            if not valid:
                raise ICSValidationException("Error processing command '{cmd}' with args '{args}' Arg '{arg}' invalid! "
                                             "Expected {expect} \n {err}".format(cmd=command, args=args,
                                                                                 arg=args[i], expect=str(self.args[i]),
                                                                                 err=str(error))
                                             )
            arg_dict[self.args[i].name] = self.args[i].process(args[i])
        return Action(self.clss, arg_dict)

    def __str__(self):
        # String representation of the ImageCommand
        return "ImageCommand({name})".format(name=self.name)


class ICSParser(object):
    # Parser class with list of image commands
    COMMANDS = [
        ImageCommand(DumpRaw, "dumpraw"),
        ImageCommand(NewImage, "newimage", [ImageArg("width", int), ImageArg("height", int)]),
        ImageCommand(SaveImage, "saveimage", [ImageArg("name", str)]),
        ImageCommand(LoadImage, "loadimage", [ImageArg("filename", str)]),
        ImageCommand(FlipX, "flipx"),
        ImageCommand(FlipY, "flipy"),
        ImageCommand(ColorShift, "colorshift", [ImageArg("color", RGB), ImageArg("saturation", Percent)]),
        ImageCommand(Rotate, "rotate", [ImageArg("center", Point), ImageArg("degrees", float)]),
        ImageCommand(Circle, "circle", [ImageArg("thickness", int), ImageArg("color", RGB), ImageArg("point", Point)]),
        ImageCommand(Line, "line", [ImageArg("thickness", int), ImageArg("color", RGB),
                                    ImageArg("point1", Point), ImageArg("point2", Point)])
    ]

    def __init__(self, filename):
        # Read in file
        with open(filename, "r") as f:
            self.data = f.readlines()

    @staticmethod
    def _find_command(line):
        # Find command within commandlist
        for cmd in ICSParser.COMMANDS:
            if line.startswith(cmd.name):
                return cmd
        raise ICSValidationException("Can't find command {}".format(line))

    def parse(self):
        # Parse the loaded file
        action_plan = ActionPlan()
        for line in self.data:
            if line.startswith("#") or not line.strip():  # Skip lines that start with a '#' it's a comment
                continue
            line = line.strip().lower()  # Remove whitespace and make lowercase for parsing
            command, *args = line.split(" ")  # Split args based on whitespace between

            cmd = ICSParser._find_command(line)  # Find command within list
            action = cmd.process(command, args)

            action_plan.add_action(action)
        return action_plan  # Return runnable action plan for window class

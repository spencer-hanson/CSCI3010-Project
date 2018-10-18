import tkinter


class Window(object):
    def __init__(self):
        self.root = tkinter.Tk()

        self.canvas = Canvas(self.root)
        self.toolbox = ToolBox(self.root)

    def show(self):
        self.canvas.setup()
        self.toolbox.setup()
        self.root.mainloop()

    def do_action(self, action):
        tool = action.get_instance()
        tool.execute()  # Execute the tool


class Canvas(object):
    WIDTH = 500
    HEIGHT = 600

    def __init__(self, gui):
        self.gui = gui

    def setup(self):
        self.gui.geometry("{}x{}".format(Canvas.WIDTH, Canvas.HEIGHT))
        self.gui.geometry("+{}+{}".format(int(self.gui.winfo_screenwidth() / 2 - Canvas.WIDTH / 2),
                                          int(self.gui.winfo_screenheight() / 2 - Canvas.HEIGHT / 2)))
        self.gui.title("Image Editor")


class ToolBox(object):
    WIDTH = 300
    HEIGHT = Canvas.HEIGHT

    def __init__(self, root):
        self.root = root
        self.gui = None

    def setup(self):
        self.gui = tkinter.Toplevel(self.root)
        self.gui.geometry("{}x{}".format(ToolBox.WIDTH, ToolBox.HEIGHT))
        self.gui.geometry("+{}+{}".format(int(self.root.winfo_screenwidth() / 2 - Canvas.WIDTH / 2) + Canvas.WIDTH + 2,
                                          int(self.root.winfo_screenheight() / 2 - Canvas.HEIGHT / 2)))
        self.gui.title("ToolBox")


class Action(object):
    def __init__(self, class_obj, kwargs):
        self.class_obj = class_obj
        self.kwargs = kwargs

    def get_instance(self):
        return self.class_obj(**self.kwargs)

    def __str__(self):
        return "Action({}, {})".format(self.class_obj.__name__, str(self.kwargs))


class ActionPlan(object):
    def __init__(self):
        self.actions = []

    def add_action(self, action):
        self.actions.append(action)

    def __iter__(self):
        return self.actions.__iter__()

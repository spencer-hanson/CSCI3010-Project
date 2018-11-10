import tkinter
from tkinter import Canvas, PhotoImage
from tkinter import filedialog
from dict_plus import DictPlus
from PIL import Image, ImageDraw
from editor.tools import *
from editor.math import Point, RGB


class Window(object):
    def __init__(self):
        self.root = tkinter.Tk()

        self.win_canvas = WindowCanvas(self.root)
        self.toolbox = ToolBox(self.root, self.win_canvas)

    def show(self):
        self.win_canvas.setup()
        self.toolbox.setup()
        self.root.mainloop()

    def do_action(self, action):
        tool = action.get_instance()
        tool.execute(self.win_canvas)  # Execute the tool


class WindowCanvas(object):
    WIDTH = 500
    HEIGHT = 600

    def __init__(self, gui):
        self.gui = gui
        self.tk_canvas = Canvas(gui)
        self.tk_canvas_img = PhotoImage(width=WindowCanvas.WIDTH, height=WindowCanvas.HEIGHT)
        self.img_canvas = None
        self.data_canvas = None
        self.img_fn = None

    def setup(self):
        self.gui.geometry("{}x{}".format(WindowCanvas.WIDTH, WindowCanvas.HEIGHT))
        self.gui.geometry("+{}+{}".format(int(self.gui.winfo_screenwidth() / 2 - WindowCanvas.WIDTH / 2),
                                          int(self.gui.winfo_screenheight() / 2 - WindowCanvas.HEIGHT / 2)))
        self.gui.title("Image Editor")

        # self.img_fn = Image.new("RGB", (200, 200), (255, 255, 255))
        # self.img_canvas = ImageDraw.Draw(self.img_fn)
        # self.data_canvas = DictPlus()
        NewImage(WindowCanvas.WIDTH, WindowCanvas.HEIGHT).execute(self)
        self.tk_canvas.create_rectangle(0, 0, WindowCanvas.WIDTH, WindowCanvas.HEIGHT, fill="#fff")
        self.tk_canvas.pack(fill='both', expand=True)
        self.tk_canvas.create_image((WindowCanvas.WIDTH / 2, WindowCanvas.HEIGHT / 2), image=self.tk_canvas_img,
                                    state="normal")

    def update_img(self):
        tw = 2
        for p in self.data_canvas:
            self.img_canvas.point(p, self.data_canvas[p])
            if self.data_canvas[p] != (255, 255, 255):  # TODO Update dict to hooked, add "version control"
                self.tk_canvas_img.put('#%02x%02x%02x' % self.data_canvas[p], p)
            # self.tk_canvas.create_oval(p, p, fill='#%02x%02x%02x' % self.data_canvas[p])


class ToolBox(object):
    WIDTH = 300
    HEIGHT = WindowCanvas.HEIGHT
    BRUSH_SIZE = 1
    COLOR = (0, 0, 0)

    def __init__(self, root, win_canvas):
        self.root = root
        self.win_canvas = win_canvas
        self.gui = None
        self.brush_on = False
        self.brush_txt = tkinter.StringVar()
        self.brush_txt.set("Paintbrush (Off)")

        self.brush_size = tkinter.StringVar()
        self.brush_size.set(str(ToolBox.BRUSH_SIZE))

        self.line_pt = None

    def do_point_paint(self, event):
        point_sq = Line.get_point_square(ToolBox.BRUSH_SIZE)
        for point in point_sq:
            new_point = (int(event.x + point[0]), int(event.y + point[1]))
            self.win_canvas.data_canvas[new_point] = ToolBox.COLOR
            self.win_canvas.tk_canvas_img.put("#%02x%02x%02x" % ToolBox.COLOR, new_point)

    def do_circle_paint(self, event):
        Circle(ToolBox.BRUSH_SIZE, RGB("", data=ToolBox.COLOR),
               Point("", data=(event.x, event.y))).execute(self.win_canvas)
        self.win_canvas.tk_canvas.create_oval(event.x - ToolBox.BRUSH_SIZE, event.y - ToolBox.BRUSH_SIZE,
                                              event.x + ToolBox.BRUSH_SIZE, event.y + ToolBox.BRUSH_SIZE,
                                              fill="#%02x%02x%02x" % ToolBox.COLOR)

    def do_line_paint(self, event):
        if self.line_pt:
            self.win_canvas.tk_canvas.create_line(self.line_pt[0], self.line_pt[1], event.x, event.y,
                                                  fill="#%02x%02x%02x" % ToolBox.COLOR, width=ToolBox.BRUSH_SIZE)
            Line(ToolBox.BRUSH_SIZE, RGB("", data=ToolBox.COLOR), Point("", data=self.line_pt),
                 Point("", data=(event.x, event.y))).execute(self.win_canvas)
            self.line_pt = None
        else:
            self.line_pt = event.x, event.y

    def save_to_file(self):
        fn = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                          filetypes=(("png files", "*.png"),))
        if fn:
            if not fn.endswith(".png"):
                fn += ".png"
            SaveImage(fn).execute(self.win_canvas)

    def load_image(self):
        fn = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("png files", "*.png"),))
        if fn:
            LoadImage(fn).execute(self.win_canvas)
            self.win_canvas.update_img()

    def new_image(self):
        NewImage(WindowCanvas.WIDTH, WindowCanvas.HEIGHT).execute(self)
        self.win_canvas.tk_canvas.create_rectangle(0, 0, WindowCanvas.WIDTH, WindowCanvas.HEIGHT, fill="#fff")

    def up_brushsize(self):
        ToolBox.BRUSH_SIZE += 1
        self.brush_size.set(str(ToolBox.BRUSH_SIZE))

    def down_brushsize(self):
        if ToolBox.BRUSH_SIZE - 1 <= 0:
            return
        ToolBox.BRUSH_SIZE -= 1
        self.brush_size.set(str(ToolBox.BRUSH_SIZE))

    def paintbrush(self):
        self.brush_on = not self.brush_on
        if self.brush_on:
            self.win_canvas.tk_canvas.unbind("<Button-1>")
            self.brush_txt.set("Paintbrush (On)")
            self.win_canvas.tk_canvas.bind("<B1-Motion>", self.do_point_paint)
        else:
            self.brush_txt.set("Paintbrush (Off)")
            self.win_canvas.tk_canvas.unbind("<B1-Motion>")

    def draw_circle(self):
        self.win_canvas.tk_canvas.unbind("<Button-1>")
        if self.brush_on:
            self.paintbrush()
        self.win_canvas.tk_canvas.bind("<B1-Motion>", self.do_circle_paint)

    def draw_line(self):
        self.win_canvas.tk_canvas.unbind("<B1-Motion>")
        if self.brush_on:
            self.paintbrush()
        self.win_canvas.tk_canvas.bind("<Button-1>", self.do_line_paint)

    def setup(self):
        self.gui = tkinter.Toplevel(self.root)
        self.gui.geometry("{}x{}".format(ToolBox.WIDTH, ToolBox.HEIGHT))
        self.gui.geometry(
            "+{}+{}".format(int(self.root.winfo_screenwidth() / 2 - WindowCanvas.WIDTH / 2) + WindowCanvas.WIDTH + 2,
                            int(self.root.winfo_screenheight() / 2 - WindowCanvas.HEIGHT / 2)))
        self.gui.title("ToolBox")

        frame = tkinter.Frame(self.gui, height=2, bd=1, relief=tkinter.SUNKEN)
        tkinter.Button(frame, command=self.paintbrush, textvariable=self.brush_txt).pack()
        inner_frame = tkinter.Frame(frame)
        tkinter.Button(inner_frame, text="Brush Size Up", command=self.up_brushsize).pack(side=tkinter.RIGHT)
        tkinter.Button(inner_frame, text="Brush Size Down", command=self.down_brushsize).pack(side=tkinter.LEFT)
        tkinter.Label(inner_frame, text=str(self.brush_size), textvariable=self.brush_size).pack(side=tkinter.RIGHT)
        inner_frame.pack()
        tkinter.Button(frame, text="Circle", command=self.draw_circle).pack()
        tkinter.Button(frame, text="Line", command=self.draw_line).pack()
        tkinter.Button(frame, text="Save", command=self.save_to_file).pack()
        tkinter.Button(frame, text="New Image", command=self.new_image).pack()
        tkinter.Button(frame, text="Load Image", command=self.load_image).pack()
        frame.pack(fill=tkinter.X, padx=5, pady=5)


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

import tkinter
from dict_plus import DictPlus
from tkinter import Canvas, PhotoImage
from tkinter import filedialog
from editor.math import Point, RGB, Percent
from editor.tools import *
from PIL import ImageTk
from tkinter.colorchooser import askcolor


class Window(object):
    def __init__(self, console=False):
        # Only init if we're not in console mode
        self.root = tkinter.Tk() if not console else None

        self.win_canvas = WindowCanvas(self.root)
        self.toolbox = ToolBox(self.root, self.win_canvas)

    def show(self):
        self.win_canvas.setup()
        self.toolbox.setup()
        self.root.mainloop()

    def do_action(self, action):
        tool = action.get_instance()
        return tool.execute(self.win_canvas)  # Execute the tool


class WindowCanvas(object):
    WIDTH = 500
    HEIGHT = 600

    def __init__(self, gui):
        self.gui = gui
        self.tk_canvas = Canvas(gui)
        self.tk_canvas_img = PhotoImage(width=WindowCanvas.WIDTH, height=WindowCanvas.HEIGHT)
        self.img_canvas = None  # Imagedraw canvas: ImageDraw.Draw(win_canvas.img_fn)
        self.data_canvas = None  # Data canvas: LossyDictPlus()
        self.img_fn = None  # Image file handle: Image.open(self.filename)

    def setup(self):
        # Basic gui setup, size, location, title, initializes canvas objects
        self.gui.geometry("{}x{}".format(WindowCanvas.WIDTH, WindowCanvas.HEIGHT))
        self.gui.geometry("+{}+{}".format(int(self.gui.winfo_screenwidth() / 2 - WindowCanvas.WIDTH / 2),
                                          int(self.gui.winfo_screenheight() / 2 - WindowCanvas.HEIGHT / 2)))
        self.gui.title("Image Editor")

        NewImage(WindowCanvas.WIDTH, WindowCanvas.HEIGHT).execute(self)

    def update_img(self):
        for p in self.data_canvas:
            self.img_canvas.point(p, self.data_canvas[p])

        self.tk_canvas_img = ImageTk.PhotoImage(self.img_fn)
        self.tk_canvas.create_image((WindowCanvas.WIDTH / 2, WindowCanvas.HEIGHT / 2),
                                    image=self.tk_canvas_img, state=tkinter.DISABLED)
        # TODO Update dict to hooked, add "version control"?


class ToolBox(object):
    WIDTH = 300
    HEIGHT = WindowCanvas.HEIGHT
    COLOR = (0, 0, 0)

    def __init__(self, root, win_canvas):
        self.root = root
        self.win_canvas = win_canvas
        self.gui = None

        self.brush_btns = DictPlus()  # Dict of buttons of brushes, used to disable current brush
        self.line_pt = None  # First clicked point for line tool
        self.saturation = None  # Scale for colorize saturation
        self.brush_size = None  # Scale for brush size
        self.rotation = None    # Scale for rotation
        self.rot_center = None  # Entry for rotation center

    def do_square_paint(self, event):
        point_sq = Line.get_point_square(self.brush_size.get())
        self.win_canvas.tk_canvas.create_rectangle(event.x, event.y,
                                                   event.x + self.brush_size.get(),
                                                   event.y + self.brush_size.get(),
                                                   outline="#%02x%02x%02x" % ToolBox.COLOR,
                                                   fill="#%02x%02x%02x" % ToolBox.COLOR,
                                                   state=tkinter.DISABLED)
        for point in point_sq:
            new_point = (int(event.x + point[0]), int(event.y + point[1]))
            self.win_canvas.data_canvas[new_point] = ToolBox.COLOR

    def do_circle_paint(self, event):
        Circle(self.brush_size.get(), RGB("", data=ToolBox.COLOR),
               Point("", data=(event.x, event.y))).execute(self.win_canvas)
        self.win_canvas.tk_canvas.create_oval(event.x - self.brush_size.get(), event.y - self.brush_size.get(),
                                              event.x + self.brush_size.get(), event.y + self.brush_size.get(),
                                              outline="#%02x%02x%02x" % ToolBox.COLOR,
                                              fill="#%02x%02x%02x" % ToolBox.COLOR,
                                              state=tkinter.DISABLED)

    def do_line_paint(self, event):
        if self.line_pt:
            self.win_canvas.tk_canvas.create_line(self.line_pt[0], self.line_pt[1], event.x, event.y,
                                                  fill="#%02x%02x%02x" % ToolBox.COLOR,
                                                  width=self.brush_size.get(),
                                                  state=tkinter.DISABLED)

            Line(self.brush_size.get(), RGB("", data=ToolBox.COLOR), Point("", data=self.line_pt),
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
        NewImage(WindowCanvas.WIDTH, WindowCanvas.HEIGHT).execute(self.win_canvas)
        self.win_canvas.tk_canvas.create_rectangle(0, 0, WindowCanvas.WIDTH, WindowCanvas.HEIGHT, fill="#fff")

    def _enable_brushes(self):
        for k in self.brush_btns:
            self.brush_btns[k].config(state=tkinter.NORMAL)

    def _rebind_brush(self, brush_name, func, binding_type="<B1-Motion>"):
        self._enable_brushes()
        self.brush_btns[brush_name].config(state=tkinter.DISABLED)
        self.win_canvas.tk_canvas.unbind("<Button-1>")
        self.win_canvas.tk_canvas.unbind("<B1-Motion>")
        self.win_canvas.tk_canvas.bind(binding_type, func)

    def draw_square(self):
        self._rebind_brush("square", self.do_square_paint)

    def draw_circle(self):
        self._rebind_brush("circle", self.do_circle_paint)

    def draw_line(self):
        self._rebind_brush("line", self.do_line_paint, binding_type="<Button-1>")

    def do_flipx(self):
        FlipX().execute(self.win_canvas)
        self.win_canvas.update_img()

    def do_flipy(self):
        FlipY().execute(self.win_canvas)
        self.win_canvas.update_img()

    def do_colorize(self):
        color = askcolor()
        if color[0]:
            ColorShift(RGB("", data=(round(color[0][0]), round(color[0][1]), round(color[0][2]))),
                       Percent("", data=self.saturation.get())).execute(self.win_canvas)
            self.win_canvas.update_img(full=True)

    def do_rotate(self):
        width, height = self.win_canvas.img_fn.size
        Rotate(Point("", data=(width / 2, height / 2)), self.rotation.get()).execute(self.win_canvas)
        self.win_canvas.update_img(full=True)

    def do_colorpick(self):
        color = askcolor()
        if color[0]:
            ToolBox.COLOR = (round(color[0][0]), round(color[0][1]), round(color[0][2]))

    def setup(self):
        # Basic separate window gui setup, set size, location, and title
        self.gui = tkinter.Toplevel(self.root)
        self.gui.geometry("{}x{}".format(ToolBox.WIDTH, ToolBox.HEIGHT))
        self.gui.geometry(
            "+{}+{}".format(int(self.root.winfo_screenwidth() / 2 - WindowCanvas.WIDTH / 2) + WindowCanvas.WIDTH + 2,
                            int(self.root.winfo_screenheight() / 2 - WindowCanvas.HEIGHT / 2)))
        self.gui.title("ToolBox")

        frame = tkinter.Frame(self.gui, height=2, bd=1, relief=tkinter.SUNKEN)

        # Brushes
        inner_frame = tkinter.Frame(frame)
        self.brush_btns["square"] = tkinter.Button(inner_frame, text="Brush", command=self.draw_square)
        self.brush_btns["square"].pack(side=tkinter.LEFT)

        self.brush_btns["circle"] = tkinter.Button(inner_frame, text="Circle", command=self.draw_circle)
        self.brush_btns["circle"].pack(side=tkinter.LEFT)

        self.brush_btns["line"] = tkinter.Button(inner_frame, text="Line", command=self.draw_line)
        self.brush_btns["line"].pack(side=tkinter.RIGHT)

        self.draw_square()  # Set default starting brush to square
        inner_frame.pack()

        # Brush sizer
        inner_frame = tkinter.Frame(frame)
        tkinter.Label(inner_frame, text=str("Brush Size"), textvariable=self.brush_size).pack(side=tkinter.LEFT)
        self.brush_size = tkinter.Scale(inner_frame, from_=1, to=20, orient=tkinter.HORIZONTAL)
        self.brush_size.set(3)
        self.brush_size.pack(side=tkinter.RIGHT)
        inner_frame.pack()

        # File I/O
        inner_frame = tkinter.Frame(frame)
        tkinter.Button(inner_frame, text="Save", command=self.save_to_file).pack(side=tkinter.LEFT)
        tkinter.Button(inner_frame, text="New Image", command=self.new_image).pack(side=tkinter.RIGHT)
        tkinter.Button(inner_frame, text="Load Image", command=self.load_image).pack(side=tkinter.RIGHT)
        inner_frame.pack()

        # Flip Transforms
        inner_frame = tkinter.Frame(frame)
        tkinter.Button(inner_frame, text="Flip X", command=self.do_flipx).pack(side=tkinter.LEFT)
        tkinter.Button(inner_frame, text="Flip Y", command=self.do_flipy).pack(side=tkinter.RIGHT)
        inner_frame.pack()

        # Colorize Transform
        inner_frame = tkinter.Frame(frame)
        tkinter.Button(inner_frame, text="Colorize", command=self.do_colorize).pack(side=tkinter.LEFT)
        tkinter.Label(inner_frame, text=str("Saturation (%)"), textvariable=self.brush_size).pack(side=tkinter.LEFT)
        self.saturation = tkinter.Scale(inner_frame, from_=1, to=99, orient=tkinter.HORIZONTAL)
        self.saturation.pack(side=tkinter.RIGHT)
        inner_frame.pack()

        # Rotate Transform
        inner_frame = tkinter.Frame(frame)
        tkinter.Button(inner_frame, text="Rotate", command=self.do_rotate).pack(side=tkinter.LEFT)
        self.rotation = tkinter.Scale(inner_frame, from_=1, to=259, orient=tkinter.HORIZONTAL)
        self.rotation.set(90)
        self.rotation.pack(side=tkinter.RIGHT)
        inner_frame.pack()

        # Color picker
        tkinter.Button(frame, text="Pick Color", command=self.do_colorpick).pack()

        frame.pack(fill=tkinter.X, padx=5, pady=5)
        frame.update()


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

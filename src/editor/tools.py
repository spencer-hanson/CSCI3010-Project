from PIL import Image, ImageDraw
from editor.math import RGB, Point, LossyDictPlus


class Tool(object):
    def execute(self, win_canvas):
        raise NotImplementedError


class LoadImage(Tool):
    def __init__(self, filename):
        self.filename = filename

    def execute(self, win_canvas):
        win_canvas.data_canvas = LossyDictPlus()
        win_canvas.img_fn = Image.open(self.filename)
        win_canvas.img_canvas = ImageDraw.Draw(win_canvas.img_fn)
        width, height = win_canvas.img_fn.size
        for x in range(0, width):
            for y in range(0, height):
                win_canvas.data_canvas[(x, y)] = win_canvas.img_fn.getpixel((x, y))


class NewImage(Tool):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def execute(self, win_canvas):
        win_canvas.data_canvas = LossyDictPlus()
        pixels = [(x, y) for x in range(0, self.width) for y in range(0, self.height)]
        for pixel in pixels:
            win_canvas.data_canvas[pixel] = (255, 255, 255)
        win_canvas.img_fn = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        win_canvas.img_canvas = ImageDraw.Draw(win_canvas.img_fn)


class SaveImage(Tool):
    def __init__(self, name):
        self.name = name

    def execute(self, win_canvas):
        if win_canvas.img_fn:
            win_canvas.update_img()
            win_canvas.img_fn.save(self.name)


class Pencil(Tool):
    def __init__(self, color, point):
        pass

    def execute(self, win_canvas):
        raise NotImplementedError  # TODO Implement Pencil


class Circle(Tool):
    def __init__(self, thickness, color, point):
        self.thickness = thickness
        self.color = color
        self.point = point

    def execute(self, win_canvas):
        for x in range(-self.thickness, self.thickness):
            for y in range(-self.thickness, self.thickness):
                if x ** 2 + y ** 2 < self.thickness ** 2:
                    win_canvas.data_canvas[(self.point.x + x, self.point.y + y)] = self.color.to_tuple()


class Line(Tool):
    def __init__(self, thickness, color, point1, point2):
        self.thickness = thickness
        self.color = color
        self.point1 = point1
        self.point2 = point2

    @staticmethod
    def get_point_square(size):
        # Get a square of points like
        # 1: [(0,,0)]
        # 2: [(0,0),(1,0),(0,1),(1,1)]
        # etc..
        points = []
        for i in range(0, size ** 2):
            diff = (i // size, i % size)
            points.append(diff)
        return points

    def execute(self, win_canvas):
        my, mx = self.point1.slope_to(self.point2)
        if mx == 0 and my == 0:
            points = [(self.point1.x, self.point1.y)]
        elif mx == 0:
            start = min(self.point1.y, self.point2.y)
            end = max(self.point1.y, self.point2.y)
            points = zip([self.point1.x] * abs(end - start), range(start, end))
        elif my == 0:
            start = min(self.point1.x, self.point2.x)
            end = max(self.point1.x, self.point2.x)
            points = zip(range(start, end), [self.point1.y] * abs(end - start))
        else:
            start = min(self.point1.x, self.point2.x)
            end = max(self.point1.x, self.point2.x)
            f = lambda x: (my / mx) * (x - self.point1.x) + self.point1.y
            points = [(x, f(x)) for x in range(start, end)]

        point_square = self.get_point_square(self.thickness)
        for point in points:
            for point_sq in point_square:
                win_canvas.data_canvas[
                    (int(point[0] + point_sq[0]), int(point[1] + point_sq[1]))] = self.color.to_tuple()


class FlipX(Tool):
    def __init__(self):
        super(FlipX, self).__init__()
        pass

    def execute(self, win_canvas):
        width, _ = win_canvas.img_fn.size

        def flipx(k, v):
            w1, h1 = k
            return (width - w1 - 1, h1), v

        win_canvas.data_canvas.map(flipx)  # A simple mapping to flip x


class DumpRaw(Tool):
    def execute(self, win_canvas):
        print(str(win_canvas.data_canvas))


class FlipY(Tool):
    def __init__(self):
        super(FlipY, self).__init__()

    def execute(self, win_canvas):
        _, height = win_canvas.img_fn.size

        def flipy(k, v):
            w1, h1 = k
            return (w1, height - h1 - 1), v

        win_canvas.data_canvas.map(flipy)


class ColorShift(Tool):
    def __init__(self, color, saturation):
        self.color = color
        self.saturation = saturation

    def execute(self, win_canvas):
        def colorize(k, v):
            return k, RGB("", data=v).colorize(self.color, self.saturation.value).to_tuple()
        win_canvas.data_canvas.map(colorize)


class Rotate(Tool):
    def __init__(self, center, degrees):
        self.center = center
        self.degrees = degrees

    def execute(self, win_canvas):
        width, height = win_canvas.img_fn.size
        def rotate(k):
            return Point(None, data=k).rotate(self.center, self.degrees).to_tuple()

        def clean(k, v):
            x, y = k
            if x < 0 or x > width:
                return False
            elif y < 0 or y > height:
                return False
            return True
        win_canvas.data_canvas.rekey(rotate)
        win_canvas.data_canvas.filter(clean)

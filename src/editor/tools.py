from PIL import Image, ImageDraw
from editor.math import RGB, Point, LossyDictPlus


class Tool(object):
    # Superclass of the tool to require subclasses to implement execute()
    def execute(self, win_canvas):
        raise NotImplementedError


class LoadImage(Tool):
    # Load an image given a filename
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
    # Create a new image, given a width and height
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
        win_canvas.tk_canvas.create_rectangle(0, 0, self.width, self.height, fill="#ffffff", outline="#ffffff", state="disabled")
        win_canvas.tk_canvas.pack(fill='both', expand=True)
        win_canvas.tk_canvas.create_image((self.width / 2, self.height / 2), image=win_canvas.tk_canvas_img, state="disabled")


class SaveImage(Tool):
    # Save an Image given a filename
    def __init__(self, name):
        self.name = name

    def execute(self, win_canvas):
        if win_canvas.img_fn:
            win_canvas.update_img()
            win_canvas.img_fn.save(self.name)


class Pencil(Tool):
    # Draw a point with a given color
    def __init__(self, color, point):
        self.color = color
        self.point = point

    def execute(self, win_canvas):
        win_canvas.data_canvas[self.point.to_tuple()] = self.color.to_tuple()


class Circle(Tool):
    # Draw a circle with thickness (radius), color and center point
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
    # Draw a line with a thickness and color from point1 to point2
    def __init__(self, thickness, color, point1, point2):
        self.thickness = thickness
        self.color = color
        self.point1 = point1
        self.point2 = point2

    @staticmethod
    def get_point_square(size):
        # Get a square of points like
        # To create the given thickness/size
        # 1: [(0,,0)]
        # 2: [(0,0),(1,0),(0,1),(1,1)]
        # etc..
        points = []
        for i in range(0, size ** 2):
            diff = (i // size, i % size)
            points.append(diff)
        return points

    def execute(self, win_canvas):
        my, mx = self.point1.slope_to(self.point2)  # Get slope to other point
        if mx == 0 and my == 0:  # If it's the same point
            points = [(self.point1.x, self.point1.y)]   # List of points
        elif mx == 0:  # If it's a horizontal line
            start = min(self.point1.y, self.point2.y)
            end = max(self.point1.y, self.point2.y)
            points = zip([self.point1.x] * abs(end - start), range(start, end))  # List of points
        elif my == 0:  # If it's a vertical line
            start = min(self.point1.x, self.point2.x)
            end = max(self.point1.x, self.point2.x)
            points = zip(range(start, end), [self.point1.y] * abs(end - start))  # List of points
        else:  # Otherwise it's a regular line
            start = min(self.point1.x, self.point2.x)
            end = max(self.point1.x, self.point2.x)
            f = lambda x: (my / mx) * (x - self.point1.x) + self.point1.y  # Function of the line between the points
            points = [(x, f(x)) for x in range(start, end)]  # List of points

        point_square = self.get_point_square(self.thickness)  # Create an identity point-square for the given thickness
        for point in points:
            for point_sq in point_square:
                # Translate the identity point-square to each point in the point list to create the line
                win_canvas.data_canvas[
                    (int(point[0] + point_sq[0]), int(point[1] + point_sq[1]))] = self.color.to_tuple()


class DumpRaw(Tool):
    # Dump the raw value of the data canvas, and return it (for testing/debugging)
    def execute(self, win_canvas):
        print(str(win_canvas.data_canvas))
        return win_canvas.data_canvas


class FlipX(Tool):
    # Flip X of all pixels
    def execute(self, win_canvas):
        width, _ = win_canvas.img_fn.size

        def flipx(k, v):
            w1, h1 = k
            return (width - w1 - 1, h1), v

        win_canvas.data_canvas.map(flipx)  # A simple mapping to flip x


class FlipY(Tool):
    # Flip Y of all pixels
    def __init__(self):
        super(FlipY, self).__init__()

    def execute(self, win_canvas):
        _, height = win_canvas.img_fn.size

        def flipy(k, v):
            w1, h1 = k
            return (w1, height - h1 - 1), v

        win_canvas.data_canvas.map(flipy)  # Simple mapping to flip y


class ColorShift(Tool):
    # Colorshift the canvas given a color and saturation
    def __init__(self, color, saturation):
        self.color = color
        self.saturation = saturation

    def execute(self, win_canvas):
        def colorize(k, v):
            return k, RGB("", data=v).colorize(self.color, self.saturation.value).to_tuple()
        # Map the canvas to another using the colorize function to change each pixel color
        win_canvas.data_canvas.map(colorize)


class Rotate(Tool):
    # Rotate the the image about a center a certain amount of degrees
    def __init__(self, center, degrees):
        self.center = center
        self.degrees = degrees

    def execute(self, win_canvas):
        width, height = win_canvas.img_fn.size

        def rotate(k):  # Rotate key (point)
            return Point(None, data=k).rotate(self.center, self.degrees).to_tuple()

        def clean(k, v):  # Clean up the points that aren't within the image bounds
            x, y = k
            if x < 0 or x > width:
                return False
            elif y < 0 or y > height:
                return False
            return True
        win_canvas.data_canvas.rekey(rotate)  # Rotate pixels
        win_canvas.data_canvas.filter(clean)  # Remove the image removed bounds

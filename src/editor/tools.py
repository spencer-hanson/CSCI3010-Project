class Tool(object):
    def execute(self):
        raise NotImplementedError


class NewImage(Tool):
    def __init__(self, width, height):
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement NewImage


class SaveImage(Tool):
    def __init__(self, name):
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement SaveImage


class Pencil(Tool):
    def __init__(self, color):
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement Pencil


class Circle(Tool):
    def __init__(self, thickness, color, point):
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement Circle


class Line(Tool):
    def __init__(self, thickness, color, point1, point2):
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement Line


class Transforms(Tool):
    def __init__(self):
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement Transforms


class FlipX(Transforms):
    def __init__(self):
        super(FlipX, self).__init__()
        pass

    def execute(self):
        raise NotImplementedError  # TODO Implement FlipX


class FlipY(Transforms):
    def __init__(self):
        super(FlipY, self).__init__()

    def execute(self):
        raise NotImplementedError  # TODO Implement FlipY


class ColorShift(Transforms):
    def __init__(self, color):
        super(ColorShift, self).__init__()

    def execute(self):
        raise NotImplementedError  # TODO Implement Colorshift


class Rotate(Transforms):
    def __init__(self, rotate):
        super(Rotate, self).__init__()

    def execute(self):
        raise NotImplementedError # TODO Implement Rotate

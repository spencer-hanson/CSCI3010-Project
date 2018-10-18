class Type(object):
    def __init__(self, data):
        # Throw a ValueError in here to invalidate the type
        if not isinstance(data, str):
            raise ValueError("Invalid data for type {}".format(self.__class__.__name__))


class Point(Type):
    def __init__(self, str_data):
        super(Point, self).__init__(str_data)
        x, y = str_data.split(",")  # Will raise ValueError if it doesn't split correctly
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class RGB(Type):
    def __init__(self, rgb_data):
        super(RGB, self).__init__(rgb_data)
        r, g, b = rgb_data.split(",")
        self.red = int(r)
        self.green = int(g)
        self.blue = int(b)

    def __str__(self):
        return "[{}, {}, {}]".format(self.red, self.blue, self.green)
class Type(object):
    def __init__(self, data):
        # Throw a ValueError in here to invalidate the type
        if not isinstance(data, str):
            raise ValueError("Invalid data for type {}".format(self.__class__.__name__))


class Point(Type):
    def __init__(self, str_data, data=None):
        if data:
            str_data = ""
            self.x = data[0]
            self.y = data[1]
        else:
            x, y = str_data.split(",")  # Will raise ValueError if it doesn't split correctly
            self.x = int(x)
            self.y = int(y)

        super(Point, self).__init__(str_data)

    def slope_to(self, point2):
        my = (point2.y - self.y)
        mx = (point2.x - self.x)
        return my, mx

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class RGB(Type):
    def __init__(self, rgb_data, data=None):
        if data:
            self.red = data[0]
            self.green = data[1]
            self.blue = data[2]
            rgb_data = ""
        else:
            r, g, b = rgb_data.split(",")
            self.red = int(r)
            self.green = int(g)
            self.blue = int(b)
        super(RGB, self).__init__(rgb_data)

    def to_tuple(self):
        return self.red, self.green, self.blue

    def __str__(self):
        return "[{}, {}, {}]".format(self.red, self.blue, self.green)

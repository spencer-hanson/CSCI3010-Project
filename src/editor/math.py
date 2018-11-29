import  math
from dict_plus import DictPlus


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

    def rotate(self, center, degrees):

        rads = math.radians(degrees)
        tx = self.x-center.x  # Translated x & y
        ty = self.y-center.y

        xp = tx*math.cos(rads) - ty*math.sin(rads)
        yp = ty*math.cos(rads) + tx*math.sin(rads)

        xp += center.x  # Add back to un-translate
        yp += center.y

        xp = round(xp)
        yp = round(yp)
        return Point("", data=(xp, yp))

    def to_tuple(self):
        return self.x, self.y

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

        def bound(el):  # Make sure that we're in the bounds of [0, 255]
            if el > 255:
                return 255
            elif el < 0:
                return 0
            else:
                return el
        self.red = bound(self.red)
        self.green = bound(self.green)
        self.blue = bound(self.blue)

        super(RGB, self).__init__(rgb_data)

    def to_tuple(self):
        return round(self.red), round(self.green), round(self.blue)

    def __sub__(self, other):
        r = self.red - other.red
        g = self.green - other.green
        b = self.blue - other.blue
        return RGB("", data=(r, g, b))

    def __mul__(self, other):
        if not isinstance(other, float) and not isinstance(other, int):
            raise NotImplementedError("Non-Scalar Multiplication not implemented!")

        r = self.red * other
        g = self.green * other
        b = self.blue * other
        return RGB("", data=(r, g, b))

    def __add__(self, other):
        if not isinstance(other, RGB):
            raise TypeError("Addition between RGB and non-RGB not allowed!")
        r = max(self.red, other.red) - min(self.red, other.red)
        g = self.green + other.green
        b = self.blue + other.blue
        return RGB("", data=(r, g, b))

    def colorize(self, other, saturation):
        x1, y1, z1 = self.to_tuple()
        a, b, c = (self - other).to_tuple()
        x = lambda t: a*t + x1  # Standard parametric equation form
        y = lambda t: b*t + y1
        z = lambda t: c*t + z1
        saturation = ((100 - saturation) - 100) / 100
        return RGB("", data=(x(saturation), y(saturation), z(saturation)))

        # Calculation notes
        # v_dir = self - other  # Direction vector
        # v_abs = math.sqrt(v_dir.red ** 2 + v_dir.green ** 2 + v_dir.blue ** 2)  # abs(direction vector)
        # dist = self.distance_to(other)*(saturation/100)
        # if v_abs == 0:  # We're already at that color we can't colorshift it any more
        #     return self.to_tuple()
        # new_v = v_dir*(dist/v_abs)

    def distance_to(self, other):
        return math.sqrt((other.red-self.red)**2 + (other.green-self.green)**2 + (other.blue-self.blue)**2)

    def __str__(self):
        return "[{}, {}, {}]".format(self.red, self.green, self.blue)


class Percent(Type):
    def __init__(self, percent_data, data=None):
        if data:
            self.value = data
        else:
            self.value = int(percent_data)
        if self.value < 0 or self.value > 100:
            raise ValueError("Invalid percent! Must be between 0 and 100!")

        super(Percent, self).__init__(percent_data)

    def __str__(self):
        return "{}%".format(self.value)


class LossyDictPlus(DictPlus):
    def _update_indexes(self, from_idx):
        self._indexes = self._make_index()
        for idx, el in enumerate(self._elements):
            # Ignore key collisions, as they are just overwrites for image operations
            # if self._indexes.has(el.id):
            #     raise IndexError("Duplicate key {} found!".format(el.id))
            self._indexes.set(el.id, idx)
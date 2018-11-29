import sys
import os
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path + '/../src')
sys.path.insert(0, path + '/../src/editor')

from ics import ICSParser
from editor.gui import Window


TESTS = [
    "tests/test_circle.ics",
    "tests/test_colorize.ics",
    "tests/test_flipx.ics",
    "tests/test_flipy.ics",
    "tests/test_line.ics",
    "tests/test_rotate.ics"
]


def test_image_editor():
    for test in TESTS:
        window = Window()
        actions = ICSParser(test).parse()
        results = [window.do_action(action) for action in actions]

    print("All tests passed!")


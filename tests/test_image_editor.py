from ics import ICSParser
from editor.gui import Window


TESTS = [
    "test_circle.ics",
    "test_colorize.ics",
    "test_flipx.ics",
    "test_flipy.ics",
    "test_line.ics",
    "test_rotate.ics"
]

def test_image_editor():
    for test in TESTS:
        window = Window()
        actions = ICSParser(test).parse()
        results = [window.do_action(action) for action in actions]

    print("All tests passed!")

test_image_editor()
import os.path as op
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QColor

def make_icon(path: str) -> QIcon:
    icon = QIcon()
    icon.addFile(path)
    return icon


FRONT_PATH = op.abspath(op.join(op.dirname(__file__), "..", "..", "snapcheck-front"))
DEFAULT_PORT = 3000
DEFAULT_URL = "127.0.0.1"

ASSETS_PATH = op.abspath(op.join(op.dirname(__file__), "assets"))
SPLASH_PATH = op.join(ASSETS_PATH, "splash.jpg")

APP_ICON = icon_path = op.join(ASSETS_PATH, "icon.svg") 
MINIMIZE_ICON = op.join(ASSETS_PATH, "minimize.svg")
NORMAL_ICON = op.join(ASSETS_PATH, "normal.svg")
CLOSE_ICON = op.join(ASSETS_PATH, "close.svg")
MAXIMIZE_ICON = op.join(ASSETS_PATH, "maximize.svg")

ICON_COLOR = "#9c9c9c"

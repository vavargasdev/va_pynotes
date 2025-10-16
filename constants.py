import os

# --- Constants ---

# IDs
ID_TAG_START = 100
ID_UPDATE = 200
ID_CLEAR_ALL = 210
ID_CLEAR_TAGS = 220
ID_EXIT = 230
ID_INSERT = 240
ID_ABOUT = 250
ID_SPLITTER = 300
ID_SEARCH = 310

# Dimensions and Paths
LEFT_PANEL_WIDTH = 310
WINDOW_DIMS = {"w": 1400, "h": 1000}
IMAGE_DIR = os.path.join(os.getcwd(), "images")
THUMB_DIR = os.path.join(os.getcwd(), "images/thumbs")
THUMB_SIZE = (250, 250)
PADDING = 10
DEFAULT_FONT = "Verdana"
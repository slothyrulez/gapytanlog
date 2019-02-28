import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GTK_APPLICATION_ID = "org.holydog.gapytanlog"
APPLICATION_NAME = "Gapytan Log"

APP_WINDOW_TITLE = APPLICATION_NAME
UI_BORDER_WIDTH = 6
REVEAL_DURATION = 1000

DEFAULT_PROJECT_NAME = "default"
# DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_LEVEL = logging.DEBUG

RESOURCES_DIR_NAME = "resources"

MENU_UI_FILENAME = "gapytanlog_menu.xml"
MENU_UI_PATH = os.path.join(BASE_DIR, RESOURCES_DIR_NAME, MENU_UI_FILENAME)

DATABASE_NAME = "gapytanlog"
DATABASE_FILENAME = "{}.db".format(DATABASE_NAME)
DATABASE_PATH = os.path.join(BASE_DIR, "..", DATABASE_FILENAME)

LIMITED_MAX_LENGTH = 511

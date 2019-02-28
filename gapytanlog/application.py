import sys

import logging
logging.getLogger(__name__)

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, GObject, Gdk

from gapytanlog.controllers.entries import get_entries_controller
from gapytanlog.constants import GTK_APPLICATION_ID, MENU_UI_PATH


class GapytanLog(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id=GTK_APPLICATION_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            **kwargs
        )
        self.window = None
        self.controller = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        # Initialize DB
        # models.create_tables()

        # Application menu
        builder = Gtk.Builder()
        builder.add_from_file(MENU_UI_PATH)
        self.set_app_menu(builder.get_object("menu"))

    def do_activate(self):
        if not self.window and not self.controller:
            self.controller = get_entries_controller(self)
            self.window = self.controller.get_window()
        self.window.present()

    def on_about(self, action, param):
        logging.debug("action {} parama {}".format(action, param))
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def on_quit(self):
        logging.debug("quit")
        self.quit()


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = GapytanLog()
    app.run(sys.argv)

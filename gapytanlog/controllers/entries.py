import pendulum

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from gapytanlog.constants import APP_WINDOW_TITLE
from gapytanlog.views.entries import EntriesView
from gapytanlog.models.entries import EntriesModel


class EntriesController:
    def __init__(self, *, view, model):
        self.view = view
        self.model = model

        self.set_tree_view_model()
        self.fill_tree_data()
        self.fill_calendar_data()

        self.connect_events()

        self.view.show_all()

    def get_window(self):
        return self.view

    def set_tree_view_model(self):
        self.view.tree_view.set_model(self.model.entries_store)

    def fill_tree_data(self):
        self.model.fill_store()

    def fill_calendar_data(self):
        selected_date_month_entries = self.model.get_selected_date_month_year_entries()
        self.view.date_calendar_button.calendar.mark_entries(
            [
                pendulum.parse(raw_entry.day).day
                for raw_entry in selected_date_month_entries
            ]
        )

    def connect_events(self):
        self.view.date_calendar_button.connect(
            "clicked", self.on_click_date_calendar_button
        )
        self.view.header.header_button_add.connect(
            "clicked", self.on_click_header_button_add
        )
        self.view.date_calendar_button.calendar.connect(
            "day-selected", self.on_click_calendar_day
        )
        self.view.date_calendar_button.calendar.connect(
            "month-changed", self.on_calendar_month_changed
        )
        self.view.simple_entry.connect("activate", self.on_activate_simple_entry)
        self.view.tree_view.connect(
            "button-press-event", self.on_button_press_tree_view
        )

    # Events
    def on_click_date_calendar_button(self, button):
        self.view.date_calendar_button.calendar_popover.set_relative_to(button)
        self.view.date_calendar_button.calendar_popover.show_all()
        self.view.date_calendar_button.calendar_popover.popup()

    def on_click_header_button_add(self, button):
        print("TODO ADDDDDD")

    # Calendar
    def on_click_calendar_day(self, calendar):
        year, month, day = calendar.get_date()
        date = pendulum.date(year=year, month=month + 1, day=day)
        # Set selected date
        self.model.set_entries_selected_date(date)
        # Change calendar toggle button
        self.view.date_calendar_button.set_label(date.to_date_string())
        # Load selected date entries
        self.model.fill_store()
        # Hide popover
        self.view.date_calendar_button.calendar_popover.popdown()

    def on_calendar_month_changed(self, calendar):
        calendar.clear_marks()
        year, month, _ = calendar.get_date()
        month_entries = self.model.get_year_month_entries(year=year, month=month + 1)
        calendar.mark_entries(
            [pendulum.parse(raw_entry.day).day for raw_entry in month_entries]
        )

    # Tree
    def on_button_press_tree_view(self, tree_view, event):
        # Right click
        print(event, event.type, event.button)
        path, _, _, _ = self.view.tree_view.get_path_at_pos(int(event.x), int(event.y))

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            menu = Gtk.Menu()
            delete_item = Gtk.MenuItem("Delete entry")
            delete_item.connect("activate", self.on_click_menu_delete, path)
            menu.add(delete_item)
            menu.attach_to_widget(self.view.tree_view)
            menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
            menu.show_all()
        # Left | center click
        elif (
            event.type == Gdk.EventType.BUTTON_PRESS
            and event.button == 1
            or event.button == 2
        ):
            model_iter = self.model.entries_store.get_iter(path)
            entry_id = self.model.entries_store[model_iter][0]
            if entry_id:
                projects = self.model.get_projects_tuple_list()
                entry = self.model.get_entry_by_id(entry_id)

                # is_revealed = self.view.revealer.get_reveal_child()
                is_same_entry = self.model.selected_entry_id == entry_id
                if is_same_entry:
                    # Toggle pannel
                    self.view.revealer.toggle()
                else:
                    # Change selected entry
                    self.model.set_selected_entry_id(entry_id)
                    # Fill panel
                    self.view.entry_edit.fill_with_entry(entry, projects)
                    # Show
                    self.view.revealer.show()
            else:
                # Entry panel to default state
                self.view.entry_edit.fill_void()
                # If no entry just hide the panel
                self.view.revealer.hide()

    def on_click_menu_delete(self, widget, path):
        model_iter = self.model.entries_store.get_iter(path)
        entry_id = self.model.entries_store[model_iter][0]
        self.model.delete_entry_by_id(entry_id)
        self.model.fill_store()

    # Simple Entry
    def on_activate_simple_entry(self, entry):
        text_entry = entry.get_text()
        if text_entry:
            self.model.add_simple_entry(text_entry)
            self.model.fill_store()
        entry.set_text("")


def get_entries_controller(application):
    return EntriesController(
        view=EntriesView(application=application, title=APP_WINDOW_TITLE),
        model=EntriesModel(),
    )

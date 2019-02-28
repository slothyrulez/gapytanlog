import logging
logging.getLogger(__name__)

from collections import UserDict

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk

import pendulum

from gapytanlog.utils import TODAY, TODAY_DISPLAY
from gapytanlog.constants import (
    LIMITED_MAX_LENGTH,
    UI_BORDER_WIDTH,
    APP_WINDOW_TITLE,
    REVEAL_DURATION
)


class SimpleEntry(Gtk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_max_length(LIMITED_MAX_LENGTH)
        self.set_property("activates-default", True)


class EntriesCalendarButton(Gtk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_label(TODAY_DISPLAY)
        self.set_tooltip_text("Pick date")
        self.calendar_popover = Gtk.Popover()
        self.calendar = EntriesCalendar()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.add(self.calendar)
        self.calendar_popover.add(vbox)
        self.calendar_popover.set_position(Gtk.PositionType.BOTTOM)


class EntriesCalendar(Gtk.Calendar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mark_entries(self, entries_day_list):
        for entry_day in entries_day_list:
            self.mark_day(entry_day)


class EntryRevealer(Gtk.Revealer):
    REVEAL_DURATION = REVEAL_DURATION

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_reveal_child(False)
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.set_transition_duration(EntryRevealer.REVEAL_DURATION)

    @property
    def shown(self):
        return self.get_reveal_child()

    def toggle(self):
        if self.shown:
            self.hide()
        else:
            self.show()

    def hide(self):
        if self.shown:
            self.set_transition_type(
                Gtk.RevealerTransitionType.SLIDE_RIGHT
            )
            self.set_transition_duration(EntryRevealer.REVEAL_DURATION)
            self.set_reveal_child(False)
            self.set_visible(False)

    def show(self):
        if not self.shown:
            self.set_transition_type(
                Gtk.RevealerTransitionType.SLIDE_LEFT
            )
            self.set_transition_duration(EntryRevealer.REVEAL_DURATION)
            self.set_reveal_child(True)
            self.set_visible(True)


class EntriesHeader(Gtk.HeaderBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(kwargs.get("title", APP_WINDOW_TITLE))
        self.set_show_close_button(True)

        self.header_button_add = Gtk.Button()
        self.header_button_menu = Gtk.Button()

        self.header_button_add.set_tooltip_text("Add entry")
        self.header_button_add.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon(name="zoom-in-symbolic"), Gtk.IconSize.BUTTON
            )
        )

        self.header_button_menu.set_tooltip_text("Menu")
        self.header_button_menu.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon(name="open-menu-symbolic"), Gtk.IconSize.BUTTON
            )
        )

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")
        box.add(self.header_button_menu)

        self.pack_start(self.header_button_add)
        self.pack_end(box)

class EntriesViewColumn(Gtk.TreeViewColumn):
    pass


class EntriesTreeView(Gtk.TreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries_column_data = [
            {"title": "Project", "expand": True},
            {"title": "Task", "expand": True},
            {"title": "Date Time", "expand": True},
        ]

        for idx, column in enumerate(self.entries_column_data, start=1):
            renderer = Gtk.CellRendererText()
            view_column = EntriesViewColumn(column["title"], renderer, text=idx)
            self.append_column(view_column)
            view_column.set_expand(column["expand"])


class EntryEdit(Gtk.ListBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        DOUBLE_PADDING = UI_BORDER_WIDTH * 2

        row = Gtk.ListBoxRow()
        row.props.width_request = 100
        row.props.height_request = 80
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=UI_BORDER_WIDTH)
        label = Gtk.Label(label="Date")
        label.set_halign(Gtk.Align.START)
        self.entry_timestamp_label = Gtk.Label(label="Default")
        self.entry_timestamp_label.set_halign(Gtk.Align.END)
        hbox.pack_start(label, True, True, DOUBLE_PADDING)
        hbox.pack_start(self.entry_timestamp_label, True, True, DOUBLE_PADDING)
        row.add(hbox)
        self.add(row)

        row = Gtk.ListBoxRow()
        row.props.width_request = 100
        row.props.height_request = 80
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=UI_BORDER_WIDTH)
        label = Gtk.Label(label="Project")
        label.set_halign(Gtk.Align.START)
        self.project_combobox = Gtk.ComboBoxText()
        self.project_combobox.set_halign(Gtk.Align.END)
        self.project_combobox.set_valign(Gtk.Align.CENTER)
        hbox.pack_start(label, True, True, DOUBLE_PADDING)
        hbox.pack_start(self.project_combobox, True, True, DOUBLE_PADDING)
        row.add(hbox)
        self.add(row)

        row = Gtk.ListBoxRow()
        row.props.width_request = 100
        row.props.height_request = 80
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=UI_BORDER_WIDTH)
        label = Gtk.Label(label="Task")
        label.set_halign(Gtk.Align.START)
        self.entry_value_label = Gtk.Label(label="Default")
        self.entry_value_label.set_halign(Gtk.Align.END)
        hbox.pack_start(label, True, True, DOUBLE_PADDING)
        hbox.pack_start(self.entry_value_label, True, True, DOUBLE_PADDING)
        row.add(hbox)
        self.add(row)

        row = Gtk.ListBoxRow()
        row.props.width_request = 100
        row.props.height_request = 80
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=UI_BORDER_WIDTH)
        label = Gtk.Label(label="Details")
        label.set_halign(Gtk.Align.START)
        self.entry_detail_value_label = Gtk.Label(label="Default")
        self.entry_detail_value_label.set_halign(Gtk.Align.END)
        hbox.pack_start(label, True, True, DOUBLE_PADDING)
        hbox.pack_start(self.entry_detail_value_label, True, True, DOUBLE_PADDING)
        row.add(hbox)
        self.add(row)

        self.fill_void()
        self.show_all()

    def set_project_data(self):
        pass

    def set_entry_timestamp(self, entry):
        self.entry_timestamp_label.set_label(
            pendulum.instance(entry.modified).to_datetime_string()
        )

    def set_entry_value(self, entry):
        self.entry_value_label.set_label(entry.task or "")

    def set_entry_detail_value(self, entry):
        self.entry_detail_value_label.set_label(entry.task_extended or "")

    def set_project_combobox_value(self, entry, projects):
        self.project_combobox.remove_all()
        for _id, name in projects:
            self.project_combobox.append(str(_id), name.capitalize())
        self.project_combobox.set_active_id(str(entry.project.id))

    def fill_with_entry(self, entry, projects):
        self.set_entry_timestamp(entry)
        self.set_entry_value(entry)
        self.set_entry_detail_value(entry)
        self.set_project_combobox_value(entry, projects)

    def fill_void(self):
        self.entry_timestamp_label.set_label("-----")
        self.entry_value_label.set_label("-----")
        self.entry_detail_value_label.set_label("-----")
        self.project_combobox.remove_all()
        self.project_combobox.append("0", "-----")
        self.project_combobox.set_active_id("0")


class EntriesView(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tree_view = EntriesTreeView()
        self.simple_entry = SimpleEntry()
        self.header = EntriesHeader()
        self.entry_edit = EntryEdit()
        self.date_calendar_button = EntriesCalendarButton()

        # Use header
        self.set_titlebar(self.header)

        self.set_border_width(UI_BORDER_WIDTH)
        self.set_default_size(16 / 10 * 500, 500)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.add(self.grid)
        self.grid.set_row_spacing(UI_BORDER_WIDTH)
        self.grid.set_column_spacing(UI_BORDER_WIDTH)

        date_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=UI_BORDER_WIDTH
        )
        date_box.pack_start(self.date_calendar_button, True, True, 0)

        self.scrolled_entries = Gtk.ScrolledWindow()
        self.scrolled_entries.set_hexpand(True)
        self.scrolled_entries.set_vexpand(True)
        self.scrolled_entries.add(self.tree_view)

        simple_entry_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=UI_BORDER_WIDTH
        )
        label = Gtk.Label(label="Quick Task")
        label.set_justify(Gtk.Justification.LEFT)
        simple_entry_box.pack_start(label, False, True, 0)
        simple_entry_box.pack_end(self.simple_entry, True, True, 0)

        self.revealer = EntryRevealer()
        box_outer = Gtk.Frame()
        box_outer.add(self.entry_edit)
        self.revealer.add(box_outer)

        self.grid.attach(date_box, 0, 0, 2, 1)
        self.grid.attach(self.scrolled_entries, 0, 1, 2, 1)
        self.grid.attach(simple_entry_box, 0, 2, 2, 1)
        self.grid.attach(self.revealer, 3, 0, 2, 3)
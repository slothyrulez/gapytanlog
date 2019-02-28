import logging

logging.getLogger(__name__)

from collections import UserDict

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk

import pendulum

from gapytanlog.utils import TODAY
from gapytanlog.models.database import Project, Entry


class EntriesStore(Gtk.ListStore):
    def __init__(self, *args, **kwargs):
        super().__init__(*(int, str, str, str, *args), **kwargs)


class EntriesModel(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["entries_selected_date"] = TODAY
        self.data["entries_store"] = EntriesStore()
        self.data["selected_entry_id"] = None

    @property
    def entries_selected_date(self):
        return self.get("entries_selected_date")

    @property
    def entries_store(self):
        return self.get("entries_store")

    @property
    def selected_entry_id(self):
        return self.get("selected_entry_id")

    def get_projects_tuple_list(self):
        return list(Project.get_ids_names_iterator())

    def get_entry_by_id(self, entry_id):
        return Entry.get_by_id(entry_id)

    def delete_entry_by_id(self, entry_id):
        Entry.delete_by_id(entry_id)

    def add_simple_entry(self, data):
        Entry.add_simple(data)

    def set_selected_entry_id(self, _id):
        self.update({"selected_entry_id": _id})

    def set_entries_selected_date(self, date):
        self.update({"entries_selected_date": date})

    def get_year_month_entries(self, *, year, month):
        return Entry.days_with_entry_by_year_month(year=year, month=month)

    def get_selected_date_entries(self):
        return list(Entry.get_date_entries_iterator(self.entries_selected_date))

    def get_selected_date_month_year_entries(self):
        return self.get_year_month_entries(
            year=self.entries_selected_date.year, month=self.entries_selected_date.month
        )

    def fill_store(self, clear=True):
        if clear:
            self.entries_store.clear()
        for entry in self.get_selected_date_entries():
            self.entries_store.append(
                [
                    entry.id,
                    entry.project.name.capitalize(),
                    entry.task,
                    pendulum.instance(entry.modified).to_datetime_string(),
                ]
            )

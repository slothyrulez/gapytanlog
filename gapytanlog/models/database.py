import datetime
import logging

logging.getLogger(__name__)

import peewee
import pendulum

from gapytanlog.constants import DATABASE_PATH, DEFAULT_PROJECT_NAME, LIMITED_MAX_LENGTH

database = peewee.SqliteDatabase(DATABASE_PATH)


class BaseModel(peewee.Model):
    """Base model class. All descendants share the same database."""

    class Meta:
        database = database


class Project(BaseModel):
    class Meta:
        table_name = "projects"

    description = peewee.TextField(null=True)
    name = peewee.CharField(max_length=LIMITED_MAX_LENGTH, unique=True)

    @classmethod
    def get_default(kls):
        return kls.select().where(Project.name == DEFAULT_PROJECT_NAME).get()

    @classmethod
    def get_ids_names_iterator(kls):
        return kls.select(Project.id, Project.name).tuples()


class Entry(BaseModel):
    class Meta:
        table_name = "entries"

    task = peewee.CharField(max_length=LIMITED_MAX_LENGTH)
    task_extended = peewee.TextField(null=True)
    created = peewee.DateTimeField(default=datetime.datetime.now)
    modified = peewee.DateTimeField()
    project = peewee.ForeignKeyField(Project, backref="entries")

    # def create(self, *args, **kwargs):
    #     print(args)
    #     print(kwargs)
    #     return super().create(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def get_by_id(kls, _id):
        print("ID ", _id)
        try:
            return kls.select().where(kls.id == _id).get()
        except kls.DoesNotExist:
            return None

    @classmethod
    def add_simple(kls, task_text):
        default_project = Project.get_default()
        return kls.create(**{"task": task_text.strip(), "project": default_project})

    @classmethod
    def get_today_entries_iterator(kls):
        today = datetime.date.today()
        return (
            kls.select()
            .where(
                kls.created.year == today.year,
                kls.created.month == today.month,
                kls.created.day == today.day,
            )
            .order_by(kls.project.name, kls.created)
            .iterator()
        )

    @classmethod
    def get_date_entries_iterator(kls, date):
        return (
            kls.select()
            .where(
                kls.created.year == date.year,
                kls.created.month == date.month,
                kls.created.day == date.day,
            )
            .order_by(kls.project.name, kls.created)
            .iterator()
        )

    @classmethod
    def days_with_entry_by_year_month(kls, *, year, month):
        return (
            kls.select(
                peewee.fn.date_trunc("day", kls.created).alias("day"),
                peewee.fn.count(Entry.id).alias("count"),
            )
            .where(kls.created.year == year, kls.created.month == month)
            .group_by(peewee.fn.date_trunc("day", kls.created))
            .namedtuples()
        )


def create_tables():
    with database:
        database.create_tables([Project, Entry])
        if not Project.select().where(Project.name == DEFAULT_PROJECT_NAME).count():

            Project.create(name=DEFAULT_PROJECT_NAME)


def get_database():
    return database

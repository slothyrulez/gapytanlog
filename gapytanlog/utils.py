import pendulum

from gapytanlog.models.database import Project

TODAY = pendulum.today()

TODAY_DISPLAY = TODAY.to_date_string()


def get_projects_ids_names():
    return [(project.id, project.name) for project in Project.select().iterator()]


def get_today_entries_project_grouped():
    pass

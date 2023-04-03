from queue_api.models import Tasks_TB, tasks_schema
from queue_api import session, engine


def get_tasks():
    tasks = session.query(Tasks_TB).filter_by(status='uploaded')
    return tasks_schema.dump(tasks)

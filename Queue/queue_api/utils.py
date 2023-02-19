from queue_api.models import Tasks_TB, tasks_schema
from queue_api import session, engine
from os import path, mkdir
from sqlalchemy import and_, update

def get_tasks():
    tasks = session.query(Tasks_TB).filter_by(status='uploaded')
    return tasks_schema.dump(tasks)

def update_task(id, email, path, format):
    up = (update(Tasks_TB).where(Tasks_TB.id == id).values(status="processed"))
    conn = engine.connect()
    print(up)
    conn.execute(up)
    conn.commit()
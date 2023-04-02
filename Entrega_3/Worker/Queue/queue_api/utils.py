from queue_api import Base
import sqlalchemy
import marshmallow

class Tasks_TB(Base):
    __tablename__ = 'tasks'
    __table_args__ = dict(schema="compress_schema")
    id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.Identity(start=1, cycle=True), nullable = False, primary_key = True)
    email = sqlalchemy.Column(sqlalchemy.String(100))
    status = sqlalchemy.Column(sqlalchemy.String(50))
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime())
    filename = sqlalchemy.Column(sqlalchemy.String(500))
    path = sqlalchemy.Column(sqlalchemy.String(1000))
    format = sqlalchemy.Column(sqlalchemy.String(50))

class TasksSchema(marshmallow.Schema):
    class Meta:
        fields = ("id", "path", "filename", "email", "format")

tasks_schema = TasksSchema(many = True)root@worker:~/Entrega-1---Sistema-de-Conversi-n-Cloud/Queue/queue_api# 
root@worker:~/Entrega-1---Sistema-de-Conversi-n-Cloud/Queue/queue_api# 
root@worker:~/Entrega-1---Sistema-de-Conversi-n-Cloud/Queue/queue_api# 
root@worker:~/Entrega-1---Sistema-de-Conversi-n-Cloud/Queue/queue_api# ls
__init__.py  models.py  utils.py
root@worker:~/Entrega-1---Sistema-de-Conversi-n-Cloud/Queue/queue_api# cat utils.py
from queue_api.models import Tasks_TB, tasks_schema
from queue_api import session, engine


def get_tasks():
    tasks = session.query(Tasks_TB).filter_by(status='uploaded')
    return tasks_schema.dump(tasks)

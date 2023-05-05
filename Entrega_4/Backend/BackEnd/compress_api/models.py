from compress_api import db, ma

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = dict(schema="compress_schema")
    usuario = db.Column(db.String(200))
    email = db.Column(db.String(100), primary_key = True)
    password = db.Column(db.String(500))
    #libros = db.relationship('Libro', backref = 'usuario', lazy = True)

class Tasks_TB(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = dict(schema="compress_schema")
    id = db.Column(db.String(40), nullable = False, primary_key = True)
    email = db.Column(db.String(100))
    status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime())
    filename = db.Column(db.String(500))
    path = db.Column(db.String(1000))
    format = db.Column(db.String(50))

class TasksSchema(ma.Schema):
    class Meta:
        fields = ("id", "status", "filename", "timestamp", "format")

tasks_schema = TasksSchema(many = True)

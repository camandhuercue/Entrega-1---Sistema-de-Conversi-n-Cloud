from compress_api import db

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = dict(schema="compress_schema")
    usuario = db.Column(db.String(200))
    email = db.Column(db.String(100), primary_key = True)
    password = db.Column(db.String(100))
    #libros = db.relationship('Libro', backref = 'usuario', lazy = True)


#class UsuarioSchema(ma.Schema):
#    class Meta:
#        fields = ("usuario", "email", "password")

#usuario_schema = UsuarioSchema()

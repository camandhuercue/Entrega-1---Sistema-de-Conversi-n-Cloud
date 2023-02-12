from flask import request, current_app, send_from_directory
from flask_restful import Resource
from compress_api import db
from compress_api.models import Usuarios


class RecursoRegistro(Resource):
    def post(self):
        if Usuarios.query.filter_by(email=request.json['email']).first() is not None:
            return {'message': f'El correo({request.json["email"]}) ya está registrado'}, 400

        if request.json['email'] == '' or request.json['password'] == '' or request.json['usuario'] == '':
            return {'message': 'Campos invalidos'}, 400

        nuevo_usuario = Usuarios(
            email = request.json['email'],
            password = request.json['password'],
            usuario = request.json['usuario'],
        )

        #nuevo_usuario.hashear_clave()

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            #access_token = create_access_token(identity = request.json['email'], expires_delta = timedelta(days = 1))
            return {
                'message': f'El correo {request.json["email"]} ha sido registrado',
                'access_token': f'pruebas'
            }

        except:
            return {'message':'Ha ocurrido un error'}, 500

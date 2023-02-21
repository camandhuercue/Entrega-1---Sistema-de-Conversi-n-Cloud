from flask import request, current_app, send_from_directory
from flask_restful import Resource
from compress_api import db
from compress_api.models import Usuarios, Tasks_TB, tasks_schema
from compress_api import utils
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import hashlib
import base64
from os import path, mkdir

class SignUp(Resource):
    def post(self):
        if Usuarios.query.filter_by(email=request.json['email']).first() is not None:
            return {'message': f'El correo({request.json["email"]}) ya está registrado', 'id': 12}, 400

        if request.json['email'] == '' or request.json['password1'] == '' or request.json['password2'] == '' or request.json['usuario'] == '':
            return {'message': f'Campos invalidos', 'id': 15}, 400

        if request.json['password1'] != request.json['password2']:
            return {'message': f'Las Contraseñas no coinciden', 'id': 18}, 400

        passwd_complex = utils.passwd.complex_passwd(request.json['password1'])

        if not passwd_complex['len'] or not passwd_complex['num'] or not passwd_complex['upp'] or not passwd_complex['low'] or not passwd_complex['esp']:
            return {'message': f'Contraseña no cumple', 'id': 23}

        passwd_hash = utils.passwd.hash_passwd(bytes(request.json['password1'], 'utf-8')).decode("utf-8")

        nuevo_usuario = Usuarios(
            email = request.json['email'],
            password = passwd_hash,
            usuario = request.json['usuario'],
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {
                'message': f'El correo {request.json["email"]} ha sido registrado',
                'id': 0
            }

        except Exception as e:
            return {'message': str(e), 'id': 42}, 500

class Login(Resource):
    def post(self):
        Usuario = Usuarios.query.get(request.json['email'])
        Password = request.json['password']
        if Usuario is None or Password is None:
            return {'message': f'Usuario o Contraseña Errada', 'id': 48}, 400
        if not utils.passwd.check_passwd(bytes(request.json['password'], 'utf-8'), bytes(Usuario.password, 'utf-8')):
            return {'message': f'Usuario o Contraseña Errada', 'id': 50}, 400
        try:
            access_token = create_access_token(identity = request.json['email'], expires_delta = timedelta(days = 1))
            return {
                'message': f'Login Exitoso',
                'id': 0,
                'access_token': access_token
            }
        except Exception as e:
            return {'message':str(e), 'id': 59}, 500

class Tasks(Resource):
    @jwt_required()
    def get(self):
        try:
            email = get_jwt_identity()
            task = Tasks_TB.query.filter_by(email=email).first()
            if task is None:
                return {'message': f'No hay registros disponibles', 'id': 69}, 400
            tasks = Tasks_TB.query.filter_by(email=email)
            return tasks_schema.dump(tasks)
        except Exception as e:
            return {'message':str(e), 'id': 80}, 500
    @jwt_required()
    def post(self):
        now = datetime.utcnow()
        Path = '/workspace/files/'
        try:
            email = get_jwt_identity()
            file = base64.decodebytes(request.json['file_content'].encode("ascii"))
            file_hash = hashlib.sha256()
            file_hash.update(file)
            if not path.exists(Path + email):
                mkdir(Path + email + "/")
            file_path = Path + email + "/" + file_hash.hexdigest()
            task = Tasks_TB.query.filter_by(email=email, path=file_path, format=request.json['format']).first()
            if task is not None:
                return {'message': f'Un trabajo para comprimir el archivo con el formato seleccionado ya existe', 'id': 91, 'task_id': task.id}, 400
            with open(file_path, 'wb') as f:
                f.write(file)
            new_task = Tasks_TB(
                email = email,
                status = 'uploaded',
                timestamp = now,
                filename = request.json['filename'],
                format = request.json['format'],
                path = file_path
            )
            db.session.add(new_task)
            db.session.commit()
            return {'message': 'Tarea agregada con éxito', 'id':0}
        except Exception as e:
            return {'message':str(e), 'id': 106}, 500
class Tasks_id(Resource):
    @jwt_required()
    def get(self, id_task):
        try:
            email = get_jwt_identity()
            if id_task is not None:
                task = Tasks_TB.query.filter_by(email=email, id=id_task).first()
                if task is not None:
                    return {'message': task.id, 'id': 0}, 200
                else:
                    return {'message': f'No hay registros disponibles', 'id': 75}, 400
        except Exception as e:
            return {'message':str(e), 'id': 119}, 500
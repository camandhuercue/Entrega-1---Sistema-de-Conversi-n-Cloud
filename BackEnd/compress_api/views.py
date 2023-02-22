from flask import request, current_app, send_from_directory
from flask_restful import Resource
from compress_api import db
from compress_api.models import Usuarios, Tasks_TB, tasks_schema
from compress_api import utils
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
import hashlib
import base64
from os import path, mkdir, remove

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
            if request.json['format'] not in ['ZIP','7Z','BZ2','TGZ','TBZ2']:
                return {'message': f'El formato no es compaible', 'id': 84}, 400
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
                    t = {
                        'id': task.id,
                        'filename': task.filename,
                        'timestamp': task.timestamp.strftime("%d/%m/%Y, %H:%M:%S"),
                        'status': task.status,                      
                        'format': task.format,
                        'internal_id': path.basename(task.path).split('/')[-1]
                    }
                    return {'message': t, 'id': 0}, 200
                else:
                    return {'message': f'No hay registros disponibles', 'id': 124}, 400
        except Exception as e:
            return {'message':str(e), 'id': 126}, 500

    @jwt_required()
    def delete(self, id_task):
        try:
            email = get_jwt_identity()
            if id_task is not None:
                task = Tasks_TB.query.filter_by(email=email, id=id_task).first()
                if task is not None:
                    Tasks_TB.query.filter_by(email=email, id=id_task).delete()
                    db.session.commit()
                    #remove(task.path)
                    file_name = path.basename(task.path).split('/')[-1]
                    if task.format == 'ZIP':
                        ext = '.zip'
                    if task.format == '7Z':
                        ext = '.7z'
                    if task.format == 'TGZ':
                        ext = '.tgz'
                    if task.format == 'TBZ2':
                        ext = '.tbz2'
                    if task.format == 'BZ2':
                        ext = '.bz2'
                    remove('/workspace/files/' + email + '/compress/' + file_name + ext)
                    return {'message': 'La tarea ha sido eliminada', 'id': 0}, 200
                else:
                    return {'message': f'No hay registros disponibles', 'id': 141}, 400
        except Exception as e:
            return {'message':str(e), 'id': 143}, 500

class get_file(Resource):
    @jwt_required()
    def get(self, file_name):
        try:
            email = get_jwt_identity()
            if file_name is not None:
                ext = None
                temp = path.splitext(file_name)
                if len(temp) > 1:
                    ext = temp[1]
                    Path = '/workspace/files/' + email + '/' + temp[0]
                else:
                    Path = '/workspace/files/' + email + '/' + file_name
                task = Tasks_TB.query.filter_by(email=email, path=Path).first()
                if task is not None:
                    if len(temp) > 1:
                        filename = task.filename + '.' + ext
                    else:
                        filename = task.filename
                    if ext is not None and ext != '':
                        if ext == ".zip" or ext == '.7z' or ext == '.bz2' or ext == '.tgz' or ext == '.tbz2':
                            Path = '/workspace/files/' + email + '/compress/' + temp[0] + ext
                            data = utils.file2base.base64file(Path).decode("utf-8")
                        else:
                            if task.status != 'processed':
                                return {'message': f'La tarea no ha sido procesada', 'id': 184}, 400
                            return {'message': f'No existe archivo con esa extensión', 'id': 185}, 400
                    else:
                        data = utils.file2base.base64file(Path).decode("utf-8")
                    return {'message': {'data': data, 'name': filename}, 'id': 0}, 200
                else:
                    return {'message': f'No hay registros disponibles', 'id': 190}, 400
        except Exception as e:
            return {'message':str(e), 'id': 192}, 500
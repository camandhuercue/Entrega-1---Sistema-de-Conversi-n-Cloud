from compress_api import api
from compress_api.views import SignUp, Login, Tasks, Tasks_id, get_file

api.add_resource(SignUp, '/api/auth/signup')
api.add_resource(Login, '/api/auth/login')
api.add_resource(Tasks, '/api/tasks')
api.add_resource(Tasks_id, '/api/tasks/<path:id_task>')
api.add_resource(get_file, '/api/files/<path:file_name>')

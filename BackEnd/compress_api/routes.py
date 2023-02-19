from compress_api import api
from compress_api.views import SignUp, Login, Tasks

api.add_resource(SignUp, '/api/auth/signup')
api.add_resource(Login, '/api/auth/login')
api.add_resource(Tasks, '/api/tasks')

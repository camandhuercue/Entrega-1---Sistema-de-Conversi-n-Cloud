from compress_api import api
from compress_api.views import RecursoRegistro

api.add_resource(RecursoRegistro, '/api/auth/registro')

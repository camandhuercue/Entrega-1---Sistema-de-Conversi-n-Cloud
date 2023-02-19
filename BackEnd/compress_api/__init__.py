from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask.scaffold
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func

db = SQLAlchemy()
api = Api()
jwt = JWTManager()
ma = Marshmallow()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    try:
        app.config.from_pyfile('config.py')
    except:
        print("error")
        exit()
    db.init_app(app)

    import compress_api.models
    with app.app_context():
        db.create_all()

    import compress_api.views
    import compress_api.routes

    api.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    return app

def _endpoint_from_view_func(view_func):
    """Internal helper that returns the default endpoint for a given
    function.  This always is the function name.
    """
    assert view_func is not None, "expected view func if endpoint is not provided."
    return view_func.__name__

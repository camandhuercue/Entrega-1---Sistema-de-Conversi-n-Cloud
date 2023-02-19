'''
Setup of the python package for the API 
'''
from setuptools import setup

setup(
    name='compress_api',
    packages=['compress_api'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'python-dotenv',
        'psycopg2-binary',
        'flask-restful',
        'bcrypt',
        'flask-jwt-extended',
        'flask-marshmallow'
    ],
)

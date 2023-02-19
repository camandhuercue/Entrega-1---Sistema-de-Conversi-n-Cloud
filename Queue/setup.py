'''
Setup of the python package for the API 
'''
from setuptools import setup

setup(
    name='queue_api',
    packages=['queue_api'],
    include_package_data=True,
    install_requires=[
        'celery',
        'redis',
        'SQLAlchemy',
        'marshmallow',
        'psycopg2-binary',
        'zipfile36',
        'py7zr',
        'bz2file',
    ],
)

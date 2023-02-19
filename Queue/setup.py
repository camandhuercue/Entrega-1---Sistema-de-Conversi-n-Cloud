'''
Setup of the python package for the API 
'''
from setuptools import setup

setup(
    include_package_data=True,
    install_requires=[
        'celery',
        'redis',
        'SQLAlchemy'
    ],
)

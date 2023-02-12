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
        'flask-sqlalchemy'
    ],
)

'''
Setup of the python package for the API 
'''
from setuptools import setup

setup(
    name='apirest',
    packages=['apirest'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy'
    ],
)

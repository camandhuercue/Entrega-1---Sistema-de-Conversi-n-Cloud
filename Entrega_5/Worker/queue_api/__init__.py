import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:SuP3r$3cUr#P$$!!@sql.soluciones.cloud:5432/compress_database')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
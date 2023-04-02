import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://compress_user:$$53eer3&777R@172.31.13.57:5432/compress_database')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

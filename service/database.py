import os

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

env_path = '.env'
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_SERVER = os.getenv("DB_SERVER")
SQLALCHEMY_DATABASE_URL = (f"postgresql+psycopg2://"
                           f"{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

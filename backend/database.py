from typing import Iterator
import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
import shutil

DATABASE_URL = "sqlite:///db/database.db"
DATABASE_PATH = "./db/database.db"
DATABASE_PATH_COPY = "./db/database_copy.db"

# For production create user and password as anvironmental variables.
# This should be fetched from env variables in docker file

# SQLALCHEMY_DATABASE_URL = "postgresql://fastapi_db:fastapi_db@db:5432/fastapi_db"
# engine = _sql.create_engine(SQLALCHEMY_DATABASE_URL)

engine = _sql.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declarative.declarative_base()


def backup_db() -> None:
    shutil.copy(DATABASE_PATH, DATABASE_PATH_COPY)


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[_orm.Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

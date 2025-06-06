"""
    src: https://fastapi.tiangolo.com/tutorial/sql-databases/
"""
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
import os.path as op

# SQLALCHEMY_DATABASE_URL = "sqlite:///" + op.abspath(op.join(op.split(__file__)[0], "..", "db.sqlite")) #./db.sqlite"
# # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# class SulciLabBase:
#     id = Column(Integer, primary_key=True, index=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def sulcilab_cli(func):
#     def wrapper_func(*args, **kwargs):
#         Base.metadata.create_all(bind=engine)
#         func(*args, **kwargs)

#     return wrapper_func
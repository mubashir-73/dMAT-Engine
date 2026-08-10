from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.db.database import engine


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.get("/")
def root():
    return {"message": "dMAT API is running"}


# from typing import Annotated
# from fastapi import Depends, FastAPI
# from sqlmodel import Session, SQLModel, select
# from db import engine  # import your engine

# def create_db_and_tables():
#    SQLModel.metadata.create_all(engine)

# def get_session():
#    with Session(engine) as session:
#        yield session

# SessionDep = Annotated[Session, Depends(get_session)]

# app = FastAPI()

# @app.on_event("startup")
# def on_startup():
#    create_db_and_tables()

# @app.get("/heroes/")
# def read_heroes(session: SessionDep):
#   heroes = session.exec(select(Hero)).all()
#    return heroes

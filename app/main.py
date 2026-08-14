from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.api.routes.questions import router
from app.db.database import engine


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()
app.include_router(router)


@app.get("/")
def root():
    return {"message": "dMAT API is running"}


# TODO: Now that schema and api are ready and have been tested except for figure sequence, need to build the ui modelling exactly the backend for testing and displaying the questions

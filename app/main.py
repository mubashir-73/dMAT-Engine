from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.api.routes.questions import router
from app.api.routes.test_sessions import router as test_session_router
from app.db.database import engine


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()
app.include_router(router)

app.include_router(test_session_router)


@app.get("/")
def root():
    return {"message": "dMAT API is running"}


# TODO: Test for latin square test session and calculation working and finally for figure sequence once done I will get to working with frontend
# TODO: Now we build the test session api, for now let's build a test session without timer to show my progress. we will add timer in next build

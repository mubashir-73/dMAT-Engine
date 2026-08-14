from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.test_session import (
    AnswerSubmit,
    TestResultResponse,
    TestSessionCreate,
    TestSessionResponse,
)
from app.services.test_session import (
    create_test_session,
    get_test_result,
    get_test_session,
    save_answer,
    submit_test_session,
)

router = APIRouter(
    prefix="/api/test-sessions",
    tags=["test-sessions"],
)


@router.post(
    "",
    response_model=TestSessionResponse,
    status_code=201,
)
async def create_test_session_route(
    session_data: TestSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_test_session(
        db,
        session_data,
    )


@router.get(
    "/{session_id}",
    response_model=TestSessionResponse,
)
async def get_test_session_route(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_test_session(
        db,
        session_id,
    )


@router.put(
    "/{session_id}/answers/{question_id}",
    response_model=TestSessionResponse,
)
async def save_answer_route(
    session_id: int,
    question_id: int,
    answer: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
):
    return await save_answer(
        db=db,
        session_id=session_id,
        question_id=question_id,
        answer=answer.answer,
    )


@router.post(
    "/{session_id}/submit",
    response_model=TestResultResponse,
)
async def submit_test_session_route(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await submit_test_session(
        db,
        session_id,
    )


@router.get(
    "/{session_id}/result",
    response_model=TestResultResponse,
)
async def get_test_result_route(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_test_result(
        db,
        session_id,
    )

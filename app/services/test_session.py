from copy import deepcopy
from random import sample
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.questionModel import Question
from app.models.testSessionModel import TestSession
from app.schemas.test_session import (
    TestQuestionResponse,
    TestResultResponse,
    TestSessionCreate,
    TestSessionResponse,
)


async def create_test_session(
    db: AsyncSession,
    session_data: TestSessionCreate,
) -> TestSessionResponse:
    if session_data.question_count < 1:
        raise HTTPException(
            status_code=400,
            detail="Question count must be greater than 0",
        )

    # Get questions belonging to the requested module.
    result = await db.execute(
        select(Question.id).where(Question.module_type == session_data.module_type)
    )

    available_question_ids = result.scalars().all()

    if len(available_question_ids) < session_data.question_count:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only {len(available_question_ids)} questions "
                f"are available for module '{session_data.module_type}'"
            ),
        )

    # Randomly select questions for this session.
    selected_question_ids = sample(
        list(available_question_ids),
        session_data.question_count,
    )

    session = TestSession(
        module_type=session_data.module_type,
        status="active",
        question_ids=selected_question_ids,
        answers={},
        total_questions=len(selected_question_ids),
    )

    db.add(session)

    await db.commit()
    await db.refresh(session)

    return await _build_session_response(db, session)


async def get_test_session(
    db: AsyncSession,
    session_id: int,
) -> TestSessionResponse:
    session = await _get_session(db, session_id)

    return await _build_session_response(db, session)


async def save_answer(
    db: AsyncSession,
    session_id: int,
    question_id: int,
    answer: Any,
) -> TestSessionResponse:
    session = await _get_session(db, session_id)

    if session.status != "active":
        raise HTTPException(
            status_code=409,
            detail="Test session is no longer active",
        )

    if question_id not in session.question_ids:
        raise HTTPException(
            status_code=400,
            detail="Question does not belong to this test session",
        )

    # Copy JSONB so SQLAlchemy sees the change.
    answers = deepcopy(session.answers)

    question_key = str(question_id)

    if answer is None:
        # Treat null as clearing the current answer.
        answers.pop(question_key, None)
    else:
        answers[question_key] = answer

    session.answers = answers

    await db.commit()
    await db.refresh(session)

    return await _build_session_response(db, session)


async def submit_test_session(
    db: AsyncSession,
    session_id: int,
) -> TestResultResponse:
    session = await _get_session(db, session_id)

    if session.status != "active":
        raise HTTPException(
            status_code=409,
            detail="Test session has already been submitted",
        )

    questions = await _get_session_questions(
        db,
        session.question_ids,
    )

    score = 0

    for question in questions:
        student_answer = session.answers.get(str(question.id))

        if student_answer is None:
            continue

        if _is_correct(
            student_answer,
            question.solution,
        ):
            score += 1

    session.score = score
    session.status = "submitted"

    await db.commit()
    await db.refresh(session)

    return _build_result_response(session)


async def get_test_result(
    db: AsyncSession,
    session_id: int,
) -> TestResultResponse:
    session = await _get_session(db, session_id)

    if session.status != "submitted":
        raise HTTPException(
            status_code=409,
            detail="Test has not been submitted yet",
        )

    return _build_result_response(session)


async def _get_session(
    db: AsyncSession,
    session_id: int,
) -> TestSession:
    result = await db.execute(select(TestSession).where(TestSession.id == session_id))

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Test session not found",
        )

    return session


async def _get_session_questions(
    db: AsyncSession,
    question_ids: list[int],
) -> list[Question]:
    if not question_ids:
        return []

    result = await db.execute(select(Question).where(Question.id.in_(question_ids)))

    questions_by_id = {question.id: question for question in result.scalars().all()}

    # Preserve the order stored in the session.
    return [
        questions_by_id[question_id]
        for question_id in question_ids
        if question_id in questions_by_id
    ]


async def _build_session_response(
    db: AsyncSession,
    session: TestSession,
) -> TestSessionResponse:
    questions = await _get_session_questions(
        db,
        session.question_ids,
    )

    return TestSessionResponse(
        id=session.id,
        module_type=session.module_type,
        status=session.status,
        questions=[
            TestQuestionResponse.model_validate(question) for question in questions
        ],
        answers=session.answers,
        total_questions=session.total_questions,
        score=session.score,
    )


def _is_correct(
    student_answer: Any,
    solution: dict,
) -> bool:
    """
    Compare a student's answer against the question solution.

    Current MVP behavior:
    - scalar/string answers are compared directly
    - dictionaries are compared structurally
    """

    correct_answer = solution.get("answer")

    if correct_answer is None:
        # Supports solutions such as:
        # {"answers": {"5": "C", "6": "E"}}
        correct_answer = solution.get("answers")

    return student_answer == correct_answer


def _build_result_response(
    session: TestSession,
) -> TestResultResponse:
    total = session.total_questions
    score = session.score or 0

    percentage = round((score / total) * 100, 2) if total > 0 else 0.0

    return TestResultResponse(
        session_id=session.id,
        status=session.status,
        score=score,
        total_questions=total,
        percentage=percentage,
    )

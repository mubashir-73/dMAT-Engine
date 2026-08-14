from typing import Any

from pydantic import BaseModel, ConfigDict


class TestSessionCreate(BaseModel):
    module_type: str
    question_count: int


class AnswerSubmit(BaseModel):
    answer: Any


class TestQuestionResponse(BaseModel):
    id: int
    module_type: str
    difficulty: str
    data: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class TestSessionResponse(BaseModel):
    id: int
    module_type: str
    status: str
    questions: list[TestQuestionResponse]
    answers: dict[str, Any]
    total_questions: int
    score: int | None

    model_config = ConfigDict(from_attributes=True)


class TestResultResponse(BaseModel):
    session_id: int
    status: str
    score: int
    total_questions: int
    percentage: float

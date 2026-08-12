from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.question import AssetResponse, QuestionCreate, QuestionResponse
from app.services.question import create_question, get_question, upload_question_asset

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
)


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=201,
)
async def create_question_route(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_question(db, question)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
)
async def get_question_route(
    question_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_question(db, question_id)


@router.post(
    "/{question_id}/assets",
    response_model=AssetResponse,
    status_code=201,
)
async def upload_question_asset_route(
    question_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await upload_question_asset(
        db,
        question_id,
        file,
    )


# TODO: Perform api testings for assets
# BUG: GET {{baseUrl}}/questions/999999 should return not found 404

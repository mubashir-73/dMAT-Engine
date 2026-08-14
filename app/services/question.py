from copy import deepcopy
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assetModel import Assets
from app.models.questionModel import Question
from app.schemas.question import QuestionCreate

STORAGE_DIR = Path("storage/questions")

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def create_question(
    db: AsyncSession,
    question_data: QuestionCreate,
) -> Question:
    question = Question(
        module_type=question_data.module_type,
        difficulty=question_data.difficulty,
        data=question_data.data,
        solution=question_data.solution,
    )

    db.add(question)
    await db.commit()
    await db.refresh(question)

    return question


async def get_question(
    db: AsyncSession,
    question_id: int,
) -> Question:
    result = await db.execute(select(Question).where(Question.id == question_id))

    question = result.scalar_one_or_none()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    return question


async def upload_question_asset(
    db: AsyncSession,
    question_id: int,
    file: UploadFile,
    role: str,
    position: int,
) -> Assets:
    if position < 1:
        raise HTTPException(
            status_code=400,
            detail="Position must be greater than 0",
        )

    # Get question
    question = await get_question(db, question_id)

    # Validate MIME type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WebP images are allowed",
        )

    # Read file
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5 MB",
        )

    # Validate actual image
    try:
        image = Image.open(BytesIO(contents))
        width, height = image.size
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    # Generate storage path
    extension = _get_extension(file.content_type)
    filename = f"{uuid4().hex}{extension}"

    directory = STORAGE_DIR / str(question_id)
    directory.mkdir(parents=True, exist_ok=True)

    storage_path = directory / filename

    try:
        # Save image
        storage_path.write_bytes(contents)

        # Create asset
        asset = Assets(
            question_id=question_id,
            storage_key=str(storage_path),
            mime_type=file.content_type,
            original_filename=file.filename,
            width=width,
            height=height,
        )

        db.add(asset)

        # Get generated asset ID without committing yet
        await db.flush()

        # Link asset to question.data
        _link_asset(
            question=question,
            role=role,
            position=position,
            asset_id=asset.id,
        )

        # Commit Asset + Question update together
        await db.commit()
        await db.refresh(asset)

        return asset

    except Exception:
        storage_path.unlink(missing_ok=True)
        await db.rollback()
        raise


def _link_asset(
    question: Question,
    role: str,
    position: int,
    asset_id: int,
) -> None:
    data = deepcopy(question.data)

    if role == "sequence":
        items = data.get("sequence")

    elif role == "option":
        items = data.get("options")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported asset role: {role}",
        )

    if not isinstance(items, list):
        raise HTTPException(
            status_code=400,
            detail=f"Question does not contain a valid {role} list",
        )

    for item in items:
        if item.get("position") == position:
            if item.get("asset_id") is not None:
                raise HTTPException(
                    status_code=409,
                    detail=f"{role} position {position} already has an asset",
                )

            item["asset_id"] = asset_id

            # Explicitly assign a new object to JSONB column
            question.data = data
            return

    raise HTTPException(
        status_code=404,
        detail=f"{role} position {position} does not exist",
    )


def _get_extension(mime_type: str) -> str:
    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return extensions[mime_type]

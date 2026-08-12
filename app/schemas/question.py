from pydantic import BaseModel, ConfigDict


class QuestionCreate(BaseModel):
    module_type: str
    difficulty: str
    data: dict
    solution: dict


class QuestionResponse(BaseModel):
    id: int
    module_type: str
    difficulty: str
    data: dict
    solution: dict

    model_config = ConfigDict(from_attributes=True)


class AssetResponse(BaseModel):
    id: int
    storage_key: str
    mime_type: str
    original_filename: str | None
    width: int | None
    height: int | None
    alt_text: str | None

    model_config = ConfigDict(from_attributes=True)

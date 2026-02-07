from pydantic import BaseModel, Field


class UserCreateDto(BaseModel):
    name: str = Field(..., min_length=1)

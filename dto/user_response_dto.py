from pydantic import BaseModel


class UserResponseDto(BaseModel):
    id: int
    name: str
    api_key: str


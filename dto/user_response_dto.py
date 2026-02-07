from pydantic import BaseModel


class UserResponseDto(BaseModel):
    name: str
    api_key: str

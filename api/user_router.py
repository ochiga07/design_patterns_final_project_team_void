from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies.user_dependencies import get_user_service
from dto.user_create_dto import UserCreateDto
from dto.user_response_dto import UserResponseDto
from service.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("")
def create_user(
    user_dto: UserCreateDto,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponseDto:
    return user_service.create_user(user_dto)

@user_router.get("", response_model=list[UserResponseDto])
def get_users(user_service: Annotated[UserService,
    Depends(get_user_service)]) -> list[UserResponseDto]:
    return user_service.get_all_users()

@user_router.get("/{user_id}", response_model=UserResponseDto)
def get_user(user_id: int, user_service:
    Annotated[UserService, Depends(get_user_service)]) -> UserResponseDto:
    return user_service.get_user(user_id)

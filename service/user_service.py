from dto.user_create_dto import UserCreateDto
from dto.user_response_dto import UserResponseDto
from repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def create_user(self, user_dto: UserCreateDto) -> UserResponseDto:
        user = self.user_repo.create_user(user_dto.name)
        return UserResponseDto(name=user.name, api_key=user.api_key)

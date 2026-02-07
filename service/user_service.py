from dto.user_create_dto import UserCreateDto
from dto.user_response_dto import UserResponseDto
from repository.user_repository import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def create_user(self, user_dto: UserCreateDto) -> UserResponseDto:
        user = self.user_repo.create_user(user_dto.name)
        return UserResponseDto(id=user.id, name=user.name, api_key=user.api_key)

    def get_user(self, user_id: int) -> UserResponseDto:
        user = self.user_repo.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")
        return UserResponseDto(id=user.id, name=user.name, api_key=user.api_key)

    def get_all_users(self) -> list[UserResponseDto]:
        users = self.user_repo.get_all_users()
        return [UserResponseDto(id=u.id, name=u.name, api_key=u.api_key) for u in users]
"""Mapper between User entities and API models."""

from domain.entities.users import User, Department
from driving.api.users.models.requests import CreateUserRequest, UpdateUserRequest
from driving.api.users.models.responses import UserResponse, DepartmentResponse


class UsersAPIMapper:
    """Maps between User domain entities and API request/response models."""

    def entity_to_response(self, entity: User) -> UserResponse:
        """Convert User entity to UserResponse."""
        return UserResponse(
            id=entity.id,
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            departments=[
                DepartmentResponse(id=dept.id, name=dept.name)
                for dept in entity.departments
            ],
        )

    def request_to_entity(self, request: CreateUserRequest) -> User:
        """Convert CreateUserRequest to User entity."""
        return User(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            is_active=request.is_active,
            departments=[
                Department(name=dept_name)
                for dept_name in request.department_names
            ],
        )

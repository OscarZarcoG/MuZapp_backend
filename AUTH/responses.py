# AUTH/responses.py
from rest_framework import status
from core.responses import BaseSuccessResponse


class UserCreatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="User created successfully", data=data)
        self.status_code = status.HTTP_201_CREATED


class UserUpdatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="User updated successfully", data=data)
        self.status_code = status.HTTP_200_OK


class UserDeletedSuccess(BaseSuccessResponse):
    def __init__(self):
        super().__init__(message="User deleted successfully")
        self.status_code = status.HTTP_204_NO_CONTENT


class UserLoginSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="User logged in successfully", data=data)
        self.status_code = status.HTTP_200_OK


class UserLogoutSuccess(BaseSuccessResponse):
    def __init__(self):
        super().__init__(message="User logged out successfully")
        self.status_code = status.HTTP_200_OK
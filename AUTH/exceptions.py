# AUTH/exceptions.py
from core.exceptions import BaseCustomException
from rest_framework import status


class PasswordMismatch(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Las contraseñas no coinciden.'
    default_code = 'password_mismatch'


class PasswordRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La contraseña es requerida.'
    default_code = 'password_required'


class UsernameRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El nombre de usuario es requerido.'
    default_code = 'username_required'


class InvalidCredentials(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Credenciales inválidas.'
    default_code = 'invalid_credentials'


class SessionExpired(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Sesión expirada.'
    default_code = 'session_expired'


class InvalidToken(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token inválido.'
    default_code = 'invalid_token'


class TokenExpired(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token expirado.'
    default_code = 'token_expired'


class PermissionDenied(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'No tienes permiso para realizar esta acción.'
    default_code = 'permission_denied'


class UserDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El usuario no existe...'
    default_code = 'user_not_found'


class UserAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El usuario ya existe.'
    default_code = 'user_already_exists'

class ProfileDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El perfil no existe.'
    default_code = 'profile_not_found'
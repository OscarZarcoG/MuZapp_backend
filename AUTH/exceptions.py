# AUTH/exceptions.py
from core.exceptions import BaseAPIException 
from rest_framework import status

class PasswordMismatch(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Las contraseñas no coinciden.'
    default_code = 'password_mismatch'
    error_type = 'password_error' 

class PasswordRequired(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La contraseña es requerida.'
    default_code = 'password_required'
    error_type = 'password_error'

class UsernameRequired(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El nombre de usuario es requerido.'
    default_code = 'username_required'
    error_type = 'username_error'

class InvalidCredentials(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Credenciales inválidas.'
    default_code = 'invalid_credentials'
    error_type = 'authentication_error'

class SessionExpired(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Sesión expirada.'
    default_code = 'session_expired'
    error_type = 'authentication_error'

class InvalidToken(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token inválido.'
    default_code = 'invalid_token'
    error_type = 'authentication_error'

class TokenExpired(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token expirado.'
    default_code = 'token_expired'
    error_type = 'authentication_error'

class PermissionDenied(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'No tienes permiso para realizar esta acción.'
    default_code = 'permission_denied'
    error_type = 'permission_error'

class UserDoesNotExist(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El usuario no existe...'
    default_code = 'user_not_found'
    error_type = 'not_found_error'

class UserAlreadyExists(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El usuario ya existe.'
    default_code = 'user_already_exists'
    error_type = 'conflict_error'

class ProfileDoesNotExist(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El perfil no existe.'
    default_code = 'profile_not_found'
    error_type = 'not_found_error'
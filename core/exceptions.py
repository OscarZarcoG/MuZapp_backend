# core/exceptions.py
from rest_framework.exceptions import APIException
from rest_framework import status

class BaseCustomException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Error desconocido'

    def __init__(self, detail=None, status_code=None, code=None):
        self.detail = detail or self.default_detail
        if status_code:
            self.status_code = status_code
        self.code = code or self.default_code
        super().__init__(self.detail)

    def __str__(self):
        return str(self.detail)


class ValidationError(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error de validación'
    default_code = 'validation_error'


class NotFound(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso no encontrado'
    default_code = 'not_found'


class ObjectAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El objeto ya existe.'
    default_code = 'already_exists'


class InternalServerError(BaseCustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Error interno del servidor'
    default_code = 'server_error'


class DatabaseError(BaseCustomException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Error de base de datos'
    default_code = 'database_error'


class UnknownError(BaseCustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Error desconocido'
    default_code = 'unknown_error'


class PermissionDenied(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN  # 403
    default_detail = 'No tiene permiso para esta acción'
    default_code = 'permission_denied'


class AuthenticationFailed(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED  # 401
    default_detail = 'Autenticación fallida'
    default_code = 'authentication_failed'
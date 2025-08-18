# core/exceptions.py
from rest_framework.exceptions import APIException
from rest_framework import status
from typing import Any, Dict, Optional

class BaseAPIException(APIException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = 'Ha ocurrido un error inesperado'
    default_code: str = 'error'
    error_type: str = 'base_api_error'
    
    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        self.meta = meta or {}
        super().__init__(detail=self.detail, code=self.code)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.detail} (code: {self.code})"

    def get_full_details(self) -> Dict[str, Any]:
        return {
            'type': self.error_type,
            'code': self.code,
            'detail': self.detail,
            'status': self.status_code,
            'meta': self.meta
        }

class ValidationError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Los datos proporcionados no son válidos'
    default_code = 'validation_error'
    error_type = 'validation_error'

    def __init__(
        self,
        detail: Optional[str] = None,
        code: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        field_errors: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(detail, code, meta)
        self.field_errors = field_errors or {}

    def get_full_details(self) -> Dict[str, Any]:
        base_details = super().get_full_details()
        if self.field_errors:
            base_details['fields'] = self.field_errors
        return base_details

class NotFoundError(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El recurso solicitado no fue encontrado'
    default_code = 'not_found'
    error_type = 'not_found_error'

class ConflictError(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflicto con el estado actual del recurso'
    default_code = 'conflict'
    error_type = 'conflict_error'

class ObjectAlreadyExistsError(ConflictError):
    default_detail = 'El recurso que intentas crear ya existe'
    default_code = 'already_exists'
    error_type = 'already_exists_error'

class AuthenticationError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Credenciales de autenticación no válidas'
    default_code = 'authentication_failed'
    error_type = 'authentication_error'

class PermissionDeniedError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'No tienes permiso para realizar esta acción'
    default_code = 'permission_denied'
    error_type = 'permission_error'

class ServiceUnavailableError(BaseAPIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'El servicio no está disponible temporalmente'
    default_code = 'service_unavailable'
    error_type = 'service_unavailable_error'

class DatabaseError(ServiceUnavailableError):
    default_detail = 'Error en la operación con la base de datos'
    default_code = 'database_error'
    error_type = 'database_error'

class BusinessRuleError(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Violación de regla de negocio'
    default_code = 'business_rule_violation'
    error_type = 'business_rule_error'
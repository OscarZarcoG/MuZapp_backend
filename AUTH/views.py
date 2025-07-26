# AUTH/views.py
from core.exceptions import DatabaseError, BaseCustomException, AuthenticationFailed, InternalServerError
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .exceptions import (
    InvalidCredentials, UsernameRequired,
    PasswordRequired, UserAlreadyExists
)
from .responses import (
    UserCreatedSuccess, UserLoginSuccess, UserLogoutSuccess
)
from .serializers import UserSerializer


class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @staticmethod
    def post(request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username:
            raise UsernameRequired()
        if not password:
            raise PasswordRequired()

        try:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)

                serializer = UserSerializer(user)
                response_data = serializer.data
                response_data['token'] = token.key


                return UserLoginSuccess(data=response_data).to_response()
            else:
                raise InvalidCredentials()
        except BaseCustomException as e:
            raise e
        except Exception:
            raise DatabaseError("Error en el login")


class UserLogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        try:
            request.user.auth_token.delete()
            logout(request)
            return UserLogoutSuccess().to_response()
        except Exception:
            raise DatabaseError()


class UserSignUpView(APIView):
    authentication_classes = []
    permission_classes = []

    @staticmethod
    def post(request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()

                token, created = Token.objects.get_or_create(user=user)

                response_data = serializer.data
                response_data['token'] = token.key

                return UserCreatedSuccess(data=response_data).to_response()
            errors = serializer.errors
            if 'username' in errors and 'This field is required' in str(errors['username']):
                raise UsernameRequired()
            if 'password' in errors and 'This field is required' in str(errors['password']):
                raise PasswordRequired()

            raise AuthenticationFailed()
        except UserAlreadyExists:
            raise UserAlreadyExists()
        except BaseCustomException as e:
            raise e
        except Exception:
            raise InternalServerError()
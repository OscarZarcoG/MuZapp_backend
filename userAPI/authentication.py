# userAPI/authentication.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .exceptions import InvalidCredentials, UserDoesNotExist


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None

        if not password:
            return None

        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
            else:
                raise InvalidCredentials()

        except UserModel.DoesNotExist:
            raise UserDoesNotExist()

        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(Q(username=username) | Q(email=username)).first()
            if user and user.check_password(password):
                return user
            else:
                raise InvalidCredentials()
# AUTH/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from .models import UserCustom
from .serializers import UserCustomSerializer
from .exceptions import (
    PasswordMismatch, PasswordRequired, UsernameRequired,
    InvalidCredentials, UserDoesNotExist, UserAlreadyExists,
    PermissionDenied
)
from core.exceptions import ValidationError, NotFoundError


class UserCustomViewSet(viewsets.ModelViewSet):
    queryset = UserCustom.objects.all()
    serializer_class = UserCustomSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'register', 'login']:
            permission_classes = [AllowAny]
        elif self.action in ['me', 'update_profile', 'logout', 'change_password', 'users_by_role']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        
        if username and UserCustom.objects.filter(username=username).exists():
            raise UserAlreadyExists(detail=f'El nombre de usuario "{username}" ya está en uso')
        
        if email and UserCustom.objects.filter(email=email).exists():
            raise UserAlreadyExists(detail=f'El email "{email}" ya está registrado')
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserCustomSerializer(user).data,
                'token': token.key,
                'message': 'Usuario registrado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'detail': 'Los datos proporcionados no son válidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username:
            raise UsernameRequired()
        if not password:
            raise PasswordRequired()
        
        user = None
        if '@' in username:
            try:
                user_obj = UserCustom.objects.get(email=username, is_active=True)
                user = authenticate(request, username=user_obj.username, password=password)
            except UserCustom.DoesNotExist:
                raise UserDoesNotExist()
        else:
            try:
                user_obj = UserCustom.objects.get(username=username, is_active=True)
                user = authenticate(request, username=username, password=password)
            except UserCustom.DoesNotExist:
                raise UserDoesNotExist()
        
        if not user:
            raise InvalidCredentials()
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserCustomSerializer(user).data,
            'token': token.key,
            'message': 'Login exitoso'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(
                detail='Error al cerrar sesión',
                meta={'error_details': str(e)}
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Perfil actualizado exitosamente'
            })
        
        raise ValidationError(
            detail='Los datos proporcionados no son válidos',
            field_errors=serializer.errors
        )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password:
            raise PasswordRequired(detail='La contraseña actual es requerida')
        if not new_password:
            raise PasswordRequired(detail='La nueva contraseña es requerida')
        
        if not check_password(old_password, request.user.password):
            raise PasswordMismatch(detail='La contraseña actual es incorrecta')
        
        request.user.set_password(new_password)
        request.user.save()
        
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        token = Token.objects.create(user=request.user)
        
        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'token': token.key
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def users_by_role(self, request):
        if request.user.role not in ['admin', 'root']:
            raise PermissionDenied()
        
        role = request.query_params.get('role')
        if role:
            users = UserCustom.objects.filter(role=role, is_active=True)
        else:
            users = UserCustom.objects.filter(is_active=True)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    
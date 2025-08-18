# AUTH/tests.py
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import json
from datetime import date, datetime
from unittest.mock import patch, MagicMock

from .models import UserCustom
from .serializers import UserCustomSerializer
from .exceptions import (
    PasswordMismatch, PasswordRequired, UsernameRequired,
    InvalidCredentials, UserDoesNotExist, UserAlreadyExists,
    PermissionDenied
)
from core.exceptions import ValidationError, NotFoundError

User = get_user_model()


class UserCustomModelTest(TestCase):
    """Tests unitarios para el modelo UserCustom"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'birthday': date(1990, 1, 1),
            'gender': 'male',
            'role': 'client'
        }
    
    def test_create_user_success(self):
        """Test crear usuario exitosamente"""
        user = UserCustom.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password='testpass123',
            **{k: v for k, v in self.user_data.items() if k not in ['username', 'email']}
        )
        
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.role, 'client')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser_success(self):
        """Test crear superusuario exitosamente"""
        user = UserCustom.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(user.username, 'admin')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_username_unique_constraint(self):
        """Test que el username debe ser único"""
        UserCustom.objects.create_user(
            username='testuser',
            email='test1@example.com',
            password='pass123'
        )
        
        with self.assertRaises(IntegrityError):
            UserCustom.objects.create_user(
                username='testuser',
                email='test2@example.com',
                password='pass123'
            )
    
    def test_phone_unique_constraint(self):
        """Test que el teléfono debe ser único"""
        UserCustom.objects.create_user(
            username='user1',
            email='test1@example.com',
            phone='+1234567890',
            password='pass123'
        )
        
        with self.assertRaises(IntegrityError):
            UserCustom.objects.create_user(
                username='user2',
                email='test2@example.com',
                phone='+1234567890',
                password='pass123'
            )
    
    def test_str_method(self):
        """Test método __str__ del modelo"""
        user = UserCustom.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='pass123'
        )
        
        expected_str = "Test User (testuser)"
        self.assertEqual(str(user), expected_str)
    
    def test_role_choices(self):
        """Test que los roles están limitados a las opciones válidas"""
        valid_roles = ['root', 'admin', 'client']
        
        for i, role in enumerate(valid_roles):
            user = UserCustom.objects.create_user(
                username=f'user_{role}',
                email=f'{role}@example.com',
                phone=f'+123456789{i}',
                role=role,
                password='pass123'
            )
            self.assertEqual(user.role, role)
    
    def test_gender_choices(self):
        """Test que los géneros están limitados a las opciones válidas"""
        valid_genders = ['male', 'female', 'other']
        
        for i, gender in enumerate(valid_genders):
            user = UserCustom.objects.create_user(
                username=f'user_{gender}',
                email=f'{gender}@example.com',
                phone=f'+987654321{i}',
                gender=gender,
                password='pass123'
            )
            self.assertEqual(user.gender, gender)


class UserCustomSerializerTest(TestCase):
    """Tests unitarios para UserCustomSerializer"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '+1234567890',
            'birthday': '1990-01-01',
            'gender': 'male',
            'role': 'client'
        }
    
    def test_serializer_create_success(self):
        """Test crear usuario a través del serializer"""
        serializer = UserCustomSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, self.valid_data['username'])
        self.assertTrue(user.check_password(self.valid_data['password']))
        self.assertEqual(user.role, 'client')
    
    def test_serializer_password_write_only(self):
        """Test que la contraseña es write-only"""
        user = UserCustom.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        serializer = UserCustomSerializer(user)
        self.assertNotIn('password', serializer.data)
    
    def test_serializer_update_password(self):
        """Test actualizar contraseña a través del serializer"""
        user = UserCustom.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpass123'
        )
        
        update_data = {'password': 'newpass123'}
        serializer = UserCustomSerializer(user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertTrue(updated_user.check_password('newpass123'))
        self.assertFalse(updated_user.check_password('oldpass123'))
    
    def test_serializer_readonly_fields(self):
        """Test que los campos readonly no se pueden modificar"""
        user = UserCustom.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        original_created_at = user.created_at
        
        update_data = {
            'created_at': '2020-01-01T00:00:00Z',
            'updated_at': '2020-01-01T00:00:00Z'
        }
        
        serializer = UserCustomSerializer(user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.created_at, original_created_at)


class UserCustomViewSetTest(APITestCase):
    """Tests unitarios para UserCustomViewSet"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        
        # Crear usuarios de prueba
        self.admin_user = UserCustom.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin',
            first_name='Admin',
            last_name='User',
            phone='+1111111111'
        )
        
        self.client_user = UserCustom.objects.create_user(
            username='client',
            email='client@example.com',
            password='clientpass123',
            role='client',
            first_name='Client',
            last_name='User',
            phone='+2222222222'
        )
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.client_token = Token.objects.create(user=self.client_user)
        
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.logout_url = reverse('auth-logout')
        self.me_url = reverse('auth-me')
    
    def test_register_success(self):
        """Test registro exitoso de usuario"""
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'phone': '+3333333333'
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Verificar que el usuario fue creado
        user = UserCustom.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.role, 'client')  # rol por defecto
    
    def test_register_duplicate_username(self):
        """Test registro con username duplicado"""
        data = {
            'username': 'admin',  # username ya existe
            'email': 'newemail@example.com',
            'password': 'newpass123',
            'phone': '+4444444444'
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
    
    def test_login_success(self):
        """Test login exitoso"""
        data = {
            'username': 'admin',
            'password': 'adminpass123'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        data = {
            'username': 'admin',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
    
    def test_logout_success(self):
        """Test logout exitoso"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el token fue eliminado
        self.assertFalse(Token.objects.filter(key=self.admin_token.key).exists())
    
    def test_me_authenticated(self):
        """Test obtener perfil del usuario autenticado"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'admin')
    
    def test_me_unauthenticated(self):
        """Test obtener perfil sin autenticación"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_success(self):
        """Test actualizar perfil exitosamente"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.client_token.key}')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(reverse('auth-update-profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.first_name, 'Updated')
        self.assertEqual(self.client_user.last_name, 'Name')
    
    def test_change_password_success(self):
        """Test cambiar contraseña exitosamente"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.client_token.key}')
        
        data = {
            'old_password': 'clientpass123',
            'new_password': 'newclientpass123'
        }
        
        response = self.client.post(reverse('auth-change-password'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la contraseña cambió
        self.client_user.refresh_from_db()
        self.assertTrue(self.client_user.check_password('newclientpass123'))
    
    def test_change_password_wrong_old_password(self):
        """Test cambiar contraseña con contraseña anterior incorrecta"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.client_token.key}')
        
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newclientpass123'
        }
        
        response = self.client.post(reverse('auth-change-password'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_users_by_role_admin_access(self):
        """Test que admin puede acceder a usuarios por rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        response = self.client.get(reverse('auth-users-by-role'), {'role': 'client'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'client')
    
    def test_users_by_role_client_denied(self):
        """Test que client no puede acceder a usuarios por rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.client_token.key}')
        
        response = self.client.get(reverse('auth-users-by-role'), {'role': 'client'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticationIntegrationTest(APITestCase):
    """Tests de integración para el sistema completo de autenticación"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.client = APIClient()
    
    def test_complete_user_lifecycle(self):
        """Test del ciclo completo de vida de un usuario"""
        # 1. Registro
        register_data = {
            'username': 'lifecycle_user',
            'first_name': 'Lifecycle',
            'last_name': 'User',
            'email': 'lifecycle@example.com',
            'password': 'lifecyclepass123',
            'phone': '+5555555555'
        }
        
        register_response = self.client.post(reverse('auth-register'), register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        token = register_response.data['token']
        
        # 2. Verificar perfil
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        me_response = self.client.get(reverse('auth-me'))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], 'lifecycle_user')
        
        # 3. Actualizar perfil
        update_data = {
            'first_name': 'Updated Lifecycle',
            'birthday': '1995-05-15'
        }
        update_response = self.client.patch(reverse('auth-update-profile'), update_data)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 4. Cambiar contraseña
        password_data = {
            'old_password': 'lifecyclepass123',
            'new_password': 'newlifecyclepass123'
        }
        password_response = self.client.post(reverse('auth-change-password'), password_data)
        self.assertEqual(password_response.status_code, status.HTTP_200_OK)
        
        # Actualizar token después del cambio de contraseña
        new_token = password_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {new_token}')
        
        # 5. Logout
        logout_response = self.client.post(reverse('auth-logout'))
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Limpiar credenciales después del logout
        self.client.credentials()
        
        # 6. Login con nueva contraseña
        login_data = {
            'username': 'lifecycle_user',
            'password': 'newlifecyclepass123'
        }
        login_response = self.client.post(reverse('auth-login'), login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_response.data)
    
    def test_permission_system_integration(self):
        """Test integración del sistema de permisos"""
        # Crear usuarios con diferentes roles
        root_user = UserCustom.objects.create_user(
            username='root_user',
            email='root@example.com',
            password='rootpass123',
            role='root',
            phone='+6666666666'
        )
        
        admin_user = UserCustom.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='adminpass123',
            role='admin',
            phone='+7777777777'
        )
        
        client_user = UserCustom.objects.create_user(
            username='client_user',
            email='client@example.com',
            password='clientpass123',
            role='client',
            phone='+8888888888'
        )
        
        # Test acceso de root
        root_token = Token.objects.create(user=root_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {root_token.key}')
        
        response = self.client.get(reverse('auth-users-by-role'), {'role': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test acceso de admin
        admin_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        response = self.client.get(reverse('auth-users-by-role'), {'role': 'client'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test acceso denegado para client
        client_token = Token.objects.create(user=client_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {client_token.key}')
        
        response = self.client.get(reverse('auth-users-by-role'), {'role': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_error_handling_integration(self):
        """Test manejo integrado de errores"""
        # Test registro con datos duplicados
        UserCustom.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='pass123',
            phone='+9999999999'
        )
        
        # Intentar registrar con username duplicado
        duplicate_data = {
            'username': 'existing_user',
            'email': 'new@example.com',
            'password': 'pass123',
            'phone': '+1010101010'
        }
        
        response = self.client.post(reverse('auth-register'), duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        
        # Test login con usuario inactivo
        inactive_user = UserCustom.objects.create_user(
            username='inactive_user',
            email='inactive@example.com',
            password='pass123',
            phone='+1111111110',
            is_active=False
        )
        
        login_data = {
            'username': 'inactive_user',
            'password': 'pass123'
        }
        
        response = self.client.post(reverse('auth-login'), login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)


class AuthExceptionsTest(TestCase):
    """Tests para las excepciones personalizadas de AUTH"""
    
    def test_password_mismatch_exception(self):
        """Test excepción PasswordMismatch"""
        exception = PasswordMismatch()
        self.assertEqual(exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(exception.default_detail, 'Las contraseñas no coinciden.')
        self.assertEqual(exception.error_type, 'password_error')
    
    def test_invalid_credentials_exception(self):
        """Test excepción InvalidCredentials"""
        exception = InvalidCredentials()
        self.assertEqual(exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(exception.default_detail, 'Credenciales inválidas.')
        self.assertEqual(exception.error_type, 'authentication_error')
    
    def test_permission_denied_exception(self):
        """Test excepción PermissionDenied"""
        exception = PermissionDenied()
        self.assertEqual(exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(exception.default_detail, 'No tienes permiso para realizar esta acción.')
    
    def test_custom_exception_details(self):
        """Test detalles personalizados en excepciones"""
        custom_detail = "Mensaje personalizado"
        exception = PasswordMismatch(detail=custom_detail)
        self.assertEqual(str(exception.detail), custom_detail)


class AuthPerformanceTest(TransactionTestCase):
    """Tests de rendimiento para operaciones críticas"""
    
    def test_bulk_user_creation_performance(self):
        """Test rendimiento en creación masiva de usuarios"""
        import time
        
        start_time = time.time()
        
        users_data = []
        for i in range(100):
            users_data.append(UserCustom(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                first_name=f'User',
                last_name=f'{i}',
                phone=f'+123456{i:04d}',
                role='client'
            ))
        
        UserCustom.objects.bulk_create(users_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verificar que la creación masiva sea eficiente (menos de 1 segundo)
        self.assertLess(execution_time, 1.0)
        
        # Verificar que todos los usuarios fueron creados
        self.assertEqual(UserCustom.objects.count(), 100)
    
    def test_query_optimization(self):
        """Test optimización de consultas"""
        # Crear usuarios con relaciones
        for i in range(10):
            user = UserCustom.objects.create_user(
                username=f'query_user_{i}',
                email=f'query_{i}@example.com',
                password='pass123',
                phone=f'+987654{i:04d}'
            )
        
        # Test consulta optimizada con select_related
        with self.assertNumQueries(1):
            users = list(UserCustom.objects.select_related().all()[:5])
            for user in users:
                # Acceder a campos que normalmente causarían queries adicionales
                _ = user.username
                _ = user.email
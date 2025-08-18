# AUTH/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserCustomViewSet

router = DefaultRouter()
router.register(r'users', UserCustomViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Endpoints específicos de autenticación
    path('auth/register/', UserCustomViewSet.as_view({'post': 'register'}), name='auth-register'),
    path('auth/login/', UserCustomViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/logout/', UserCustomViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('auth/me/', UserCustomViewSet.as_view({'get': 'me'}), name='auth-me'),
    path('auth/update-profile/', UserCustomViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='auth-update-profile'),
    path('auth/change-password/', UserCustomViewSet.as_view({'post': 'change_password'}), name='auth-change-password'),
    path('auth/users-by-role/', UserCustomViewSet.as_view({'get': 'users_by_role'}), name='auth-users-by-role'),
]
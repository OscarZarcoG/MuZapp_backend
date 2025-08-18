# AUTH/urls.py
from django.urls import path
from .views import UserCustomViewSet

urlpatterns = [
    path('auth/register/', UserCustomViewSet.as_view({'post': 'register'}), name='auth-register'),
    path('auth/login/', UserCustomViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/logout/', UserCustomViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('auth/me/', UserCustomViewSet.as_view({'get': 'me'}), name='auth-me'),
    path('auth/update-profile/', UserCustomViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'}), name='auth-update-profile'),
    path('auth/change-password/', UserCustomViewSet.as_view({'post': 'change_password'}), name='auth-change-password'),
    path('auth/users-by-role/', UserCustomViewSet.as_view({'get': 'users_by_role'}), name='auth-users-by-role'),
    
    path('auth/', UserCustomViewSet.as_view({'get': 'list'}), name='auth-list'),
    path('auth/<int:pk>/', UserCustomViewSet.as_view({
        'get': 'retrieve',
        'put': 'update', 
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='auth-detail'),
    
    path('auth/<int:pk>/change-user-role/', UserCustomViewSet.as_view({'patch': 'change_user_role'}), name='auth-change-user-role'),
    path('auth/<int:pk>/hard-delete/', UserCustomViewSet.as_view({'delete': 'hard_delete_user'}), name='auth-hard-delete'),
    path('auth/<int:pk>/restore/', UserCustomViewSet.as_view({'patch': 'restore_user'}), name='auth-restore'),
]
# userAPI/urls.py
from django.urls import path
from .views import UserSignUpView, UserLoginView, UserLogoutView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('signup/', UserSignUpView.as_view(), name='user-create'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]
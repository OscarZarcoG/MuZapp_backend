# GIGS/AUDIO/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AudioEquipmentViewSet

router = DefaultRouter()
router.register(r'equipment', AudioEquipmentViewSet, basename='audioequipment')

urlpatterns = [
    path('', include(router.urls)),
]
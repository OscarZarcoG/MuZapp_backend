# GIGS/CATERING/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CateringViewSet

router = DefaultRouter()
router.register(r'requests', CateringViewSet, basename='catering')

urlpatterns = [
    path('', include(router.urls)),
]
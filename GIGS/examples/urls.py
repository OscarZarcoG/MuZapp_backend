from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookingEventViewSet, ContractSignatureViewSet,
    EventPhotoViewSet, VenueTemplateViewSet,
    AudioTemplateViewSet, ContractTemplateViewSet
)

app_name = 'events'

router = DefaultRouter()
router.register(r'events', BookingEventViewSet, basename='bookingevent')
router.register(r'signatures', ContractSignatureViewSet, basename='contractsignature')
router.register(r'photos', EventPhotoViewSet, basename='eventphoto')
router.register(r'venue-templates', VenueTemplateViewSet, basename='venuetemplate')
router.register(r'audio-templates', AudioTemplateViewSet, basename='audiotemplate')
router.register(r'contract-templates', ContractTemplateViewSet, basename='contracttemplate')

urlpatterns = [
    path('api/', include(router.urls)),
]
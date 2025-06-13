from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import (
    BookingEvent, ContractSignature, EventPhoto,
    VenueTemplate, AudioTemplate, ContractTemplate
)
from .serializers import (
    BookingEventSerializer, ContractSignatureSerializer,
    EventPhotoSerializer, VenueTemplateSerializer,
    AudioTemplateSerializer, ContractTemplateSerializer
)


class BookingEventViewSet(viewsets.ModelViewSet):
    queryset = BookingEvent.objects.all()
    serializer_class = BookingEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'event_type', 'date', 'assigned_to']
    search_fields = ['title', 'client_name', 'celebrant_name', 'venue_name']
    ordering_fields = ['date', 'created_at', 'start_time']
    ordering = ['-date', '-start_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Admins ven todo, otros solo lo asignado o creado por ellos
        if not user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to=user) | Q(created_by=user)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard con estadísticas"""
        queryset = self.get_queryset()

        stats = {
            'total_events': queryset.count(),
            'upcoming_events': queryset.filter(is_upcoming=True).count(),
            'today_events': queryset.filter(is_today=True).count(),
            'pending_events': queryset.filter(status='pending').count(),
            'confirmed_events': queryset.filter(status='confirmed').count(),
            'completed_events': queryset.filter(status='completed').count(),
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def add_song_link(self, request, pk=None):
        """Agregar enlace de canción"""
        event = self.get_object()
        url = request.data.get('url')

        if not url:
            return Response(
                {'error': 'URL requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event.add_song_link(url)
        event.save()

        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def remove_song_link(self, request, pk=None):
        """Remover enlace de canción"""
        event = self.get_object()
        url = request.data.get('url')

        if not url:
            return Response(
                {'error': 'URL requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event.remove_song_link(url)
        event.save()

        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def generate_contract(self, request, pk=None):
        """Generar contrato"""
        event = self.get_object()

        if not event.can_generate_contract:
            return Response(
                {'error': 'No se puede generar contrato'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Aquí iría la lógica de generación de contrato
        event.status = 'contract_generated'
        event.save()

        return Response({'status': 'contract_generated'})


class ContractSignatureViewSet(viewsets.ModelViewSet):
    queryset = ContractSignature.objects.all()
    serializer_class = ContractSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'signature_type']

    def perform_create(self, serializer):
        serializer.save(
            signed_by=self.request.user,
            ip_address=self.get_client_ip()
        )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class EventPhotoViewSet(viewsets.ModelViewSet):
    queryset = EventPhoto.objects.all()
    serializer_class = EventPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'is_featured']

    @action(detail=True, methods=['post'])
    def set_featured(self, request, pk=None):
        """Marcar como foto destacada"""
        photo = self.get_object()

        # Quitar featured de otras fotos del mismo evento
        EventPhoto.objects.filter(
            event=photo.event,
            is_featured=True
        ).update(is_featured=False)

        photo.is_featured = True
        photo.save()

        return Response({'status': 'success'})


class VenueTemplateViewSet(viewsets.ModelViewSet):
    queryset = VenueTemplate.objects.filter(is_active=True)
    serializer_class = VenueTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'address']
    ordering = ['name']


class AudioTemplateViewSet(viewsets.ModelViewSet):
    queryset = AudioTemplate.objects.filter(is_active=True)
    serializer_class = AudioTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']


class ContractTemplateViewSet(viewsets.ModelViewSet):
    queryset = ContractTemplate.objects.filter(is_active=True)
    serializer_class = ContractTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'content']
    ordering = ['-is_default', 'name']

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Obtener plantilla por defecto"""
        template = ContractTemplate.objects.filter(
            is_default=True,
            is_active=True
        ).first()

        if template:
            serializer = self.get_serializer(template)
            return Response(serializer.data)

        return Response(
            {'error': 'No hay plantilla por defecto'},
            status=status.HTTP_404_NOT_FOUND
        )
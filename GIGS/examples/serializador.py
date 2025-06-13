from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    BookingEvent, ContractSignature, EventPhoto,
    VenueTemplate, AudioTemplate, ContractTemplate
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ContractSignatureSerializer(serializers.ModelSerializer):
    signed_by = UserSerializer(read_only=True)
    signature_type_display = serializers.CharField(source='get_signature_type_display', read_only=True)

    class Meta:
        model = ContractSignature
        fields = '__all__'
        read_only_fields = ['signed_by', 'ip_address', 'signed_at']


class EventPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPhoto
        fields = '__all__'


class BookingEventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    signatures = ContractSignatureSerializer(many=True, read_only=True)
    photos = EventPhotoSerializer(many=True, read_only=True)

    # Campos calculados
    duration_hours = serializers.ReadOnlyField()
    total_break_minutes = serializers.ReadOnlyField()
    pending_payment = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    payment_percentage = serializers.ReadOnlyField()
    can_edit = serializers.ReadOnlyField()
    can_generate_contract = serializers.ReadOnlyField()

    # Campos de display
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    formatted_duration = serializers.CharField(source='get_formatted_duration', read_only=True)
    song_links_list = serializers.ListField(source='get_song_links_list', read_only=True)

    class Meta:
        model = BookingEvent
        fields = '__all__'
        read_only_fields = [
            'contract_number', 'tiempo_total', 'total_payment',
            'created_by', 'contract_generated_at'
        ]

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class VenueTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueTemplate
        fields = '__all__'


class AudioTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTemplate
        fields = '__all__'


class ContractTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractTemplate
        fields = '__all__'
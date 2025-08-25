from rest_framework import serializers
from .models import Client, ClientManager

class ClientManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientManager
        fields = ['id', 'name', 'email']


class ClientSerializer(serializers.ModelSerializer):
    manager = ClientManagerSerializer(read_only=True)

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
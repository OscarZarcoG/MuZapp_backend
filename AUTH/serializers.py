# AUTH/serializers.py
from rest_framework import serializers
from .models import UserCustom

class UserCustomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'phone',
            'image_profile',
            'birthday',
            'gender',
            'role',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)
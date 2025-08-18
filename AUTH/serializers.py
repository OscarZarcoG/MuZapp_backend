# AUTH/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserCustom

class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')

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

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                try:
                    user_obj = UserCustom.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except UserCustom.DoesNotExist:
                    pass
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('La cuenta está desactivada.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Credenciales inválidas.')
        else:
            raise serializers.ValidationError('Debe proporcionar username/email y password.')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserCustom
        fields = (
            'username',
            'first_name', 
            'last_name',
            'email',
            'password',
            'password_confirm',
            'phone',
            'birthday',
            'gender'
        )
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        
        validated_data['role'] = 'client'
        
        password = validated_data.pop('password')
        user = UserCustom(**validated_data)
        user.set_password(password)
        user.save()
        return user
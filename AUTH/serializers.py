# AUTH/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from .exceptions import UserAlreadyExists, PasswordRequired


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            if hasattr(instance, 'profile'):
                data['profile'] = UserProfileSerializer(instance.profile).data
            else:
                # Crear el profile si no existe
                profile = UserProfile.objects.create(user=instance)
                data['profile'] = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            # Crear el profile si no existe
            profile = UserProfile.objects.create(user=instance)
            data['profile'] = UserProfileSerializer(profile).data
        except Exception:
            # Si hay cualquier error, devolver profile vacío
            data['profile'] = {'profile_picture': None}
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        username = validated_data.get('username')

        if User.objects.filter(username=username).exists():
            raise UserAlreadyExists()

        if 'password' not in validated_data:
            raise PasswordRequired()

        user = User.objects.create_user(
            username=username,
            password=validated_data['password']
        )

        if profile_data and 'profile_picture' in profile_data:
            if hasattr(user, 'profile'):
                user.profile.profile_picture = profile_data['profile_picture']
                user.profile.save()

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        instance.username = validated_data.get('username', instance.username)

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()

        if profile_data and 'profile_picture' in profile_data:
            try:
                profile = instance.profile
                profile.profile_picture = profile_data.get('profile_picture')
                profile.save()
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(
                    user=instance,
                    profile_picture=profile_data.get('profile_picture')
                )

        return instance
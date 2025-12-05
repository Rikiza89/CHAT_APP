# apps/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, FriendRequest, Friendship

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'avatar_url', 
                  'status_message', 'is_online', 'last_seen']
        read_only_fields = ['id', 'last_seen']
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user
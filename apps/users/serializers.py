from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name',
                  'last_name', 'phone_number', 'role']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(
        write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name',
                  'phone_number', 'role', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """Checking if user credentials are valid"""
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials, please try again.")
        
        # Generating tokens
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'profile_picture']
        read_only_fields = ['id', 'email']

    def validate_username(self, value):
        """Ensures username can only be changed once per month."""
        user = self.instance
        if user and user.username != value:
            if not user.can_change_username():
                raise serializers.ValidationError("You can only change your username once per month.")
        return value
    
    def update(self, instance , validated_data):
        """Update user profile and track username changes."""
        if 'username' in validated_data and instance.username != validated_data['username']:
            instance.last_username_change = now()
        return super().update(instance, validated_data)
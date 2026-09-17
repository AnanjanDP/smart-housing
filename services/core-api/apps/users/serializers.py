from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'name', 'role', 'phone_number', 'bio', 'avatar_url', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_name(self, obj):
        full = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full if full else obj.username

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'role', 'phone_number', 'avatar_url')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.Role.TENANT),
            phone_number=validated_data.get('phone_number', ''),
            avatar_url=validated_data.get('avatar_url', '')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login_input = attrs.get(self.username_field) or attrs.get('username') or attrs.get('email')
        password = attrs.get('password')

        if login_input and password:
            user = User.objects.filter(Q(email__iexact=login_input) | Q(username__iexact=login_input)).first()
            if user and user.check_password(password):
                attrs[self.username_field] = user.email
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

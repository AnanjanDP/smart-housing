from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from apps.users.models import User

# Roles a person may choose for themselves. ADMIN is never self-assignable.
SELF_SERVICE_ROLES = [
    (User.Role.TENANT, 'Tenant'),
    (User.Role.LANDLORD, 'Landlord'),
]


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'name', 'role', 'phone_number', 'bio', 'avatar_url', 'created_at')
        # role decides what a user may do, and email is how they sign in, so neither can be edited here.
        read_only_fields = ('id', 'email', 'role', 'created_at')

    def get_name(self, obj):
        full = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full if full else obj.username

class PublicUserSerializer(serializers.ModelSerializer):
    """What anyone may see about another user: who they are, never how to contact them.

    Listing owners, reviewers and roommate profiles are visible to anonymous visitors, so they use this
    instead of UserSerializer (which includes the email address and phone number).
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'name', 'avatar_url')
        read_only_fields = fields

    def get_name(self, obj):
        full = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full if full else obj.username


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=SELF_SERVICE_ROLES, default=User.Role.TENANT)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'role', 'phone_number', 'avatar_url')

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate(self, attrs):
        candidate = User(
            email=attrs.get('email', ''),
            username=attrs.get('username', ''),
            first_name=attrs.get('first_name', ''),
            last_name=attrs.get('last_name', ''),
        )
        try:
            validate_password(attrs['password'], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': list(exc.messages)})
        return attrs

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

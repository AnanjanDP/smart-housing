from apps.users.models import User

class UserService:
    @staticmethod
    def create_tenant(email, username, password, **extra_fields):
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            role=User.Role.TENANT,
            **extra_fields
        )

    @staticmethod
    def create_landlord(email, username, password, **extra_fields):
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            role=User.Role.LANDLORD,
            **extra_fields
        )

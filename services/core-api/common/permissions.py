from rest_framework import permissions

class IsLandlordUser(permissions.BasePermission):
    """Allows access only to users registered as Landlords."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'LANDLORD')

class IsTenantUser(permissions.BasePermission):
    """Allows access only to users registered as Tenants."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'TENANT')

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'owner', getattr(obj, 'user', None))
        return owner == request.user

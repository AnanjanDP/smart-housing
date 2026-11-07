from rest_framework import permissions


class IsListingOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class CanPublishListings(permissions.BasePermission):
    """Only landlords (and admins) may create listings; everyone may read them."""
    message = 'Only landlords can publish listings.'

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        user = request.user
        return bool(user and user.is_authenticated and user.role in ('LANDLORD', 'ADMIN'))

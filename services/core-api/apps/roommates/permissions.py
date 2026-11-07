from rest_framework import permissions


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """A roommate profile can be changed or deleted only by the person it belongs to."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id

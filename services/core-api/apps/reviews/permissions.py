from rest_framework import permissions


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """A review can be changed or deleted only by the person who wrote it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer_id == request.user.id

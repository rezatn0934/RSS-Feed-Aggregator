from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserIsOwner(BasePermission):
    message = 'Permission denied, you do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id



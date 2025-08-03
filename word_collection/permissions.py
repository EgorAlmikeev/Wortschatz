from rest_framework.permissions import BasePermission, SAFE_METHODS
from .utils import get_superuser_id

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.owner or request.user.id == get_superuser_id()
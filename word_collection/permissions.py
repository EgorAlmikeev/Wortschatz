from rest_framework.permissions import BasePermission
from .utils import get_superuser_id

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD']:
            return True
        return request.user == obj.owner or request.user.id == get_superuser_id()
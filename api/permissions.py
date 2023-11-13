from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied


class IsOwnerOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        
        if obj.author.user != request.user:
            raise PermissionDenied('You do not have permission to perform this action!')
        
        return True
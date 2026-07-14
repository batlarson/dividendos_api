from rest_framework.permissions import BasePermission

class EsDuenoDelActivo(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user
from rest_framework.permissions import BasePermission
import datetime

class EsDuenoDelActivo(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user
    
class ActualizarEntreSemana(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH']:
            dia = datetime.date.today().weekday()
            if dia >= 5:
                return False
        return True
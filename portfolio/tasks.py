from celery import shared_task
from .models import Dividendo, Historial, Activo

@shared_task
def tarea_prueba():
    return "Celery funciona!"

@shared_task(bind=True, max_retries=3)
def procesar_dividendo(self, dividendo_id):
    try:
        dividendo = Dividendo.objects.get(id=dividendo_id)
        Historial.objects.create(
            activo=dividendo.activo,
            mensaje=f"{dividendo.activo.ticker} te ha pagado {round(dividendo.importe_neto(), 4)} el {dividendo.fecha_pago}"
        )
    except Dividendo.DoesNotExist:
        return f"Dividendo {dividendo_id} no encontrado"
    except Exception as exc:
        try:
            self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            return f"Error procesando dividendo {dividendo_id} después de 3 intentos: {str(exc)}"

@shared_task
def revisar_activos_sin_dividendos():
    from django.utils import timezone
    from datetime import timedelta
    
    hace_6_meses = timezone.now().date() - timedelta(days=180)
    
    activos = Activo.objects.exclude(
        dividendo__fecha_pago__gte=hace_6_meses
    )
    
    for activo in activos:
        Historial.objects.create(
            activo=activo,
            mensaje=f"ALERTA: {activo.ticker} no ha pagado dividendos en 6 meses"
        )
    
    return f"Revisados {activos.count()} activos sin dividendos recientes"
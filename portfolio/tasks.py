from celery import shared_task
from .models import Dividendo, Historial

@shared_task
def tarea_prueba():
    return "Celery funciona!"

@shared_task
def procesar_dividendo(dividendo_id):
    dividendo = Dividendo.objects.get(id=dividendo_id)
    Historial.objects.create(
        activo=dividendo.activo,
        mensaje=f"{dividendo.activo.ticker} te ha pagado {round(dividendo.importe_neto(), 4)} el {dividendo.fecha_pago}"
    )
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Historial, Dividendo

@receiver(post_save, sender=Dividendo)
def dividendo_agregado(sender, instance, created, **kwargs):
    if created:
        Historial.objects.create(
            activo = instance.activo,
            mensaje=f"{instance.activo.ticker} te ha pagado {instance.importe_neto()} el {instance.fecha_pago}"
        )

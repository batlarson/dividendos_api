from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Historial, Dividendo
from .tasks import procesar_dividendo

@receiver(post_save, sender=Dividendo)
def dividendo_agregado(sender, instance, created, **kwargs):
    if created:
        procesar_dividendo.delay(instance.id)  # manda el ID a Celery
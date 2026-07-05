from celery import shared_task

@shared_task
def tarea_prueba():
    return "Celery funciona!"
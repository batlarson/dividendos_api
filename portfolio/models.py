from django.db import models
from django.contrib.auth.models import User

class Activo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    ticker = models.CharField(max_length=5)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Compra(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE) 
    fecha_compra = models.DateField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.DecimalField(max_digits=15, decimal_places=8)

    def __str__(self):
        return f"{self.activo} - {self.fecha_compra}"

class Dividendo(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE) 
    fecha_pago = models.DateField()
    div_origen = models.DecimalField(max_digits=20, decimal_places=2)
    cambio_nominal = models.DecimalField(max_digits=15, decimal_places=8)
    impuesto = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.activo} | {self.fecha_pago} | {self.importe_neto()}€"
    
    def importe_neto(self):
        return self.div_origen * self.cambio_nominal * (1 - self.impuesto / 100)
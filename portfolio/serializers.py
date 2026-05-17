from rest_framework import serializers
from .models import Activo, Compra, Dividendo

class ActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activo
        fields = ['id', 'usuario', 'precio', 'ticker', 'nombre', 'cantidad']
        read_only_fields = ['id', 'usuario']

class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        fields = ['id', 'activo', 'fecha_compra', 'precio', 'cantidad']
        read_only_fields = ['id']

class DividendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dividendo
        fields = ['id', 'activo', 'fecha_pago', 'div_origen','cambio_nominal', 'impuesto']
        read_only_fields = ['id']

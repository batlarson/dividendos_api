from rest_framework import serializers
from .models import Activo, Compra, Dividendo
from django.db.models import Count, Sum, F, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response


class ActivoSerializer(serializers.ModelSerializer):
    precio_medio = serializers.SerializerMethodField()
    div_anual = serializers.SerializerMethodField()
    yoc = serializers.SerializerMethodField()
       
    def get_precio_medio(self, obj):
        resultado = (Compra.objects.filter(activo=obj).aggregate(
            total_valor=Sum(F('precio') * F('cantidad')),
            total_cantidad=Sum(F('cantidad'))
            ))
        if resultado['total_cantidad']:
            return resultado['total_valor'] / resultado['total_cantidad']
        return None
    
    def get_div_anual(self,obj):
        hace_un_año = timezone.now().date() - timedelta(days=365)
        resultado = (Dividendo.objects.filter(activo=obj, fecha_pago__gte=hace_un_año).aggregate(
            total_div = Sum('div_origen'),
        ))
        if resultado['total_div']:
            return resultado['total_div']
        return None
    
    def get_yoc(self, obj):
        precio_medio = self.get_precio_medio(obj)
        div_anual = self.get_div_anual(obj)
        
        if precio_medio and div_anual:
            return div_anual / obj.cantidad / precio_medio * 100
        return None
    
    def top_divs_activos(self,obj):
        resultado = (Dividendo.objects.values('activo', 'activo__ticker').annotate(
            total_div = Sum('div_origen')           
        ).order_by('-total_div')[:3])
        return resultado
        
    class Meta:
        model = Activo
        fields = ['id', 'usuario', 'precio', 'ticker', 'nombre', 'cantidad', 'precio_medio', 'div_anual', 'yoc']
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


        
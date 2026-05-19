from rest_framework import serializers
from .models import Activo, Compra, Dividendo
from django.db.models import Count, Sum, F, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
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
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        hace_un_año = timezone.now().date() - timedelta(days=365)
        total_activos = self.get_queryset().count()
        total_invertido = (Compra.objects.filter(
            activo__usuario = request.user,
        ).aggregate(
            total_precio=Sum(F('precio')* F('cantidad'))
        ))
        dividendos_anuales = (Dividendo.objects.filter(
            activo__usuario = request.user,
            fecha_pago__gte = hace_un_año
        ).aggregate(
            total_div=Sum('div_origen')
        ))
        if dividendos_anuales['total_div'] and total_invertido['total_precio']:
            yoc_global = dividendos_anuales['total_div'] / total_invertido['total_precio'] * 100
        else:
            yoc_global = None
        return Response({
            'total_activos': total_activos,
            'total_invertido': total_invertido['total_precio'],
            'dividendos_anuales': dividendos_anuales['total_div'],
            'yoc_global': yoc_global
        })
    

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


        
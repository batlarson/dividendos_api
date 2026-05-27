from rest_framework import serializers
from .models import Activo, Compra, Dividendo
from django.db.models import Count, Sum, F, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
import yfinance as yf


class ActivoSerializer(serializers.ModelSerializer):
    precio_medio = serializers.SerializerMethodField()
    div_anual = serializers.SerializerMethodField()
    yoc = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    dividend_yield = serializers.SerializerMethodField()
    payout_ratio = serializers.SerializerMethodField()
    per = serializers.SerializerMethodField()

    def get_precio(self, obj):
        ticker = yf.Ticker(obj.ticker)
        return ticker.info.get('currentPrice')
    
    def get_dividend_yield(self, obj):
        ticker = yf.Ticker(obj.ticker)
        return ticker.info.get('dividendYield')
    
    def get_payout_ratio(self, obj):
        ticker = yf.Ticker(obj.ticker)
        return ticker.info.get('payoutRatio')
    
    def get_per(self, obj):
        ticker = yf.Ticker(obj.ticker)
        return ticker.info.get('trailingPE')
       
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
    
        
    class Meta:
        model = Activo
        fields = ['id', 'usuario', 'ticker', 'nombre', 'cantidad', 'precio', 'precio_medio', 'dividend_yield', 'div_anual', 'yoc', 'payout_ratio', 'per']
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


        
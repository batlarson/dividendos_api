from rest_framework import serializers
from .models import Activo, Compra, Dividendo, Historial
from django.db.models import Count, Sum, F, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
import yfinance as yf
from django.core.cache import cache


class ActivoSerializer(serializers.ModelSerializer):
    precio_medio = serializers.SerializerMethodField()
    cantidad = serializers.SerializerMethodField()
    div_anual = serializers.SerializerMethodField()
    yoc = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    dividend_yield = serializers.SerializerMethodField()
    payout_ratio = serializers.SerializerMethodField()
    per = serializers.SerializerMethodField()

    def get_precio(self, obj):
        cache_key = f'precio_{obj.ticker}'
        precio = cache.get(cache_key)
        if precio is None:
            ticker = yf.Ticker(obj.ticker)
            precio = ticker.info.get('currentPrice')
            cache.set(cache_key, precio, timeout=60)  # 1 minuto
        return precio
    
    def get_cantidad(self, obj):
        resultado = Compra.objects.filter(activo=obj).aggregate(
            total=Sum('cantidad')
        )
        return resultado['total'] or 0
    
    def get_dividend_yield(self, obj):
        cache_key = f'yield_{obj.ticker}'
        dividend_yield = cache.get(cache_key)
        if dividend_yield is None:
            ticker = yf.Ticker(obj.ticker)
            dividend_yield = ticker.info.get('dividendYield')
            cache.set(cache_key, dividend_yield, timeout=600)  # 10 minutos
        return dividend_yield
    
    def get_payout_ratio(self, obj):
        cache_key = f'payout_ratio_{obj.ticker}'
        payout_ratio = cache.get(cache_key)
        if payout_ratio is None:
            ticker = yf.Ticker(obj.ticker)
            payout_ratio = ticker.info.get('payoutRatio')
            cache.set(cache_key, payout_ratio, timeout=600)  # 10 minutos
        return payout_ratio
    
    def get_per(self, obj):
        cache_key = f'per_{obj.ticker}'
        per = cache.get(cache_key)
        if per is None:
            ticker = yf.Ticker(obj.ticker)
            per = ticker.info.get('trailingPE')
            cache.set(cache_key, per, timeout=1200)  # 20 minutos
        return per
       
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
        cantidad = self.get_cantidad(obj)
        
        if precio_medio and div_anual:
            return div_anual / cantidad / precio_medio * 100
        return None
    
        
    class Meta:
        model = Activo
        fields = ['id', 'usuario', 'ticker', 'nombre', 'cantidad', 'precio', 'precio_medio', 'dividend_yield', 'div_anual', 'yoc', 'payout_ratio', 'per']
        read_only_fields = ['id', 'usuario', 'cantidad']

class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        fields = ['id', 'activo', 'fecha_compra', 'precio', 'cantidad', 'cambio_divisa']
        read_only_fields = ['id']

class DividendoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dividendo
        fields = ['id', 'activo', 'fecha_pago', 'div_origen','cambio_nominal', 'impuesto']
        read_only_fields = ['id']

class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = ['id', 'activo', 'mensaje', 'fecha']



        
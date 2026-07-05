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

    def get_yahoo_data(self, obj):
        cache_key = f'yahoo_{obj.ticker}'
        data = cache.get(cache_key)
        if data is None:
            ticker = yf.Ticker(obj.ticker)
            eurusd = yf.Ticker("EURUSD=X")
            tipo_cambio = eurusd.info.get('regularMarketPrice', 1)
            info = ticker.info
            data = {
                'precio': round(info.get('currentPrice', 0) / tipo_cambio, 2),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'per': info.get('trailingPE'),
            }
            cache.set(cache_key, data, timeout=60)
        return data

    def get_precio(self, obj):
        return self.get_yahoo_data(obj)['precio']
    
    def get_cantidad(self, obj):
        resultado = Compra.objects.filter(activo=obj).aggregate(
            total=Sum('cantidad')
        )
        return resultado['total'] or 0
    
    def get_dividend_yield(self, obj):
        return self.get_yahoo_data(obj)['dividend_yield']
    
    def get_payout_ratio(self, obj):
        return self.get_yahoo_data(obj)['payout_ratio']
    
    def get_per(self, obj):
        return self.get_yahoo_data(obj)['per']
       
    def get_precio_medio(self, obj):
        resultado = (Compra.objects.filter(activo=obj).aggregate(
            total_valor=Sum(F('precio') * F('cantidad') * F('cambio_divisa')),
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
    activo_nombre = serializers.SerializerMethodField()
    
    def get_activo_nombre(self, obj):
        return obj.activo.nombre
    
    class Meta:
        model = Compra
        fields = ['id', 'activo', 'fecha_compra', 'precio', 'cantidad', 'cambio_divisa','activo_nombre']
        read_only_fields = ['id']

class DividendoSerializer(serializers.ModelSerializer):
    activo_nombre = serializers.SerializerMethodField()
    
    def get_activo_nombre(self, obj):
        return obj.activo.nombre

    class Meta:
        model = Dividendo
        fields = ['id', 'activo', 'fecha_pago', 'div_origen','cambio_nominal', 'impuesto', 'activo_nombre']
        read_only_fields = ['id']

class HistorialSerializer(serializers.ModelSerializer):
    activo_nombre = serializers.SerializerMethodField()
    
    def get_activo_nombre(self, obj):
        return obj.activo.nombre

    class Meta:
        model = Historial
        fields = ['id', 'activo', 'mensaje', 'fecha', 'activo_nombre']



        
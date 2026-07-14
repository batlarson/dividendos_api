from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.db.models import Count, Sum, F, Avg, Q, Case, When, Value, CharField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Activo, Compra, Dividendo, Historial
from .serializers import ActivoSerializer, DividendoSerializer, CompraSerializer, HistorialSerializer
import yfinance as yf

class ActivoViewSet(viewsets.ModelViewSet):
    serializer_class = ActivoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ticker', 'nombre']
    search_fields = ['nombre', 'ticker']
    ##La diferencia con filterset_fields es que search hace búsqueda parcial con icontains — busca dentro del texto. filterset_fields busca coincidencia exacta.
    ordering_fields = ['precio', 'ticker', 'cantidad', 'nombre', 'dividend_yield']
    ordering = ['ticker']  # orden por defecto

    def get_queryset(self):
        return Activo.objects.filter(usuario=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

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
    
    @action(detail=False, methods=['get'])
    def no_divs(self,request):
        hace_medio_año = timezone.now().date() - timedelta(days = 180)

        con_dividendos = (Dividendo.objects.filter(
            activo__usuario = request.user,
            fecha_pago__gte = hace_medio_año,
        ).values_list('activo_id', flat=True))

        sin_dividendos = self.get_queryset().exclude(id__in=con_dividendos)
        return Response([
            {'ticker': activo.ticker, 'mensaje': 'Sin dividendos en 6 meses'}
            for activo in sin_dividendos
        ])

    @action(detail=False, methods=['get'])
    def top_divs_activos(self, request):
        resultado = (Dividendo.objects.values('activo', 'activo__ticker').annotate(
            total_div = Sum('div_origen')           
        ).order_by('-total_div')[:3])
        return Response(list(resultado))
        
    @action(detail=False, methods=['get'])    
    def full_divs_gt(self, request):
        umbral = request.query_params.get('umbral', 100)
        resultado = (Dividendo.objects
            .values('activo__ticker')     
            .annotate(total=Sum('div_origen')) 
            .filter(total__gte=umbral)    
            .order_by('-total'))
        return Response(list(resultado))

    @action(detail=False, methods=['get']) 
    def mejor_mes_divs(self, request):
        resultado = (Dividendo.objects
            .annotate(month=TruncMonth('fecha_pago'))
            .values('month')
            .annotate(total = Sum('div_origen'))
            .order_by('-total')[:1])
        return Response(list(resultado))
    
    @action(detail=False, methods=['get'])
    def a_revisar(self, request):
        hace_medio_año = timezone.now().date() - timedelta(days=180)
        
        con_dividendos = Dividendo.objects.filter(
            activo__usuario=request.user,
            fecha_pago__gte=hace_medio_año
        ).values_list('activo_id', flat=True)
        
        pocas_compras = Compra.objects.filter(
            activo__usuario=request.user
        ).values('activo_id').annotate(
            total=Count('id')
        ).filter(total__lte=1).values_list('activo_id', flat=True)
        
        resultado = self.get_queryset().filter(
            Q(id__in=pocas_compras) | ~Q(id__in=con_dividendos)
        )
        
        return Response([
            {'ticker': a.ticker, 'nombre': a.nombre}
            for a in resultado
        ])
    
    @action(detail=False, methods=['get'])
    def clasificar_dividendos(self, request):
        hace_un_año = timezone.now().date() - timedelta(days=365)
        
        resultado = self.get_queryset().annotate(
            total_divs=Sum('dividendo__div_origen', filter=Q(dividendo__fecha_pago__gte=hace_un_año)),
            clasificacion=Case(
                When(total_divs__gte=100, then=Value('Excelente')),
                When(total_divs__gte=50, then=Value('Bueno')),
                When(total_divs__gt=0, then=Value('Bajo')),
                default=Value('Sin dividendos'),
                output_field=CharField()
            )
        ).values('ticker', 'nombre', 'total_divs', 'clasificacion')
        
        return Response(list(resultado))
        
        


class CompraViewSet(viewsets.ModelViewSet):
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['activo__ticker']
    ordering_fields = ['fecha_compra', 'precio', 'cantidad']
    ordering = ['-fecha_compra']

    def get_queryset(self):
        return Compra.objects.filter(activo__usuario=self.request.user).select_related('activo').order_by('-fecha_compra')



class DividendoViewSet(viewsets.ModelViewSet):
    serializer_class = DividendoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['activo__ticker']
    ordering_fields = ['fecha_pago', 'div_origen']
    ordering = ['-fecha_pago']

    def get_queryset(self):
        return Dividendo.objects.filter(activo__usuario=self.request.user).select_related('activo').order_by('-fecha_pago')
    
class HistorialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['activo__ticker']

    def get_queryset(self):
         return Historial.objects.filter(activo__usuario=self.request.user).select_related('activo').order_by('-fecha')


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data['access']
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,      # JavaScript no puede leerla
                secure=not settings.DEBUG,        # Solo HTTPS
                samesite='Lax',     # Protección CSRF
            )
        return response
    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Lee el refresh token de la cookie y lo mete en el request
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token missing.'}, status=400)
        request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            response.set_cookie(
                key='access_token',
                value=response.data['access'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
            )
        return response


@api_view(['POST'])
def logout_view(request):
    response = Response({'message': 'Logout exitoso'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response
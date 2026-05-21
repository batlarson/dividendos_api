from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, F, Avg
from .models import Activo, Compra, Dividendo
from .serializers import ActivoSerializer, DividendoSerializer, CompraSerializer

class ActivoViewSet(viewsets.ModelViewSet):
    serializer_class = ActivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activo.objects.filter(usuario=self.request.user)

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


class CompraViewSet(viewsets.ModelViewSet):
    serializer_class = CompraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Compra.objects.filter(activo__usuario=self.request.user)



class DividendoViewSet(viewsets.ModelViewSet):
    serializer_class = DividendoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dividendo.objects.filter(activo__usuario=self.request.user)




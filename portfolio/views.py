from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Activo, Compra, Dividendo
from .serializers import ActivoSerializer, DividendoSerializer, CompraSerializer

class ActivoViewSet(viewsets.ModelViewSet):
    serializer_class = ActivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activo.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

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




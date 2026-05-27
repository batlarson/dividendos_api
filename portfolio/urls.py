from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivoViewSet, CompraViewSet, DividendoViewSet


router = DefaultRouter()
router.register('activos', ActivoViewSet, basename='activo')
router.register('compras', CompraViewSet, basename='compra')
router.register('dividendos', DividendoViewSet, basename='dividendo')

urlpatterns = router.urls
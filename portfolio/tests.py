from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Activo, Compra, Dividendo, Historial

class ActivoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.activo = Activo.objects.create(
            usuario=self.user,
            nombre='Coca Cola',
            ticker='KO',
        )
        
        self.compra1 = Compra.objects.create(
            activo=self.activo,
            fecha_compra='2026-05-22',
            precio=100,
            cantidad=10
        )
        
        self.compra2 = Compra.objects.create(
            activo=self.activo,
            fecha_compra='2026-05-22',
            precio=130,
            cantidad=5
        )

        self.div = Dividendo.objects.create(
            activo=self.activo,
            fecha_pago='2026-04-22',
            div_origen= 0.5,
            cambio_nominal= 1.16,
            impuesto= 15
        )
    
    def test_crear_activo(self):
        url = reverse('activo-list')

        data = {
            'nombre': 'Coca Cola',
            'ticker': 'KO',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activo.objects.count(), 2)

    def test_precio_medio_ponderado(self):
        url_detalle = reverse('activo-detail', kwargs={'pk': self.activo.id})

        response = self.client.get(url_detalle)
        self.assertEqual(float(response.data['precio_medio']), 110.0)

    def test_yoc(self):
        url_detalle = reverse('activo-detail', kwargs={'pk': self.activo.id})

        response = self.client.get(url_detalle)
        self.assertAlmostEqual(float(response.data['yoc']), 0.02987, places=3)
    
    def test_historial(self):
        self.assertEqual(Historial.objects.count(), 1)

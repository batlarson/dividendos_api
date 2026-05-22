from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Activo, Compra, Dividendo

class ActivoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_crear_activo(self):
        url = reverse('activo-list')

        data = {
            'nombre': 'Coca Cola',
            'ticker': 'KO',
            'precio': 155,
            'cantidad': 2
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activo.objects.count(), 1)

    def test_precio_medio_ponderado(self):
        url_activo = reverse('activo-list')
        url_compra = reverse('compra-list')    

        data_activo = {
            'nombre': 'Coca Cola',
            'ticker': 'KO',
            'precio': 155,
            'cantidad': 2
        }

        response = self.client.post(url_activo, data_activo)
        activo_id = response.data['id']
        url_detalle = reverse('activo-detail', kwargs={'pk': activo_id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activo.objects.count(), 1)

        data_compra_1 = {
            'activo': activo_id,
            'fecha_compra': '2026-05-22',
            'precio': 100,
            'cantidad': 10
        }

        response = self.client.post(url_compra, data_compra_1)
        self.assertEqual(Compra.objects.count(), 1)

        data_compra_2 = {
            'activo': activo_id,
            'fecha_compra': '2026-05-22',
            'precio': 130,
            'cantidad': 5
        }

        response = self.client.post(url_compra, data_compra_2)      
        self.assertEqual(Compra.objects.count(), 2)

        response = self.client.get(url_detalle)
        self.assertEqual(float(response.data['precio_medio']), 110.0)

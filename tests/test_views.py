from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from decimal import Decimal
import json

from GIGS.models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato
from .test_base import BaseTestCase


class ClienteViewSetTest(APITestCase, BaseTestCase):
    """Pruebas para ClienteViewSet"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = '/api/agenda/clientes/'
    
    def test_listar_clientes(self):
        """Prueba listar todos los clientes"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_cliente'], 'Juan Pérez')
    
    def test_crear_cliente(self):
        """Prueba crear un nuevo cliente"""
        data = {
            'nombre_cliente': 'María García',
            'telefono_cliente': '987654321',
            'frecuencia': 2
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre_cliente'], 'María García')
        self.assertTrue(Cliente.objects.filter(nombre_cliente='María García').exists())
    
    def test_obtener_cliente_especifico(self):
        """Prueba obtener un cliente específico"""
        url = f'{self.url}{self.cliente.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_cliente'], 'Juan Pérez')
    
    def test_actualizar_cliente(self):
        """Prueba actualizar un cliente"""
        url = f'{self.url}{self.cliente.id}/'
        data = {
            'nombre_cliente': 'Juan Pérez Actualizado',
            'telefono_cliente': '999888777',
            'frecuencia': 3
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_cliente'], 'Juan Pérez Actualizado')
    
    def test_eliminar_cliente(self):
        """Prueba eliminar un cliente (soft delete)"""
        url = f'{self.url}{self.cliente.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que el cliente fue marcado como inactivo
        cliente = Cliente.objects.get(id=self.cliente.id)
        self.assertFalse(cliente.is_active)
    
    def test_buscar_clientes(self):
        """Prueba la funcionalidad de búsqueda"""
        # Crear cliente adicional
        Cliente.objects.create(
            nombre_cliente='Ana López',
            telefono_cliente='555666777',
            frecuencia=1
        )
        
        # Buscar por nombre
        response = self.client.get(f'{self.url}?search=Ana')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_cliente'], 'Ana López')
    
    def test_filtrar_por_frecuencia(self):
        """Prueba filtrar clientes por frecuencia"""
        Cliente.objects.create(
            nombre_cliente='Cliente Frecuente',
            telefono_cliente='111222333',
            frecuencia=5
        )
        
        response = self.client.get(f'{self.url}?frecuencia=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_cliente'], 'Cliente Frecuente')


class EquipoAudioViewSetTest(APITestCase, BaseTestCase):
    """Pruebas para EquipoAudioViewSet"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = '/api/agenda/equipos-audio/'
    
    def test_listar_equipos(self):
        """Prueba listar equipos de audio"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['marca'], 'JBL')
    
    def test_crear_equipo(self):
        """Prueba crear un nuevo equipo"""
        data = {
            'marca': 'Yamaha',
            'modelo': 'DXR12',
            'numero_bocinas': 4,
            'descripcion': 'Equipo profesional',
            'precio': 2000
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['marca'], 'Yamaha')
    
    def test_filtrar_por_precio(self):
        """Prueba el endpoint personalizado de filtro por precio"""
        # Crear equipos con diferentes precios
        Equipo_Audio.objects.create(
            marca='Bose',
            modelo='S1 Pro',
            numero_bocinas=1,
            descripcion='Equipo portátil',
            precio=800
        )
        
        url = f'{self.url}por_precio/?precio_min=1000&precio_max=2000'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe devolver el equipo JBL que cuesta 1500
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['marca'], 'JBL')


class ContratoViewSetTest(APITestCase, BaseTestCase):
    """Pruebas para ContratoViewSet"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = '/api/agenda/contratos/'
    
    def test_listar_contratos(self):
        """Prueba listar contratos"""
        contrato = self.crear_contrato()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Cumpleaños de Juan')
    
    def test_crear_contrato(self):
        """Prueba crear un nuevo contrato"""
        data = {
            'titulo': 'Boda de Ana y Carlos',
            'tipo_evento': 'wedding',
            'nombre_festejado': 'Ana y Carlos',
            'fecha_evento': date.today() + timedelta(days=45),
            'hora_inicio': '19:00:00',
            'hora_final': '23:00:00',
            'costo_hora': '200.00',
            'pago_adelanto': '400.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Iglesia San José',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 100
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], 'Boda de Ana y Carlos')
        self.assertEqual(response.data['estado_evento'], 'confirmed')  # Porque tiene adelanto
    
    def test_crear_contrato_con_conflicto_horario(self):
        """Prueba crear contrato con conflicto de horarios"""
        # Crear primer contrato
        fecha_evento = date.today() + timedelta(days=50)
        self.crear_contrato(
            fecha_evento=fecha_evento,
            hora_inicio=time(20, 0),
            hora_final=time(23, 0)
        )
        
        # Intentar crear contrato conflictivo
        data = {
            'titulo': 'Evento Conflictivo',
            'tipo_evento': 'birthday',
            'nombre_festejado': 'Test',
            'fecha_evento': fecha_evento,
            'hora_inicio': '22:00:00',  # Se solapa
            'hora_final': '23:59:00',
            'costo_hora': '150.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Lugar Test',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 50
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Conflicto de horarios', str(response.data))
    
    def test_obtener_proximos_eventos(self):
        """Prueba el endpoint de próximos eventos"""
        # Crear evento próximo
        self.crear_contrato(
            fecha_evento=date.today() + timedelta(days=15),
            titulo='Evento Próximo'
        )
        
        # Crear evento lejano
        self.crear_contrato(
            fecha_evento=date.today() + timedelta(days=60),
            titulo='Evento Lejano'
        )
        
        url = f'{self.url}proximos_eventos/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe devolver el evento próximo (dentro de 30 días)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Evento Próximo')
    
    def test_obtener_eventos_hoy(self):
        """Prueba el endpoint de eventos de hoy"""
        # Crear evento para hoy
        self.crear_contrato(
            fecha_evento=date.today(),
            titulo='Evento de Hoy'
        )
        
        # Crear evento para mañana
        self.crear_contrato(
            fecha_evento=date.today() + timedelta(days=1),
            titulo='Evento de Mañana'
        )
        
        url = f'{self.url}eventos_hoy/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe devolver el evento de hoy
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Evento de Hoy')
    
    def test_obtener_estadisticas(self):
        """Prueba el endpoint de estadísticas"""
        # Crear contratos con diferentes estados
        self.crear_contrato(titulo='Pendiente', pago_adelanto=Decimal('0.00'))
        self.crear_contrato(titulo='Confirmado', pago_adelanto=Decimal('200.00'))
        
        url = f'{self.url}estadisticas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_contratos'], 2)
        self.assertEqual(response.data['pendientes'], 1)
        self.assertEqual(response.data['confirmados'], 1)
    
    def test_cancelar_contrato(self):
        """Prueba cancelar un contrato"""
        contrato = self.crear_contrato()
        
        url = f'{self.url}{contrato.id}/cancelar/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado_evento'], 'cancelled')
    
    def test_confirmar_contrato(self):
        """Prueba confirmar un contrato con adelanto"""
        contrato = self.crear_contrato(pago_adelanto=Decimal('0.00'))
        
        url = f'{self.url}{contrato.id}/confirmar/'
        data = {'adelanto': 300}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado_evento'], 'confirmed')
        self.assertEqual(float(response.data['pago_adelanto']), 300.0)
    
    def test_confirmar_contrato_sin_adelanto(self):
        """Prueba confirmar contrato sin adelanto (debe fallar)"""
        contrato = self.crear_contrato()
        
        url = f'{self.url}{contrato.id}/confirmar/'
        data = {'adelanto': 0}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('El adelanto debe ser mayor a 0', str(response.data))
    
    def test_buscar_contratos(self):
        """Prueba la funcionalidad de búsqueda en contratos"""
        contrato = self.crear_contrato(titulo='Cumpleaños Especial')
        
        response = self.client.get(f'{self.url}?search=Especial')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Cumpleaños Especial')
    
    def test_filtrar_por_estado(self):
        """Prueba filtrar contratos por estado"""
        self.crear_contrato(titulo='Pendiente', pago_adelanto=Decimal('0.00'))
        self.crear_contrato(titulo='Confirmado', pago_adelanto=Decimal('200.00'))
        
        response = self.client.get(f'{self.url}?estado_evento=confirmed')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Confirmado')
    
    def test_filtrar_por_tipo_evento(self):
        """Prueba filtrar contratos por tipo de evento"""
        self.crear_contrato(tipo_evento='birthday')
        self.crear_contrato(tipo_evento='wedding', titulo='Boda Test')
        
        response = self.client.get(f'{self.url}?tipo_evento=wedding')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Boda Test')


class PeticionViewSetTest(APITestCase, BaseTestCase):
    """Pruebas para PeticionViewSet"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = '/api/agenda/peticiones/'
    
    def test_listar_peticiones(self):
        """Prueba listar peticiones"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # peticion1 y peticion2 del setUp
    
    def test_crear_peticion(self):
        """Prueba crear una nueva petición"""
        data = {
            'nombre_cancion': 'Nueva Canción',
            'link': 'https://youtube.com/nueva'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre_cancion'], 'Nueva Canción')
    
    def test_buscar_peticiones(self):
        """Prueba buscar peticiones por nombre"""
        response = self.client.get(f'{self.url}?search=Vida')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_cancion'], 'La Vida es una Fiesta')


class RepertorioViewSetTest(APITestCase, BaseTestCase):
    """Pruebas para RepertorioViewSet"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = '/api/agenda/repertorio/'
    
    def test_listar_repertorio(self):
        """Prueba listar repertorio"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_cancion'], 'Música Variada')
    
    def test_crear_repertorio(self):
        """Prueba crear nuevo repertorio"""
        data = {
            'nombre_cancion': 'Rock Clásico'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre_cancion'], 'Rock Clásico')


class CateringViewSetTest(APITestCase, BaseTestCase):
    """Pruebas para CateringViewSet"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = '/api/agenda/catering/'
    
    def test_listar_catering(self):
        """Prueba listar catering"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['peticion_grupo'], 'Bebidas y snacks para el grupo')
    
    def test_crear_catering(self):
        """Prueba crear nuevo catering"""
        data = {
            'peticion_grupo': 'Comida vegetariana para 30 personas'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['peticion_grupo'], 'Comida vegetariana para 30 personas')
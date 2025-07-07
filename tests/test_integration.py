from django.test import TestCase, TransactionTestCase
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, time, timedelta
from decimal import Decimal
import json

from GIGS.models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Contrato
from .test_base import BaseTestCase


class ContratoIntegrationTest(APITestCase, BaseTestCase):
    """Pruebas de integración para el flujo completo de contratos"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
    
    def test_flujo_completo_creacion_contrato(self):
        """Prueba el flujo completo desde la creación hasta la confirmación de un contrato"""
        
        # 1. Crear un nuevo cliente
        cliente_data = {
            'nombre_cliente': 'Carlos Mendoza',
            'telefono_cliente': '987123456',
            'redes_sociales': 'https://facebook.com/carlos',
            'frecuencia': 1
        }
        
        response = self.client.post('/api/agenda/clientes/', cliente_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cliente_id = response.data['id']
        
        # 2. Crear equipo de audio
        equipo_data = {
            'marca': 'Bose',
            'modelo': 'L1 Pro32',
            'numero_bocinas': 2,
            'descripcion': 'Sistema portátil profesional',
            'precio': 3000
        }
        
        response = self.client.post('/api/agenda/equipos-audio/', equipo_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        equipo_id = response.data['id']
        
        # 3. Crear catering
        catering_data = {
            'peticion_grupo': 'Bebidas energéticas y agua para el grupo'
        }
        
        response = self.client.post('/api/agenda/catering/', catering_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        catering_id = response.data['id']
        
        # 4. Crear peticiones musicales
        peticion1_data = {
            'nombre_cancion': 'Bohemian Rhapsody',
            'link': 'https://youtube.com/bohemian'
        }
        
        peticion2_data = {
            'nombre_cancion': 'Hotel California'
        }
        
        response1 = self.client.post('/api/agenda/peticiones/', peticion1_data, format='json')
        response2 = self.client.post('/api/agenda/peticiones/', peticion2_data, format='json')
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        peticion1_id = response1.data['id']
        peticion2_id = response2.data['id']
        
        # 5. Crear contrato completo
        contrato_data = {
            'titulo': 'Aniversario de Bodas Carlos y María',
            'tipo_evento': 'anniversary',
            'nombre_festejado': 'Carlos y María',
            'fecha_evento': date.today() + timedelta(days=45),
            'hora_inicio': '19:00:00',
            'hora_final': '23:30:00',
            'costo_hora': '250.00',
            'pago_adelanto': '0.00',  # Sin adelanto inicialmente
            'cliente': cliente_id,
            'equipo_audio': equipo_id,
            'catering': catering_id,
            'nombre_lugar': 'Restaurante El Jardín',
            'descripcion_lugar': 'Restaurante con terraza y jardín',
            'google_maps_url': 'https://maps.google.com/jardin',
            'audiencia': 80,
            'oportunidades_descanso': 2,
            'tiempo_descanso': 20,
            'notas': 'Evento especial de aniversario, música romántica preferida'
        }
        
        response = self.client.post('/api/agenda/contratos/', contrato_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        contrato_id = response.data['id']
        contrato_numero = response.data['numero_contrato']
        
        # Verificar cálculos automáticos
        self.assertEqual(response.data['tiempo_total'], 5)  # 19:00 a 23:30 = 4.5 horas, redondeado a 5
        self.assertEqual(float(response.data['pago_total']), 1250.0)  # 250 * 5 = 1250
        self.assertEqual(response.data['estado_evento'], 'pending')  # Sin adelanto
        
        # 6. Agregar peticiones al contrato
        contrato_url = f'/api/agenda/contratos/{contrato_id}/'
        contrato_response = self.client.get(contrato_url)
        contrato_actual = contrato_response.data
        
        # Actualizar con peticiones
        contrato_actual['peticiones_cliente'] = [peticion1_id, peticion2_id]
        
        response = self.client.put(contrato_url, contrato_actual, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 7. Confirmar contrato con adelanto
        confirmar_url = f'/api/agenda/contratos/{contrato_id}/confirmar/'
        adelanto_data = {'adelanto': 500}
        
        response = self.client.post(confirmar_url, adelanto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado_evento'], 'confirmed')
        self.assertEqual(float(response.data['pago_adelanto']), 500.0)
        self.assertEqual(float(response.data['pago_restante']), 750.0)
        
        # 8. Verificar estadísticas actualizadas
        stats_response = self.client.get('/api/agenda/contratos/estadisticas/')
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stats_response.data['confirmados'], 1)
        
        # 9. Verificar que aparece en próximos eventos
        proximos_response = self.client.get('/api/agenda/contratos/proximos_eventos/')
        self.assertEqual(proximos_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(proximos_response.data), 1)
        self.assertEqual(proximos_response.data[0]['titulo'], 'Aniversario de Bodas Carlos y María')
    
    def test_flujo_conflicto_horarios(self):
        """Prueba el flujo de manejo de conflictos de horarios"""
        
        fecha_evento = date.today() + timedelta(days=30)
        
        # 1. Crear primer contrato
        contrato1_data = {
            'titulo': 'Primer Evento',
            'tipo_evento': 'birthday',
            'nombre_festejado': 'Juan',
            'fecha_evento': fecha_evento,
            'hora_inicio': '20:00:00',
            'hora_final': '23:00:00',
            'costo_hora': '150.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Lugar 1',
            'google_maps_url': 'https://maps.google.com/lugar1',
            'audiencia': 50
        }
        
        response1 = self.client.post('/api/agenda/contratos/', contrato1_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # 2. Intentar crear contrato con solapamiento
        contrato2_data = {
            'titulo': 'Evento Conflictivo',
            'tipo_evento': 'wedding',
            'nombre_festejado': 'María',
            'fecha_evento': fecha_evento,
            'hora_inicio': '22:00:00',  # Se solapa con el anterior
            'hora_final': '23:59:00',
            'costo_hora': '200.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Lugar 2',
            'google_maps_url': 'https://maps.google.com/lugar2',
            'audiencia': 70
        }
        
        response2 = self.client.post('/api/agenda/contratos/', contrato2_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Conflicto de horarios', str(response2.data))
        
        # 3. Crear contrato válido con separación adecuada
        contrato3_data = {
            'titulo': 'Evento Válido',
            'tipo_evento': 'graduation',
            'nombre_festejado': 'Ana',
            'fecha_evento': fecha_evento,
            'hora_inicio': '00:00:00',  # 1 hora después del primer evento
            'hora_final': '02:00:00',   # Termina a las 2 AM del día siguiente
            'costo_hora': '180.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Lugar 3',
            'google_maps_url': 'https://maps.google.com/lugar3',
            'audiencia': 60
        }
        
        response3 = self.client.post('/api/agenda/contratos/', contrato3_data, format='json')
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response3.data['tiempo_total'], 2)  # 24:00 a 02:00 = 2 horas
    
    def test_flujo_cancelacion_y_restauracion(self):
        """Prueba el flujo de cancelación y posible restauración"""
        
        # 1. Crear contrato
        contrato = self.crear_contrato(titulo='Evento a Cancelar')
        
        # 2. Confirmar contrato
        confirmar_url = f'/api/agenda/contratos/{contrato.id}/confirmar/'
        response = self.client.post(confirmar_url, {'adelanto': 300}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado_evento'], 'confirmed')
        
        # 3. Cancelar contrato
        cancelar_url = f'/api/agenda/contratos/{contrato.id}/cancelar/'
        response = self.client.post(cancelar_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado_evento'], 'cancelled')
        
        # 4. Verificar que no aparece en próximos eventos
        proximos_response = self.client.get('/api/agenda/contratos/proximos_eventos/')
        self.assertEqual(len(proximos_response.data), 0)
        
        # 5. Verificar estadísticas
        stats_response = self.client.get('/api/agenda/contratos/estadisticas/')
        self.assertEqual(stats_response.data['cancelados'], 1)
    
    def test_flujo_busqueda_y_filtros(self):
        """Prueba el flujo de búsqueda y filtros en diferentes endpoints"""
        
        # Crear datos de prueba variados
        cliente2 = self.crear_cliente(
            nombre_cliente='Ana García',
            telefono_cliente='555666777'
        )
        
        # Contratos con diferentes características
        contrato1 = self.crear_contrato(
            titulo='Cumpleaños de Pedro',
            tipo_evento='birthday',
            fecha_evento=date.today() + timedelta(days=15)
        )
        
        contrato2 = self.crear_contrato(
            titulo='Boda de Ana y Luis',
            tipo_evento='wedding',
            cliente=cliente2,
            fecha_evento=date.today() + timedelta(days=25)
        )
        
        # 1. Buscar contratos por título
        response = self.client.get('/api/agenda/contratos/?search=Boda')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'Boda de Ana y Luis')
        
        # 2. Filtrar por tipo de evento
        response = self.client.get('/api/agenda/contratos/?tipo_evento=birthday')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo_evento'], 'birthday')
        
        # 3. Filtrar por cliente
        response = self.client.get(f'/api/agenda/contratos/?cliente={cliente2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['cliente'], cliente2.id)
        
        # 4. Buscar clientes
        response = self.client.get('/api/agenda/clientes/?search=Ana')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_cliente'], 'Ana García')
        
        # 5. Filtrar equipos por precio
        response = self.client.get('/api/agenda/equipos-audio/por_precio/?precio_min=1000&precio_max=2000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Solo el equipo JBL
    
    def test_flujo_actualizacion_masiva(self):
        """Prueba actualizaciones que afectan múltiples registros"""
        
        # Crear múltiples contratos
        contratos = []
        for i in range(3):
            contrato = self.crear_contrato(
                titulo=f'Evento {i+1}',
                fecha_evento=date.today() + timedelta(days=20+i*10)
            )
            contratos.append(contrato)
        
        # Confirmar todos los contratos
        for contrato in contratos:
            confirmar_url = f'/api/agenda/contratos/{contrato.id}/confirmar/'
            response = self.client.post(confirmar_url, {'adelanto': 200}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estadísticas
        stats_response = self.client.get('/api/agenda/contratos/estadisticas/')
        self.assertEqual(stats_response.data['confirmados'], 3)
        self.assertEqual(stats_response.data['total_contratos'], 3)
        
        # Verificar próximos eventos
        proximos_response = self.client.get('/api/agenda/contratos/proximos_eventos/')
        self.assertEqual(len(proximos_response.data), 3)


class DatabaseIntegrityTest(TransactionTestCase):
    """Pruebas de integridad de base de datos"""
    
    def test_transaccion_rollback_en_error(self):
        """Prueba que las transacciones se revierten correctamente en caso de error"""
        
        # Crear cliente válido
        cliente = Cliente.objects.create(
            nombre_cliente='Cliente Test',
            telefono_cliente='123456789',
            frecuencia=1
        )
        
        initial_count = Contrato.objects.count()
        
        try:
            with transaction.atomic():
                # Crear contrato válido
                contrato = Contrato.objects.create(
                    titulo='Contrato Test',
                    tipo_evento='birthday',
                    nombre_festejado='Test',
                    fecha_evento=date.today() + timedelta(days=30),
                    hora_inicio=time(20, 0),
                    hora_final=time(23, 0),
                    costo_hora=Decimal('150.00'),
                    cliente=cliente,
                    nombre_lugar='Lugar Test',
                    google_maps_url='https://maps.google.com/test',
                    audiencia=50
                )
                
                # Forzar un error (violación de integridad)
                # Intentar crear otro contrato con el mismo número
                contrato2 = Contrato(
                    numero_contrato=contrato.numero_contrato,  # Duplicado
                    titulo='Contrato Duplicado',
                    tipo_evento='wedding',
                    nombre_festejado='Test 2',
                    fecha_evento=date.today() + timedelta(days=31),
                    hora_inicio=time(19, 0),
                    hora_final=time(22, 0),
                    costo_hora=Decimal('200.00'),
                    cliente=cliente,
                    nombre_lugar='Lugar Test 2',
                    google_maps_url='https://maps.google.com/test2',
                    audiencia=60
                )
                contrato2.save()
                
        except Exception:
            # Se espera que falle
            pass
        
        # Verificar que no se creó ningún contrato
        final_count = Contrato.objects.count()
        self.assertEqual(initial_count, final_count)
    
    def test_soft_delete_integridad(self):
        """Prueba que el soft delete mantiene la integridad referencial"""
        
        # Crear cliente y contrato
        cliente = Cliente.objects.create(
            nombre_cliente='Cliente a Eliminar',
            telefono_cliente='987654321',
            frecuencia=1
        )
        
        contrato = Contrato.objects.create(
            titulo='Contrato con Cliente',
            tipo_evento='birthday',
            nombre_festejado='Test',
            fecha_evento=date.today() + timedelta(days=30),
            hora_inicio=time(20, 0),
            hora_final=time(23, 0),
            costo_hora=Decimal('150.00'),
            cliente=cliente,
            nombre_lugar='Lugar Test',
            google_maps_url='https://maps.google.com/test',
            audiencia=50
        )
        
        # Eliminar cliente (soft delete)
        cliente.delete()
        
        # El contrato debe seguir existiendo y referenciando al cliente
        contrato.refresh_from_db()
        self.assertIsNotNone(contrato.cliente)
        self.assertEqual(contrato.cliente.id, cliente.id)
        
        # Pero el cliente debe estar marcado como inactivo
        cliente.refresh_from_db()
        self.assertFalse(cliente.is_active)
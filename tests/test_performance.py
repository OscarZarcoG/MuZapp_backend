from django.test import TestCase, override_settings
from django.test.utils import override_settings
from django.db import connection
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from datetime import date, time, timedelta
from decimal import Decimal
import time as time_module
from unittest.mock import patch

from GIGS.models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Contrato
from .test_base import BaseTestCase


class QueryPerformanceTest(TestCase, BaseTestCase):
    """Pruebas de rendimiento de consultas a la base de datos"""
    
    def setUp(self):
        super().setUp()
        # Crear datos de prueba en cantidad
        self.crear_datos_masivos()
    
    def crear_datos_masivos(self):
        """Crea una cantidad significativa de datos para pruebas de rendimiento"""
        
        # Crear 50 clientes
        clientes = []
        for i in range(50):
            cliente = Cliente.objects.create(
                nombre_cliente=f'Cliente {i+1}',
                telefono_cliente=f'55512345{i:02d}',
                redes_sociales=f'https://facebook.com/cliente{i+1}',
                frecuencia=i % 5 + 1
            )
            clientes.append(cliente)
        
        # Crear 20 equipos de audio
        equipos = []
        marcas = ['JBL', 'Bose', 'Yamaha', 'Pioneer', 'Sony']
        for i in range(20):
            equipo = Equipo_Audio.objects.create(
                marca=marcas[i % len(marcas)],
                modelo=f'Modelo {i+1}',
                numero_bocinas=2 + (i % 4),
                descripcion=f'Descripción del equipo {i+1}',
                precio=1000 + (i * 100)
            )
            equipos.append(equipo)
        
        # Crear 30 servicios de catering
        caterings = []
        for i in range(30):
            catering = Catering.objects.create(
                peticion_grupo=f'Petición de catering {i+1}'
            )
            caterings.append(catering)
        
        # Crear 100 peticiones musicales
        peticiones = []
        for i in range(100):
            peticion = Peticion.objects.create(
                nombre_cancion=f'Canción {i+1}',
                link=f'https://youtube.com/cancion{i+1}' if i % 2 == 0 else None
            )
            peticiones.append(peticion)
        
        # Crear 200 contratos
        tipos_evento = ['birthday', 'wedding', 'anniversary', 'graduation', 'corporate']
        for i in range(200):
            fecha_evento = date.today() + timedelta(days=i)
            
            contrato = Contrato.objects.create(
                titulo=f'Evento {i+1}',
                tipo_evento=tipos_evento[i % len(tipos_evento)],
                nombre_festejado=f'Festejado {i+1}',
                fecha_evento=fecha_evento,
                hora_inicio=time(19 + (i % 4), 0),
                hora_final=time(22 + (i % 3), 30),
                costo_hora=Decimal(str(150 + (i % 10) * 25)),
                cliente=clientes[i % len(clientes)],
                equipo_audio=equipos[i % len(equipos)] if i % 3 == 0 else None,
                catering=caterings[i % len(caterings)] if i % 4 == 0 else None,
                nombre_lugar=f'Lugar {i+1}',
                descripcion_lugar=f'Descripción del lugar {i+1}',
                google_maps_url=f'https://maps.google.com/lugar{i+1}',
                audiencia=50 + (i % 100),
                oportunidades_descanso=i % 3,
                tiempo_descanso=15 + (i % 3) * 5,
                notas=f'Notas del evento {i+1}'
            )
            
            # Agregar algunas peticiones a algunos contratos
            if i % 5 == 0:
                peticiones_contrato = peticiones[i:i+3] if i+3 <= len(peticiones) else peticiones[i:]
                contrato.peticiones_cliente.set(peticiones_contrato)
        
        self.clientes = clientes
        self.equipos = equipos
        self.caterings = caterings
        self.peticiones = peticiones
    
    def test_consulta_contratos_con_relaciones(self):
        """Prueba el rendimiento de consultas con select_related y prefetch_related"""
        
        # Medir consulta sin optimización
        start_time = time_module.time()
        with self.assertNumQueries(201):  # 1 + 200 (N+1 problem)
            contratos = list(Contrato.objects.all())
            for contrato in contratos:
                _ = contrato.cliente.nombre_cliente
        end_time = time_module.time()
        tiempo_sin_optimizar = end_time - start_time
        
        # Medir consulta optimizada
        start_time = time_module.time()
        with self.assertNumQueries(1):  # Solo 1 consulta con select_related
            contratos_optimizados = list(
                Contrato.objects.select_related('cliente', 'equipo_audio', 'catering')
            )
            for contrato in contratos_optimizados:
                _ = contrato.cliente.nombre_cliente
                if contrato.equipo_audio:
                    _ = contrato.equipo_audio.marca
                if contrato.catering:
                    _ = contrato.catering.peticion_grupo
        end_time = time_module.time()
        tiempo_optimizado = end_time - start_time
        
        # La consulta optimizada debe ser significativamente más rápida
        self.assertLess(tiempo_optimizado, tiempo_sin_optimizar)
        
        # Verificar que obtenemos los mismos datos
        self.assertEqual(len(contratos), len(contratos_optimizados))
    
    def test_consulta_contratos_con_peticiones(self):
        """Prueba el rendimiento de consultas con ManyToMany usando prefetch_related"""
        
        # Obtener contratos que tienen peticiones
        contratos_con_peticiones = Contrato.objects.filter(
            peticiones_cliente__isnull=False
        ).distinct()
        
        if contratos_con_peticiones.exists():
            # Consulta sin optimización
            with self.assertNumQueries(41):  # 1 + 40 consultas adicionales
                contratos = list(contratos_con_peticiones)
                for contrato in contratos:
                    peticiones = list(contrato.peticiones_cliente.all())
            
            # Consulta optimizada
            with self.assertNumQueries(2):  # 1 para contratos + 1 para peticiones
                contratos_optimizados = list(
                    contratos_con_peticiones.prefetch_related('peticiones_cliente')
                )
                for contrato in contratos_optimizados:
                    peticiones = list(contrato.peticiones_cliente.all())
    
    def test_filtros_complejos_rendimiento(self):
        """Prueba el rendimiento de filtros complejos"""
        
        start_time = time_module.time()
        
        # Consulta compleja con múltiples filtros
        contratos_filtrados = Contrato.objects.filter(
            fecha_evento__gte=date.today(),
            fecha_evento__lte=date.today() + timedelta(days=30),
            cliente__frecuencia__gte=3,
            pago_total__gte=500
        ).select_related('cliente', 'equipo_audio').order_by('fecha_evento')
        
        resultados = list(contratos_filtrados)
        
        end_time = time_module.time()
        tiempo_consulta = end_time - start_time
        
        # La consulta debe completarse en menos de 1 segundo
        self.assertLess(tiempo_consulta, 1.0)
        
        # Verificar que los resultados son correctos
        for contrato in resultados:
            self.assertGreaterEqual(contrato.fecha_evento, date.today())
            self.assertLessEqual(
                contrato.fecha_evento, 
                date.today() + timedelta(days=30)
            )
            self.assertGreaterEqual(contrato.cliente.frecuencia, 3)
    
    def test_agregaciones_rendimiento(self):
        """Prueba el rendimiento de consultas con agregaciones"""
        
        from django.db.models import Count, Sum, Avg, Max, Min
        
        start_time = time_module.time()
        
        # Estadísticas complejas
        estadisticas = Contrato.objects.aggregate(
            total_contratos=Count('id'),
            total_ingresos=Sum('pago_total'),
            promedio_pago=Avg('pago_total'),
            pago_maximo=Max('pago_total'),
            pago_minimo=Min('pago_total')
        )
        
        # Contratos por tipo de evento
        contratos_por_tipo = Contrato.objects.values('tipo_evento').annotate(
            cantidad=Count('id'),
            ingresos_totales=Sum('pago_total')
        ).order_by('-cantidad')
        
        # Clientes más frecuentes
        clientes_frecuentes = Cliente.objects.annotate(
            num_contratos=Count('contrato')
        ).filter(num_contratos__gt=0).order_by('-num_contratos')[:10]
        
        end_time = time_module.time()
        tiempo_agregaciones = end_time - start_time
        
        # Las agregaciones deben completarse rápidamente
        self.assertLess(tiempo_agregaciones, 0.5)
        
        # Verificar que obtenemos resultados válidos
        self.assertIsNotNone(estadisticas['total_contratos'])
        self.assertGreater(estadisticas['total_contratos'], 0)
        
        self.assertGreater(len(list(contratos_por_tipo)), 0)
        self.assertGreater(len(list(clientes_frecuentes)), 0)


class APIPerformanceTest(APITestCase, BaseTestCase):
    """Pruebas de rendimiento de la API"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        # Crear algunos datos para las pruebas
        for i in range(20):
            cliente = self.crear_cliente(
                nombre_cliente=f'Cliente API {i+1}',
                telefono_cliente=f'55512345{i:02d}'
            )
            
            self.crear_contrato(
                titulo=f'Evento API {i+1}',
                cliente=cliente,
                fecha_evento=date.today() + timedelta(days=i+1)
            )
    
    def test_listado_contratos_rendimiento(self):
        """Prueba el rendimiento del endpoint de listado de contratos"""
        
        start_time = time_module.time()
        
        response = self.client.get('/api/agenda/contratos/')
        
        end_time = time_module.time()
        tiempo_respuesta = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_respuesta, 1.0)  # Menos de 1 segundo
        
        # Verificar que la respuesta contiene los datos esperados
        self.assertGreater(len(response.data), 0)
    
    def test_busqueda_contratos_rendimiento(self):
        """Prueba el rendimiento de búsqueda en contratos"""
        
        start_time = time_module.time()
        
        response = self.client.get('/api/agenda/contratos/?search=Evento')
        
        end_time = time_module.time()
        tiempo_respuesta = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_respuesta, 1.0)
        
        # Verificar que la búsqueda funciona
        for contrato in response.data:
            self.assertIn('Evento', contrato['titulo'])
    
    def test_filtros_multiples_rendimiento(self):
        """Prueba el rendimiento con múltiples filtros aplicados"""
        
        start_time = time_module.time()
        
        response = self.client.get(
            '/api/agenda/contratos/'
            '?tipo_evento=birthday'
            '&fecha_evento__gte=' + date.today().isoformat() +
            '&ordering=fecha_evento'
        )
        
        end_time = time_module.time()
        tiempo_respuesta = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_respuesta, 1.0)
    
    def test_estadisticas_rendimiento(self):
        """Prueba el rendimiento del endpoint de estadísticas"""
        
        start_time = time_module.time()
        
        response = self.client.get('/api/agenda/contratos/estadisticas/')
        
        end_time = time_module.time()
        tiempo_respuesta = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_respuesta, 0.5)  # Estadísticas deben ser muy rápidas
        
        # Verificar estructura de respuesta
        self.assertIn('total_contratos', response.data)
        self.assertIn('confirmados', response.data)
        self.assertIn('pendientes', response.data)
        self.assertIn('cancelados', response.data)
    
    def test_proximos_eventos_rendimiento(self):
        """Prueba el rendimiento del endpoint de próximos eventos"""
        
        start_time = time_module.time()
        
        response = self.client.get('/api/agenda/contratos/proximos_eventos/')
        
        end_time = time_module.time()
        tiempo_respuesta = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_respuesta, 0.5)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class CachePerformanceTest(TestCase, BaseTestCase):
    """Pruebas de rendimiento con caché"""
    
    def setUp(self):
        super().setUp()
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_cache_estadisticas(self):
        """Prueba que las estadísticas se cachean correctamente"""
        
        # Crear algunos contratos
        for i in range(10):
            self.crear_contrato(
                titulo=f'Contrato Cache {i+1}',
                fecha_evento=date.today() + timedelta(days=i+1)
            )
        
        from GIGS.views import ContratoViewSet
        viewset = ContratoViewSet()
        
        # Primera llamada - debe calcular y cachear
        start_time = time_module.time()
        estadisticas1 = viewset._get_estadisticas_cached()
        tiempo1 = time_module.time() - start_time
        
        # Segunda llamada - debe usar caché
        start_time = time_module.time()
        estadisticas2 = viewset._get_estadisticas_cached()
        tiempo2 = time_module.time() - start_time
        
        # La segunda llamada debe ser más rápida
        self.assertLess(tiempo2, tiempo1)
        
        # Los resultados deben ser iguales
        self.assertEqual(estadisticas1, estadisticas2)
    
    def test_invalidacion_cache(self):
        """Prueba que el caché se invalida correctamente"""
        
        from GIGS.views import ContratoViewSet
        viewset = ContratoViewSet()
        
        # Obtener estadísticas iniciales
        estadisticas_iniciales = viewset._get_estadisticas_cached()
        
        # Crear un nuevo contrato
        nuevo_contrato = self.crear_contrato(
            titulo='Contrato Invalidación',
            fecha_evento=date.today() + timedelta(days=5)
        )
        
        # Las estadísticas deben reflejar el cambio
        estadisticas_actualizadas = viewset._get_estadisticas_cached()
        
        self.assertNotEqual(
            estadisticas_iniciales['total_contratos'],
            estadisticas_actualizadas['total_contratos']
        )


class MemoryUsageTest(TestCase, BaseTestCase):
    """Pruebas de uso de memoria"""
    
    def test_consulta_grande_memoria(self):
        """Prueba que las consultas grandes no consuman memoria excesiva"""
        
        # Crear muchos registros
        clientes = []
        for i in range(100):
            cliente = Cliente(
                nombre_cliente=f'Cliente Memoria {i+1}',
                telefono_cliente=f'55512345{i:02d}',
                frecuencia=1
            )
            clientes.append(cliente)
        
        Cliente.objects.bulk_create(clientes)
        
        # Usar iterator() para consultas grandes
        contador = 0
        for cliente in Cliente.objects.iterator(chunk_size=10):
            contador += 1
        
        self.assertEqual(contador, 100)
    
    def test_bulk_operations(self):
        """Prueba que las operaciones en lote sean eficientes"""
        
        # Crear registros en lote
        start_time = time_module.time()
        
        peticiones = []
        for i in range(100):
            peticion = Peticion(
                nombre_cancion=f'Canción Bulk {i+1}',
                link=f'https://youtube.com/bulk{i+1}'
            )
            peticiones.append(peticion)
        
        Peticion.objects.bulk_create(peticiones)
        
        end_time = time_module.time()
        tiempo_bulk = end_time - start_time
        
        # Debe ser rápido
        self.assertLess(tiempo_bulk, 1.0)
        
        # Verificar que se crearon todos
        self.assertEqual(Peticion.objects.filter(nombre_cancion__startswith='Canción Bulk').count(), 100)
        
        # Actualización en lote
        start_time = time_module.time()
        
        Peticion.objects.filter(
            nombre_cancion__startswith='Canción Bulk'
        ).update(link='https://youtube.com/updated')
        
        end_time = time_module.time()
        tiempo_update = end_time - start_time
        
        self.assertLess(tiempo_update, 0.5)
        
        # Verificar actualización
        peticiones_actualizadas = Peticion.objects.filter(
            nombre_cancion__startswith='Canción Bulk',
            link='https://youtube.com/updated'
        ).count()
        
        self.assertEqual(peticiones_actualizadas, 100)
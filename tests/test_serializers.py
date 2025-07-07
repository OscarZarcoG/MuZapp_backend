from django.test import TestCase
from rest_framework.exceptions import ValidationError
from datetime import date, time, timedelta
from decimal import Decimal

from GIGS.serializers import (
    ClienteSerializer, EquipoAudioSerializer, CateringSerializer,
    PeticionSerializer, RepertorioSerializer, FotosEventoSerializer,
    ContratoSerializer, ContratoCreateSerializer, ContratoListSerializer
)
from GIGS.models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Contrato
from .test_base import BaseTestCase


class ClienteSerializerTest(BaseTestCase):
    """Pruebas para ClienteSerializer"""
    
    def test_serializar_cliente(self):
        """Prueba serializar un cliente existente"""
        serializer = ClienteSerializer(self.cliente)
        data = serializer.data
        
        self.assertEqual(data['nombre_cliente'], 'Juan Pérez')
        self.assertEqual(data['telefono_cliente'], '987654321')
        self.assertEqual(data['frecuencia'], 1)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_deserializar_cliente_valido(self):
        """Prueba deserializar datos válidos de cliente"""
        data = {
            'nombre_cliente': 'María García',
            'telefono_cliente': '999888777',
            'redes_sociales': 'https://instagram.com/maria',
            'frecuencia': 3
        }
        
        serializer = ClienteSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        cliente = serializer.save()
        self.assertEqual(cliente.nombre_cliente, 'María García')
        self.assertEqual(cliente.frecuencia, 3)
    
    def test_deserializar_cliente_datos_faltantes(self):
        """Prueba deserializar con datos faltantes"""
        data = {
            'nombre_cliente': 'Cliente Incompleto'
            # Falta telefono_cliente y frecuencia
        }
        
        serializer = ClienteSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('frecuencia', serializer.errors)
    
    def test_actualizar_cliente(self):
        """Prueba actualizar un cliente existente"""
        data = {
            'nombre_cliente': 'Juan Pérez Actualizado',
            'telefono_cliente': '111222333',
            'frecuencia': 5
        }
        
        serializer = ClienteSerializer(self.cliente, data=data)
        self.assertTrue(serializer.is_valid())
        
        cliente_actualizado = serializer.save()
        self.assertEqual(cliente_actualizado.nombre_cliente, 'Juan Pérez Actualizado')
        self.assertEqual(cliente_actualizado.frecuencia, 5)


class EquipoAudioSerializerTest(BaseTestCase):
    """Pruebas para EquipoAudioSerializer"""
    
    def test_serializar_equipo_audio(self):
        """Prueba serializar un equipo de audio"""
        serializer = EquipoAudioSerializer(self.equipo_audio)
        data = serializer.data
        
        self.assertEqual(data['marca'], 'JBL')
        self.assertEqual(data['modelo'], 'EON615')
        self.assertEqual(data['numero_bocinas'], 2)
        self.assertEqual(data['precio'], 1500)
    
    def test_deserializar_equipo_valido(self):
        """Prueba deserializar datos válidos de equipo"""
        data = {
            'marca': 'Yamaha',
            'modelo': 'DXR12',
            'numero_bocinas': 4,
            'descripcion': 'Equipo profesional de alta calidad',
            'precio': 2500
        }
        
        serializer = EquipoAudioSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        equipo = serializer.save()
        self.assertEqual(equipo.marca, 'Yamaha')
        self.assertEqual(equipo.precio, 2500)
    
    def test_precio_negativo(self):
        """Prueba que no se permita precio negativo"""
        data = {
            'marca': 'Test',
            'modelo': 'Test',
            'numero_bocinas': 2,
            'descripcion': 'Test',
            'precio': -100
        }
        
        serializer = EquipoAudioSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # La validación de precio negativo se maneja en el modelo


class ContratoSerializerTest(BaseTestCase):
    """Pruebas para ContratoSerializer"""
    
    def test_serializar_contrato(self):
        """Prueba serializar un contrato existente"""
        contrato = self.crear_contrato()
        serializer = ContratoSerializer(contrato)
        data = serializer.data
        
        self.assertEqual(data['titulo'], 'Cumpleaños de Juan')
        self.assertEqual(data['cliente_nombre'], 'Juan Pérez')
        self.assertEqual(data['tipo_evento'], 'birthday')
        self.assertIn('numero_contrato', data)
        self.assertIn('tiempo_total', data)
        self.assertIn('pago_total', data)
    
    def test_campos_solo_lectura(self):
        """Prueba que los campos calculados sean de solo lectura"""
        contrato = self.crear_contrato()
        serializer = ContratoSerializer(contrato)
        
        # Estos campos deben estar en read_only_fields
        read_only_fields = serializer.Meta.read_only_fields
        self.assertIn('numero_contrato', read_only_fields)
        self.assertIn('tiempo_total', read_only_fields)
        self.assertIn('pago_total', read_only_fields)
        self.assertIn('pago_restante', read_only_fields)
        self.assertIn('porcentaje', read_only_fields)


class ContratoCreateSerializerTest(BaseTestCase):
    """Pruebas para ContratoCreateSerializer"""
    
    def test_crear_contrato_valido(self):
        """Prueba crear un contrato con datos válidos"""
        data = {
            'titulo': 'Boda de Ana y Carlos',
            'tipo_evento': 'wedding',
            'nombre_festejado': 'Ana y Carlos',
            'fecha_evento': date.today() + timedelta(days=60),
            'hora_inicio': '19:00:00',
            'hora_final': '23:00:00',
            'costo_hora': '200.00',
            'pago_adelanto': '400.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Iglesia San José',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 100
        }
        
        serializer = ContratoCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        contrato = serializer.save()
        self.assertEqual(contrato.titulo, 'Boda de Ana y Carlos')
        self.assertEqual(contrato.tipo_evento, 'wedding')
        self.assertEqual(contrato.tiempo_total, 4)  # 19:00 a 23:00 = 4 horas
        self.assertEqual(contrato.estado_evento, 'confirmed')  # Porque tiene adelanto
    
    def test_validacion_horas_iguales(self):
        """Prueba validación de horas de inicio y fin iguales"""
        data = {
            'titulo': 'Evento Inválido',
            'tipo_evento': 'birthday',
            'nombre_festejado': 'Test',
            'fecha_evento': date.today() + timedelta(days=30),
            'hora_inicio': '20:00:00',
            'hora_final': '20:00:00',  # Igual a hora_inicio
            'costo_hora': '150.00',
            'cliente': self.cliente.id,
            'nombre_lugar': 'Lugar Test',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 50
        }
        
        serializer = ContratoCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('hora_final', serializer.errors)
    
    def test_validacion_valores_negativos(self):
        """Prueba validación de valores monetarios negativos"""
        data = {
            'titulo': 'Evento con Valores Negativos',
            'tipo_evento': 'birthday',
            'nombre_festejado': 'Test',
            'fecha_evento': date.today() + timedelta(days=30),
            'hora_inicio': '20:00:00',
            'hora_final': '23:00:00',
            'costo_hora': '-150.00',  # Negativo
            'pago_adelanto': '-100.00',  # Negativo
            'cliente': self.cliente.id,
            'nombre_lugar': 'Lugar Test',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 50
        }
        
        serializer = ContratoCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('costo_hora', serializer.errors)
        self.assertIn('pago_adelanto', serializer.errors)
    
    def test_validacion_conflictos_horarios(self):
        """Prueba validación de conflictos de horarios en serializer"""
        # Crear primer contrato
        fecha_evento = date.today() + timedelta(days=45)
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
        
        serializer = ContratoCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # La validación de conflictos debe aparecer en los errores
        self.assertTrue(any('conflicto' in str(error).lower() for error in serializer.errors.values()))
    
    def test_crear_contrato_con_relaciones(self):
        """Prueba crear contrato con relaciones a otros modelos"""
        data = {
            'titulo': 'Evento Completo',
            'tipo_evento': 'birthday',
            'nombre_festejado': 'Festejado Test',
            'fecha_evento': date.today() + timedelta(days=40),
            'hora_inicio': '18:00:00',
            'hora_final': '22:00:00',
            'costo_hora': '180.00',
            'pago_adelanto': '300.00',
            'cliente': self.cliente.id,
            'equipo_audio': self.equipo_audio.id,
            'catering': self.catering.id,
            'nombre_lugar': 'Lugar Completo',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 70,
            'oportunidades_descanso': 2,
            'tiempo_descanso': 15,
            'notas': 'Evento con todas las relaciones'
        }
        
        serializer = ContratoCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        contrato = serializer.save()
        self.assertEqual(contrato.cliente, self.cliente)
        self.assertEqual(contrato.equipo_audio, self.equipo_audio)
        self.assertEqual(contrato.catering, self.catering)
        self.assertEqual(contrato.tiempo_total, 4)  # 18:00 a 22:00


class ContratoListSerializerTest(BaseTestCase):
    """Pruebas para ContratoListSerializer"""
    
    def test_serializar_lista_contratos(self):
        """Prueba serializar una lista de contratos"""
        contrato1 = self.crear_contrato(titulo='Contrato 1')
        contrato2 = self.crear_contrato(
            titulo='Contrato 2',
            fecha_evento=date.today() + timedelta(days=35)
        )
        
        contratos = [contrato1, contrato2]
        serializer = ContratoListSerializer(contratos, many=True)
        data = serializer.data
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['titulo'], 'Contrato 1')
        self.assertEqual(data[1]['titulo'], 'Contrato 2')
        
        # Verificar que incluye información del cliente
        self.assertEqual(data[0]['cliente_nombre'], 'Juan Pérez')
        self.assertEqual(data[1]['cliente_nombre'], 'Juan Pérez')


class PeticionSerializerTest(BaseTestCase):
    """Pruebas para PeticionSerializer"""
    
    def test_serializar_peticion(self):
        """Prueba serializar una petición"""
        serializer = PeticionSerializer(self.peticion1)
        data = serializer.data
        
        self.assertEqual(data['nombre_cancion'], 'La Vida es una Fiesta')
        self.assertEqual(data['link'], 'https://youtube.com/watch?v=123')
    
    def test_crear_peticion_sin_link(self):
        """Prueba crear petición sin link (campo opcional)"""
        data = {
            'nombre_cancion': 'Canción sin Link'
        }
        
        serializer = PeticionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        peticion = serializer.save()
        self.assertEqual(peticion.nombre_cancion, 'Canción sin Link')
        self.assertIsNone(peticion.link)
    
    def test_crear_peticion_con_link_invalido(self):
        """Prueba crear petición con URL inválida"""
        data = {
            'nombre_cancion': 'Canción con Link Inválido',
            'link': 'esto-no-es-una-url'
        }
        
        serializer = PeticionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('link', serializer.errors)


class RepertorioSerializerTest(BaseTestCase):
    """Pruebas para RepertorioSerializer"""
    
    def test_serializar_repertorio(self):
        """Prueba serializar repertorio"""
        serializer = RepertorioSerializer(self.repertorio)
        data = serializer.data
        
        self.assertEqual(data['nombre_cancion'], 'Música Variada')
    
    def test_crear_repertorio(self):
        """Prueba crear nuevo repertorio"""
        data = {
            'nombre_cancion': 'Rock Nacional'
        }
        
        serializer = RepertorioSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        repertorio = serializer.save()
        self.assertEqual(repertorio.nombre_cancion, 'Rock Nacional')


class CateringSerializerTest(BaseTestCase):
    """Pruebas para CateringSerializer"""
    
    def test_serializar_catering(self):
        """Prueba serializar catering"""
        serializer = CateringSerializer(self.catering)
        data = serializer.data
        
        self.assertEqual(data['peticion_grupo'], 'Bebidas y snacks para el grupo')
    
    def test_crear_catering(self):
        """Prueba crear nuevo catering"""
        data = {
            'peticion_grupo': 'Menú vegetariano para 40 personas'
        }
        
        serializer = CateringSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        catering = serializer.save()
        self.assertEqual(catering.peticion_grupo, 'Menú vegetariano para 40 personas')
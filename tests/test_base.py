from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time, timedelta
from GIGS.models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato


class BaseTestCase(TestCase):
    """Clase base para todas las pruebas con datos de prueba comunes"""
    
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            nombre_cliente="Juan Pérez",
            telefono_cliente="987654321",
            redes_sociales="https://facebook.com/juan",
            frecuencia=1
        )
        
        # Crear equipo de audio de prueba
        self.equipo_audio = Equipo_Audio.objects.create(
            marca="JBL",
            modelo="EON615",
            numero_bocinas=2,
            descripcion="Equipo profesional para eventos",
            precio=1500
        )
        
        # Crear catering de prueba
        self.catering = Catering.objects.create(
            peticion_grupo="Bebidas y snacks para el grupo"
        )
        
        # Crear peticiones de prueba
        self.peticion1 = Peticion.objects.create(
            nombre_cancion="La Vida es una Fiesta",
            link="https://youtube.com/watch?v=123"
        )
        
        self.peticion2 = Peticion.objects.create(
            nombre_cancion="Feliz Cumpleaños"
        )
        
        # Crear repertorio de prueba
        self.repertorio = Repertorio.objects.create(
            nombre_cancion="Música Variada"
        )
        
        # Datos base para contratos
        self.contrato_data = {
            'titulo': 'Cumpleaños de Juan',
            'tipo_evento': 'birthday',
            'nombre_festejado': 'Juan Pérez',
            'fecha_evento': date.today() + timedelta(days=30),
            'hora_inicio': time(20, 0),
            'hora_final': time(23, 0),
            'costo_hora': 150.00,
            'pago_adelanto': 0.00,
            'cliente': self.cliente,
            'nombre_lugar': 'Salón Los Jardines',
            'descripcion_lugar': 'Salón amplio con jardín',
            'google_maps_url': 'https://maps.google.com/test',
            'audiencia': 50,
            'equipo_audio': self.equipo_audio,
            'catering': self.catering,
            'oportunidades_descanso': 2,
            'tiempo_descanso': 15,
            'notas': 'Evento especial'
        }
    
    def crear_contrato(self, **kwargs):
        """Helper para crear contratos con datos personalizados"""
        data = self.contrato_data.copy()
        data.update(kwargs)
        contrato = Contrato.objects.create(**data)
        contrato.peticiones_cliente.add(self.peticion1, self.peticion2)
        return contrato
    
    def crear_cliente(self, **kwargs):
        """Helper para crear clientes con datos personalizados"""
        defaults = {
            'nombre_cliente': 'Cliente Test',
            'telefono_cliente': '123456789',
            'frecuencia': 1
        }
        defaults.update(kwargs)
        return Cliente.objects.create(**defaults)
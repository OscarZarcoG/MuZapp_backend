from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, time, timedelta
from decimal import Decimal
from GIGS.models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato
from .test_base import BaseTestCase


class ClienteModelTest(BaseTestCase):
    """Pruebas para el modelo Cliente"""
    
    def test_crear_cliente(self):
        """Prueba la creación de un cliente"""
        cliente = self.crear_cliente(
            nombre_cliente="María García",
            telefono_cliente="987654321",
            frecuencia=2
        )
        
        self.assertEqual(cliente.nombre_cliente, "María García")
        self.assertEqual(cliente.telefono_cliente, "987654321")
        self.assertEqual(cliente.frecuencia, 2)
        self.assertTrue(cliente.is_active)
        self.assertIsNotNone(cliente.created_at)
    
    def test_str_cliente(self):
        """Prueba la representación string del cliente"""
        self.assertEqual(str(self.cliente), "Juan Pérez")
    
    def test_soft_delete_cliente(self):
        """Prueba el borrado suave del cliente"""
        cliente_id = self.cliente.id
        self.cliente.delete()
        
        # El cliente debe seguir existiendo pero marcado como inactivo
        cliente = Cliente.objects.get(id=cliente_id)
        self.assertFalse(cliente.is_active)
        self.assertIsNotNone(cliente.deleted_at)
    
    def test_restore_cliente(self):
        """Prueba la restauración de un cliente eliminado"""
        self.cliente.delete()
        self.cliente.restore()
        
        self.assertTrue(self.cliente.is_active)
        self.assertIsNone(self.cliente.deleted_at)


class EquipoAudioModelTest(BaseTestCase):
    """Pruebas para el modelo Equipo_Audio"""
    
    def test_crear_equipo_audio(self):
        """Prueba la creación de un equipo de audio"""
        equipo = Equipo_Audio.objects.create(
            marca="Yamaha",
            modelo="DXR12",
            numero_bocinas=4,
            descripcion="Equipo profesional",
            precio=2000
        )
        
        self.assertEqual(equipo.marca, "Yamaha")
        self.assertEqual(equipo.modelo, "DXR12")
        self.assertEqual(equipo.numero_bocinas, 4)
        self.assertEqual(equipo.precio, 2000)
    
    def test_str_equipo_audio(self):
        """Prueba la representación string del equipo"""
        self.assertEqual(str(self.equipo_audio), "JBL EON615")
    
    def test_precio_negativo(self):
        """Prueba que no se permita precio negativo"""
        with self.assertRaises(ValidationError):
            equipo = Equipo_Audio(
                marca="Test",
                modelo="Test",
                numero_bocinas=2,
                descripcion="Test",
                precio=-100
            )
            equipo.full_clean()


class ContratoModelTest(BaseTestCase):
    """Pruebas para el modelo Contrato"""
    
    def test_crear_contrato_basico(self):
        """Prueba la creación básica de un contrato"""
        contrato = self.crear_contrato()
        
        self.assertEqual(contrato.titulo, 'Cumpleaños de Juan')
        self.assertEqual(contrato.cliente, self.cliente)
        self.assertEqual(contrato.tipo_evento, 'birthday')
        self.assertTrue(contrato.numero_contrato)
        self.assertEqual(contrato.estado_evento, 'pending')
    
    def test_generar_numero_contrato(self):
        """Prueba la generación automática del número de contrato"""
        contrato1 = self.crear_contrato()
        contrato2 = self.crear_contrato(
            fecha_evento=date.today() + timedelta(days=31)
        )
        
        # Los números deben ser únicos y seguir el formato YYYYMMDD-NNNN
        self.assertNotEqual(contrato1.numero_contrato, contrato2.numero_contrato)
        self.assertRegex(contrato1.numero_contrato, r'\d{8}-\d{4}')
        self.assertRegex(contrato2.numero_contrato, r'\d{8}-\d{4}')
    
    def test_calcular_tiempo_total(self):
        """Prueba el cálculo del tiempo total del evento"""
        # Evento de 3 horas exactas
        contrato = self.crear_contrato(
            hora_inicio=time(20, 0),
            hora_final=time(23, 0)
        )
        self.assertEqual(contrato.tiempo_total, 3)
        
        # Evento con 30 minutos extra (no debe redondear)
        contrato2 = self.crear_contrato(
            hora_inicio=time(20, 0),
            hora_final=time(23, 30),
            fecha_evento=date.today() + timedelta(days=32)
        )
        self.assertEqual(contrato2.tiempo_total, 3)
        
        # Evento con 45 minutos extra (debe redondear hacia arriba)
        contrato3 = self.crear_contrato(
            hora_inicio=time(20, 0),
            hora_final=time(23, 45),
            fecha_evento=date.today() + timedelta(days=33)
        )
        self.assertEqual(contrato3.tiempo_total, 4)
    
    def test_calcular_tiempo_total_cruzando_medianoche(self):
        """Prueba el cálculo cuando el evento cruza medianoche"""
        contrato = self.crear_contrato(
            hora_inicio=time(22, 0),
            hora_final=time(2, 0)  # Al día siguiente
        )
        self.assertEqual(contrato.tiempo_total, 4)
    
    def test_calcular_pagos(self):
        """Prueba los cálculos financieros"""
        contrato = self.crear_contrato(
            costo_hora=Decimal('150.00'),
            pago_adelanto=Decimal('200.00'),
            costo_extra=Decimal('50.00')
        )
        
        # Tiempo total: 3 horas, costo_hora: 150, costo_extra: 50
        # pago_total = (150 * 3) + 50 = 500
        self.assertEqual(contrato.pago_total, Decimal('500.00'))
        
        # pago_restante = 500 - 200 = 300
        self.assertEqual(contrato.pago_restante, Decimal('300.00'))
        
        # porcentaje = (200 / 500) * 100 = 40%
        self.assertEqual(contrato.porcentaje, Decimal('40.00'))
    
    def test_validacion_horas_iguales(self):
        """Prueba que no se permitan horas de inicio y fin iguales"""
        with self.assertRaises(ValidationError):
            contrato = Contrato(
                **{**self.contrato_data, 
                   'hora_inicio': time(20, 0),
                   'hora_final': time(20, 0)}
            )
            contrato.full_clean()
    
    def test_validacion_conflictos_horarios(self):
        """Prueba la validación de conflictos de horarios"""
        # Crear primer contrato
        fecha_evento = date.today() + timedelta(days=35)
        contrato1 = self.crear_contrato(
            fecha_evento=fecha_evento,
            hora_inicio=time(20, 0),
            hora_final=time(23, 0)
        )
        
        # Intentar crear contrato con solapamiento
        with self.assertRaises(ValidationError):
            contrato2 = Contrato(
                **{**self.contrato_data,
                   'fecha_evento': fecha_evento,
                   'hora_inicio': time(22, 0),  # Se solapa con el anterior
                   'hora_final': time(23, 59)}
            )
            contrato2.full_clean()
    
    def test_validacion_separacion_minima(self):
        """Prueba la validación de separación mínima entre eventos"""
        fecha_evento = date.today() + timedelta(days=36)
        
        # Crear primer contrato
        contrato1 = self.crear_contrato(
            fecha_evento=fecha_evento,
            hora_inicio=time(20, 0),
            hora_final=time(23, 0)
        )
        
        # Intentar crear contrato con menos de 1 hora de separación
        with self.assertRaises(ValidationError):
            contrato2 = Contrato(
                **{**self.contrato_data,
                   'fecha_evento': fecha_evento,
                   'hora_inicio': time(23, 30),  # Solo 30 minutos después
                   'hora_final': time(23, 59)}
            )
            contrato2.full_clean()
    
    def test_eventos_separados_correctamente(self):
        """Prueba que eventos con separación correcta se permitan"""
        fecha_evento = date.today() + timedelta(days=37)
        
        # Crear primer contrato
        contrato1 = self.crear_contrato(
            fecha_evento=fecha_evento,
            hora_inicio=time(20, 0),
            hora_final=time(23, 0)
        )
        
        # Crear segundo contrato con separación adecuada
        contrato2 = self.crear_contrato(
            fecha_evento=fecha_evento,
            hora_inicio=time(0, 0),   # 1 hora después (medianoche)
            hora_final=time(2, 0),    # Termina a las 2 AM del día siguiente
            titulo="Evento Nocturno"
        )
        
        self.assertIsNotNone(contrato2.id)
        self.assertEqual(contrato2.tiempo_total, 2)
    
    def test_actualizar_estado_evento(self):
        """Prueba la actualización automática del estado del evento"""
        # Contrato sin adelanto debe estar pendiente
        contrato = self.crear_contrato(pago_adelanto=Decimal('0.00'))
        self.assertEqual(contrato.estado_evento, 'pending')
        
        # Contrato con adelanto debe estar confirmado
        contrato.pago_adelanto = Decimal('200.00')
        contrato.save()
        self.assertEqual(contrato.estado_evento, 'confirmed')
    
    def test_str_contrato(self):
        """Prueba la representación string del contrato"""
        contrato = self.crear_contrato()
        expected = f"Contrato {contrato.numero_contrato} - Cumpleaños de Juan"
        self.assertEqual(str(contrato), expected)


class PeticionModelTest(BaseTestCase):
    """Pruebas para el modelo Peticion"""
    
    def test_crear_peticion(self):
        """Prueba la creación de una petición"""
        peticion = Peticion.objects.create(
            nombre_cancion="Canción de Prueba",
            link="https://youtube.com/test"
        )
        
        self.assertEqual(peticion.nombre_cancion, "Canción de Prueba")
        self.assertEqual(peticion.link, "https://youtube.com/test")
    
    def test_peticion_sin_link(self):
        """Prueba crear petición sin link (opcional)"""
        peticion = Peticion.objects.create(
            nombre_cancion="Canción sin Link"
        )
        
        self.assertEqual(peticion.nombre_cancion, "Canción sin Link")
        self.assertIsNone(peticion.link)


class RepertorioModelTest(BaseTestCase):
    """Pruebas para el modelo Repertorio"""
    
    def test_crear_repertorio(self):
        """Prueba la creación de repertorio"""
        repertorio = Repertorio.objects.create(
            nombre_cancion="Música Clásica"
        )
        
        self.assertEqual(repertorio.nombre_cancion, "Música Clásica")
        self.assertEqual(str(repertorio), "Música Clásica")


class CateringModelTest(BaseTestCase):
    """Pruebas para el modelo Catering"""
    
    def test_crear_catering(self):
        """Prueba la creación de catering"""
        catering = Catering.objects.create(
            peticion_grupo="Comida vegetariana para 50 personas"
        )
        
        self.assertEqual(catering.peticion_grupo, "Comida vegetariana para 50 personas")
        self.assertEqual(str(catering), "Comida vegetariana para 50 personas")
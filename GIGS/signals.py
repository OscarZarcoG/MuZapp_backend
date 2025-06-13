from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Contrato


@receiver(pre_save, sender=Contrato)
def actualizar_campos_calculados(sender, instance, **kwargs):
    """Actualizar campos calculados antes de guardar"""
    # Solo actualizar si es una instancia nueva o si han cambiado los campos relevantes
    if instance.pk:
        try:
            old_instance = Contrato.objects.get(pk=instance.pk)
            # Verificar si han cambiado los campos que afectan los cálculos
            campos_cambiados = (
                old_instance.hora_inicio != instance.hora_inicio or
                old_instance.hora_final != instance.hora_final or
                old_instance.costo_hora != instance.costo_hora or
                old_instance.pago_adelanto != instance.pago_adelanto or
                old_instance.costo_extra != instance.costo_extra
            )
            
            if not campos_cambiados:
                return
        except Contrato.DoesNotExist:
            pass
    
    # Calcular tiempo total
    if instance.hora_inicio and instance.hora_final:
        instance.tiempo_total = instance.calcular_tiempo_total()
    
    # Calcular valores financieros
    if instance.costo_hora and instance.tiempo_total:
        instance.pago_total = instance.calcular_pago_total()
        instance.pago_restante = instance.calcular_pago_restante()
        instance.porcentaje = instance.calcular_porcentaje()


@receiver(post_save, sender=Contrato)
def generar_numero_contrato(sender, instance, created, **kwargs):
    """Generar número de contrato si es una nueva instancia"""
    if created and not instance.numero_contrato:
        instance.numero_contrato = instance.generar_numero_contrato()
        # Usar update para evitar recursión infinita
        Contrato.objects.filter(pk=instance.pk).update(
            numero_contrato=instance.numero_contrato
        )


@receiver(post_save, sender=Contrato)
def log_cambio_estado(sender, instance, created, **kwargs):
    """Registrar cambios de estado del contrato"""
    if not created:
        try:
            # Obtener la instancia anterior para comparar
            old_instance = Contrato.objects.get(pk=instance.pk)
            if hasattr(old_instance, '_state_before_save'):
                old_estado = old_instance._state_before_save
                if old_estado != instance.estado_evento:
                    # Aquí podrías agregar logging o notificaciones
                    print(f"Contrato {instance.numero_contrato} cambió de {old_estado} a {instance.estado_evento}")
        except Contrato.DoesNotExist:
            pass


# Función para actualizar estados automáticamente (se puede ejecutar con un cron job)
def actualizar_estados_contratos():
    """Función para actualizar automáticamente los estados de los contratos"""
    from django.utils import timezone
    ahora = timezone.now()
    
    # Contratos que deberían estar en progreso
    contratos_en_progreso = Contrato.objects.filter(
        fecha_evento=ahora.date(),
        hora_inicio__lte=ahora.time(),
        hora_final__gte=ahora.time(),
        estado_evento__in=['confirmed', 'pending']
    )
    
    for contrato in contratos_en_progreso:
        contrato.estado_evento = 'in_progress'
        contrato.save()
    
    # Contratos que deberían estar completados
    contratos_completados = Contrato.objects.filter(
        fecha_evento__lt=ahora.date(),
        estado_evento__in=['confirmed', 'in_progress']
    )
    
    # También verificar contratos del día actual que ya terminaron
    contratos_hoy_terminados = Contrato.objects.filter(
        fecha_evento=ahora.date(),
        hora_final__lt=ahora.time(),
        estado_evento='in_progress'
    )
    
    for contrato in contratos_completados.union(contratos_hoy_terminados):
        contrato.estado_evento = 'completed'
        contrato.save()
    
    print(f"Estados actualizados: {contratos_en_progreso.count()} en progreso, {contratos_completados.count() + contratos_hoy_terminados.count()} completados")


# Comando de management para ejecutar la actualización
# Crear archivo: management/commands/actualizar_estados.py
ACTUALIZAR_ESTADOS_COMMAND = '''
from django.core.management.base import BaseCommand
from GIGS.signals import actualizar_estados_contratos

class Command(BaseCommand):
    help = 'Actualiza automáticamente los estados de los contratos'
    
    def handle(self, *args, **options):
        actualizar_estados_contratos()
        self.stdout.write(
            self.style.SUCCESS('Estados de contratos actualizados exitosamente')
        )
'''
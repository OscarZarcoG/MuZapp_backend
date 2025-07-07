from rest_framework import serializers
from .models import Cliente, Equipo_Audio, Catering, Peticion, Repertorio, Fotos_Evento, Contrato


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class EquipoAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo_Audio
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class CateringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catering
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class PeticionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peticion
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class RepertorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repertorio
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class FotosEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fotos_Evento
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class ContratoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    equipo_audio_nombre = serializers.CharField(source='equipo_audio.__str__', read_only=True)
    catering_descripcion = serializers.CharField(source='catering.peticion_grupo', read_only=True)
    peticiones_cliente_nombres = serializers.StringRelatedField(source='peticiones_cliente', many=True, read_only=True)
    
    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'deleted_at', 
            'numero_contrato', 'tiempo_total', 'pago_total', 
            'pago_restante', 'porcentaje', 'cliente_nombre',
            'equipo_audio_nombre', 'catering_descripcion',
            'peticiones_cliente_nombres'
        )
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar horas
        if data.get('hora_final') and data.get('hora_inicio'):
            if data['hora_final'] == data['hora_inicio']:
                raise serializers.ValidationError({
                    "hora_final": "La hora de finalización debe ser diferente a la hora de inicio"
                })
        
        # Validar valores monetarios
        if data.get('pago_adelanto', 0) < 0:
            raise serializers.ValidationError({
                "pago_adelanto": "El adelanto no puede ser negativo"
            })
        
        if data.get('costo_hora', 0) < 0:
            raise serializers.ValidationError({
                "costo_hora": "El costo por hora no puede ser negativo"
            })
        
        # Validar conflictos de horarios
        if data.get('fecha_evento') and data.get('hora_inicio') and data.get('hora_final'):
            self._validar_conflictos_horarios(data)
        
        return data
    
    def _validar_conflictos_horarios(self, data):
        """Valida conflictos de horarios para el serializer"""
        from datetime import datetime, timedelta
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        fecha_evento = data['fecha_evento']
        hora_inicio = data['hora_inicio']
        hora_final = data['hora_final']
        
        # Buscar otros contratos en la misma fecha
        contratos_mismo_dia = Contrato.objects.filter(
            fecha_evento=fecha_evento,
            estado_evento__in=['confirmed', 'pending', 'in_progress']
        )
        
        # Excluir el contrato actual si estamos editando
        if self.instance:
            contratos_mismo_dia = contratos_mismo_dia.exclude(id=self.instance.id)
        
        inicio_actual = datetime.combine(fecha_evento, hora_inicio)
        final_actual = datetime.combine(fecha_evento, hora_final)
        
        # Si la hora final es menor que la inicial, el evento termina al día siguiente
        if hora_final < hora_inicio:
            final_actual += timedelta(days=1)
        
        for contrato in contratos_mismo_dia:
            inicio_existente = datetime.combine(contrato.fecha_evento, contrato.hora_inicio)
            final_existente = datetime.combine(contrato.fecha_evento, contrato.hora_final)
            
            # Si la hora final es menor que la inicial, el evento termina al día siguiente
            if contrato.hora_final < contrato.hora_inicio:
                final_existente += timedelta(days=1)
            
            # Verificar si hay solapamiento o falta de separación mínima
            # Los eventos se solapan si: inicio_actual < final_existente AND final_actual > inicio_existente
            hay_solapamiento = inicio_actual < final_existente and final_actual > inicio_existente
            
            if hay_solapamiento:
                raise serializers.ValidationError({
                    "fecha_evento": f"Conflicto de horarios: Ya existe un evento el {fecha_evento} "
                                  f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                                  f"Los eventos no pueden solaparse."
                })
            
            # Verificar separación mínima de 1 hora entre eventos
            # Si el nuevo evento es después del existente
            if inicio_actual >= final_existente:
                diferencia = (inicio_actual - final_existente).total_seconds() / 3600
                if diferencia < 1:
                    raise serializers.ValidationError({
                        "fecha_evento": f"Conflicto de horarios: Ya existe un evento el {fecha_evento} "
                                      f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                                      f"Debe haber al menos 1 hora de diferencia entre eventos."
                    })
            
            # Si el nuevo evento es antes del existente
            elif final_actual <= inicio_existente:
                diferencia = (inicio_existente - final_actual).total_seconds() / 3600
                if diferencia < 1:
                    raise serializers.ValidationError({
                        "fecha_evento": f"Conflicto de horarios: Ya existe un evento el {fecha_evento} "
                                      f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                                      f"Debe haber al menos 1 hora de diferencia entre eventos."
                    })
        
        return data


class ContratoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear contratos con validaciones adicionales"""
    
    class Meta:
        model = Contrato
        exclude = (
            'numero_contrato', 'tiempo_total', 'pago_total', 
            'pago_restante', 'porcentaje', 'created_at', 
            'updated_at', 'deleted_at'
        )
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar horas
        if data.get('hora_final') and data.get('hora_inicio'):
            if data['hora_final'] == data['hora_inicio']:
                raise serializers.ValidationError({
                    "hora_final": "La hora de finalización debe ser diferente a la hora de inicio"
                })
        
        # Validar valores monetarios
        if data.get('pago_adelanto', 0) < 0:
            raise serializers.ValidationError({
                "pago_adelanto": "El adelanto no puede ser negativo"
            })
        
        if data.get('costo_hora', 0) < 0:
            raise serializers.ValidationError({
                "costo_hora": "El costo por hora no puede ser negativo"
            })
        
        # Validar conflictos de horarios
        if data.get('fecha_evento') and data.get('hora_inicio') and data.get('hora_final'):
            self._validar_conflictos_horarios(data)
        
        return data
    
    def _validar_conflictos_horarios(self, data):
        """Valida conflictos de horarios para el serializer"""
        from datetime import datetime, timedelta
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        fecha_evento = data['fecha_evento']
        hora_inicio = data['hora_inicio']
        hora_final = data['hora_final']
        
        # Buscar otros contratos en la misma fecha
        contratos_mismo_dia = Contrato.objects.filter(
            fecha_evento=fecha_evento,
            estado_evento__in=['confirmed', 'pending', 'in_progress']
        )
        
        # Excluir el contrato actual si estamos editando
        if self.instance:
            contratos_mismo_dia = contratos_mismo_dia.exclude(id=self.instance.id)
        
        inicio_actual = datetime.combine(fecha_evento, hora_inicio)
        final_actual = datetime.combine(fecha_evento, hora_final)
        
        # Si la hora final es menor que la inicial, el evento termina al día siguiente
        if hora_final < hora_inicio:
            final_actual += timedelta(days=1)
        
        for contrato in contratos_mismo_dia:
            inicio_existente = datetime.combine(contrato.fecha_evento, contrato.hora_inicio)
            final_existente = datetime.combine(contrato.fecha_evento, contrato.hora_final)
            
            # Si la hora final es menor que la inicial, el evento termina al día siguiente
            if contrato.hora_final < contrato.hora_inicio:
                final_existente += timedelta(days=1)
            
            # Verificar si hay solapamiento o falta de separación mínima
            # Los eventos se solapan si: inicio_actual < final_existente AND final_actual > inicio_existente
            hay_solapamiento = inicio_actual < final_existente and final_actual > inicio_existente
            
            if hay_solapamiento:
                raise serializers.ValidationError({
                    "fecha_evento": f"Conflicto de horarios: Ya existe un evento el {fecha_evento} "
                                  f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                                  f"Los eventos no pueden solaparse."
                })
            
            # Verificar separación mínima de 1 hora entre eventos
            # Si el nuevo evento es después del existente
            if inicio_actual >= final_existente:
                diferencia = (inicio_actual - final_existente).total_seconds() / 3600
                if diferencia < 1:
                    raise serializers.ValidationError({
                        "fecha_evento": f"Conflicto de horarios: Ya existe un evento el {fecha_evento} "
                                      f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                                      f"Debe haber al menos 1 hora de diferencia entre eventos."
                    })
            
            # Si el nuevo evento es antes del existente
            elif final_actual <= inicio_existente:
                diferencia = (inicio_existente - final_actual).total_seconds() / 3600
                if diferencia < 1:
                    raise serializers.ValidationError({
                        "fecha_evento": f"Conflicto de horarios: Ya existe un evento el {fecha_evento} "
                                      f"de {contrato.hora_inicio} a {contrato.hora_final}. "
                                      f"Debe haber al menos 1 hora de diferencia entre eventos."
                    })
    
    def create(self, validated_data):
        """Crear contrato con cálculos automáticos"""
        peticiones = validated_data.pop('peticiones_cliente', [])
        contrato = Contrato.objects.create(**validated_data)
        
        if peticiones:
            contrato.peticiones_cliente.set(peticiones)
        
        return contrato


class ContratoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de contratos"""
    cliente_nombre = serializers.CharField(source='cliente.nombre_cliente', read_only=True)
    estado_evento_display = serializers.CharField(source='get_estado_evento_display', read_only=True)
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)
    
    class Meta:
        model = Contrato
        fields = (
            'id', 'numero_contrato', 'titulo', 'tipo_evento', 
            'tipo_evento_display', 'estado_evento', 'estado_evento_display',
            'fecha_evento', 'hora_inicio', 'hora_final', 
            'cliente_nombre', 'pago_total', 'porcentaje'
        )
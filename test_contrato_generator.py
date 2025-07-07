#!/usr/bin/env python
"""
Script de prueba para el generador de contratos
Ejecuta este script desde el directorio del proyecto Django

Uso:
python test_contrato_generator.py
"""

import os
import sys
import django
from datetime import datetime, time, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AgendaMusicos.settings')
django.setup()

from GIGS.models import Contrato, Cliente
from GIGS.utils import ContratoGenerator

def crear_contrato_prueba():
    """Crea un contrato de prueba para demostrar la funcionalidad"""
    
    # Crear o obtener un cliente de prueba
    cliente, created = Cliente.objects.get_or_create(
        nombre_cliente="Juan Pérez García",
        defaults={
            'telefono_cliente': '987654321',
            'email_cliente': 'juan.perez@email.com',
            'direccion_cliente': 'Av. Principal 123, Piura',
            'frecuencia': 'primera_vez'
        }
    )
    
    if created:
        print(f"✅ Cliente creado: {cliente.nombre_cliente}")
    else:
        print(f"✅ Cliente encontrado: {cliente.nombre_cliente}")
    
    # Crear un contrato de prueba
    contrato, created = Contrato.objects.get_or_create(
        titulo="Matrimonio de Juan y María",
        defaults={
            'cliente': cliente,
            'tipo_evento': 'wedding',
            'nombre_festejado': 'Juan y María',
            'fecha_evento': date(2024, 6, 15),
            'hora_inicio': time(19, 0),
            'hora_final': time(23, 0),
            'tiempo_total': 4.0,
            'costo_hora': 150.0,
            'pago_total': 600.0,
            'pago_adelanto': 300.0,
            'costo_extra': 0.0,
            'nombre_lugar': 'Salón de Eventos Los Jardines',
            'direccion_lugar': 'Av. Los Jardines 456, Piura',
            'oportunidades_descanso': 2,
            'tiempo_descanso': 15,
            'notas': 'Evento especial con música variada'
        }
    )
    
    if created:
        print(f"✅ Contrato creado: {contrato.numero_contrato}")
    else:
        print(f"✅ Contrato encontrado: {contrato.numero_contrato}")
    
    return contrato

def probar_generacion_docx(contrato):
    """Prueba la generación de DOCX"""
    try:
        print("\n🔄 Generando contrato en formato DOCX...")
        
        # Usar el generador directamente
        generator = ContratoGenerator(contrato)
        filename = f"contrato_prueba_{contrato.numero_contrato}.docx"
        filepath = os.path.join(os.getcwd(), filename)
        
        generator.save_to_file(filepath)
        
        if os.path.exists(filepath):
            print(f"✅ Contrato DOCX generado exitosamente: {filepath}")
            print(f"📄 Tamaño del archivo: {os.path.getsize(filepath)} bytes")
            return filepath
        else:
            print("❌ Error: El archivo DOCX no se generó")
            return None
            
    except Exception as e:
        print(f"❌ Error al generar DOCX: {str(e)}")
        return None

def probar_generacion_pdf(contrato):
    """Prueba la generación de PDF"""
    try:
        print("\n🔄 Generando contrato en formato PDF...")
        
        # Usar el método del modelo
        response = contrato.generar_contrato_pdf()
        
        # Guardar el PDF en un archivo
        filename = f"contrato_prueba_{contrato.numero_contrato}.pdf"
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        if os.path.exists(filepath):
            print(f"✅ Contrato PDF generado exitosamente: {filepath}")
            print(f"📄 Tamaño del archivo: {os.path.getsize(filepath)} bytes")
            return filepath
        else:
            print("❌ Error: El archivo PDF no se generó")
            return None
            
    except Exception as e:
        print(f"❌ Error al generar PDF: {str(e)}")
        print("💡 Nota: Para generar PDF necesitas Microsoft Word o LibreOffice instalado")
        return None

def mostrar_informacion_contrato(contrato):
    """Muestra información del contrato"""
    print("\n📋 INFORMACIÓN DEL CONTRATO")
    print("=" * 50)
    print(f"Número: {contrato.numero_contrato}")
    print(f"Título: {contrato.titulo}")
    print(f"Cliente: {contrato.cliente.nombre_cliente}")
    print(f"Fecha: {contrato.fecha_evento}")
    print(f"Hora: {contrato.hora_inicio} - {contrato.hora_final}")
    print(f"Lugar: {contrato.nombre_lugar}")
    print(f"Pago total: S/. {contrato.pago_total}")
    print(f"Adelanto: S/. {contrato.pago_adelanto}")
    print(f"Restante: S/. {contrato.pago_restante}")
    print(f"Estado: {contrato.get_estado_evento_display()}")

def main():
    """Función principal"""
    print("🎵 GENERADOR DE CONTRATOS - BAHIA MIX")
    print("=" * 50)
    
    # Crear contrato de prueba
    contrato = crear_contrato_prueba()
    
    # Mostrar información
    mostrar_informacion_contrato(contrato)
    
    # Probar generación DOCX
    docx_path = probar_generacion_docx(contrato)
    
    # Probar generación PDF
    pdf_path = probar_generacion_pdf(contrato)
    
    print("\n🎉 PRUEBAS COMPLETADAS")
    print("=" * 50)
    
    if docx_path:
        print(f"📄 DOCX: {docx_path}")
    
    if pdf_path:
        print(f"📄 PDF: {pdf_path}")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Abrir los archivos generados para verificar el contenido")
    print("2. Probar desde la API: GET /api/contratos/{id}/generar_docx/")
    print("3. Probar desde la API: GET /api/contratos/{id}/generar_pdf/")
    print("4. Personalizar la plantilla en GIGS/utils.py")
    
if __name__ == "__main__":
    main()
# Generador de Contratos - AgendaMusicos

Este sistema permite generar contratos musicales en formato DOCX y PDF de manera automática.

## 🚀 Características

- **Generación DOCX**: Documentos Word editables con formato profesional
- **Generación PDF Rápida**: PDFs generados con ReportLab (0.2-0.5 segundos)
- **Generación PDF Fiel**: PDFs generados desde DOCX con docx2pdf (1-2 minutos, más fiel al formato)
- **Datos dinámicos**: Información del contrato insertada automáticamente
- **Logo personalizado**: Incluye logo de la empresa
- **Formato profesional**: Diseño limpio y profesional

## 📋 Dependencias

Instala las dependencias ejecutando:

```bash
pip install -r requirements_contrato.txt
```

### Dependencias principales:
- `python-docx`: Para generar documentos DOCX
- `reportlab`: Para generación rápida de PDF
- `docx2pdf`: Para conversión DOCX a PDF (requiere Microsoft Word)
- `pywin32`: Para inicialización COM en Windows

## 🔧 Uso

### 1. API REST

#### Generar PDF (Rápido - ReportLab)
```http
GET /api/agenda/contratos/{id}/generar_pdf/
```
**Tiempo**: ~0.2-0.5 segundos
**Ventajas**: Muy rápido, no requiere Microsoft Word
**Desventajas**: Formato básico

#### Generar PDF (Fiel al formato - docx2pdf)
```http
GET /api/agenda/contratos/{id}/generar_pdf_docx2pdf/
```
**Tiempo**: ~1-2 minutos
**Ventajas**: Formato idéntico al DOCX original
**Desventajas**: Lento, requiere Microsoft Word instalado

#### Generar DOCX
```http
GET /api/agenda/contratos/{id}/generar_docx/
```
**Tiempo**: ~0.1-0.3 segundos
**Formato**: Documento Word editable

### 2. Código Python

```python
from GIGS.models import Contrato

# Obtener contrato
contrato = Contrato.objects.get(id=1)

# Generar PDF rápido (ReportLab)
response_pdf_rapido = contrato.generar_contrato_pdf()

# Generar PDF fiel al formato (docx2pdf)
response_pdf_fiel = contrato.generar_contrato_pdf_docx2pdf()

# Generar DOCX
response_docx = contrato.generar_contrato_docx()
```

### 3. Desde el shell de Django

```bash
python manage.py shell
```

```python
from GIGS.models import Contrato
import time

contrato = Contrato.objects.first()
print(f'Contrato: {contrato.numero_contrato}')

# Probar generación rápida
start = time.time()
response = contrato.generar_contrato_pdf()
end = time.time()
print(f'PDF rápido generado en: {end-start:.2f} segundos')
```

## 📁 Archivos del sistema

- `GIGS/models.py`: Métodos del modelo Contrato
- `GIGS/views.py`: Endpoints de la API
- `GIGS/utils.py`: Generador DOCX y conversión docx2pdf
- `GIGS/pdf_generator.py`: Generador PDF con ReportLab
- `media/logo/Logotipo.jpg`: Logo de la empresa

## 🎯 Recomendaciones de uso

### Para desarrollo y pruebas:
- Usa la **generación PDF rápida** (`generar_pdf`)
- Tiempo: ~0.2-0.5 segundos
- Ideal para testing y desarrollo

### Para producción con calidad:
- Usa la **generación DOCX** para documentos editables
- Usa la **generación PDF fiel** (`generar_pdf_docx2pdf`) para PDFs finales
- Tiempo: ~1-2 minutos pero con formato profesional

### Para APIs de alta frecuencia:
- Usa la **generación PDF rápida** (`generar_pdf`)
- Considera implementar cache para contratos frecuentemente solicitados

## 🔧 Configuración

### Logo personalizado
Coloca tu logo en: `media/logo/Logotipo.jpg`
- Tamaño recomendado: 200x200 píxeles
- Formato: JPG, PNG

### Personalización del formato
Edita los archivos:
- `GIGS/pdf_generator.py`: Para el formato PDF rápido
- `GIGS/utils.py`: Para el formato DOCX/PDF fiel

## 🐛 Solución de problemas

### Error: "No se ha llamado a CoInitialize"
- **Solución**: Ya está solucionado con la inicialización COM automática
- El sistema inicializa `pythoncom.CoInitialize()` automáticamente

### Error: "No module named 'docx'"
- **Solución**: `pip install python-docx`

### Error: "No module named 'reportlab'"
- **Solución**: `pip install reportlab`

### PDF toma mucho tiempo
- **Solución**: Usa `generar_pdf` en lugar de `generar_pdf_docx2pdf`
- La versión rápida es 300x más rápida

## 📊 Comparación de métodos

| Método | Tiempo | Calidad | Requisitos | Uso recomendado |
|--------|--------|---------|------------|------------------|
| PDF Rápido (ReportLab) | 0.2-0.5s | Básica | Solo Python | Desarrollo, APIs |
| PDF Fiel (docx2pdf) | 1-2min | Alta | MS Word | Producción final |
| DOCX | 0.1-0.3s | Alta | Solo Python | Documentos editables |

## 🔄 Actualizaciones

**v2.0** (Actual):
- ✅ Generación PDF rápida con ReportLab
- ✅ Solución al error de CoInitialize
- ✅ Dos opciones de generación PDF
- ✅ Documentación completa
- ✅ Optimización de rendimiento (300x más rápido)

**v1.0**:
- ✅ Generación DOCX
- ✅ Conversión DOCX a PDF
- ✅ Integración con Django REST
# Pruebas Unitarias - AgendaMusicos

Este directorio contiene todas las pruebas unitarias, de integración y de rendimiento para el proyecto AgendaMusicos.

## 📁 Estructura de Pruebas

```
tests/
├── __init__.py                 # Inicialización del paquete de pruebas
├── test_base.py               # Clase base con datos de prueba comunes
├── test_models.py             # Pruebas de modelos Django
├── test_views.py              # Pruebas de vistas y API endpoints
├── test_serializers.py        # Pruebas de serializadores DRF
├── test_integration.py        # Pruebas de integración completas
├── test_performance.py        # Pruebas de rendimiento y optimización
├── test_runner.py             # Script personalizado para ejecutar pruebas
├── reports/                   # Directorio para reportes de pruebas
└── README.md                  # Este archivo
```

## 🚀 Ejecución de Pruebas

### Método 1: Django Test Runner (Recomendado)

```bash
# Ejecutar todas las pruebas
python manage.py test tests

# Ejecutar pruebas específicas
python manage.py test tests.test_models
python manage.py test tests.test_views.ClienteViewSetTest
python manage.py test tests.test_models.ContratoModelTest.test_calcular_tiempo_total

# Ejecutar con verbosidad
python manage.py test tests --verbosity=2

# Mantener base de datos de pruebas
python manage.py test tests --keepdb

# Ejecutar en paralelo
python manage.py test tests --parallel
```

### Método 2: Script Personalizado

```bash
# Ejecutar todas las pruebas con reporte detallado
python tests/test_runner.py

# Ejecutar prueba específica
python tests/test_runner.py tests.test_models "Pruebas de Modelos"

# Incluir análisis de cobertura
python tests/test_runner.py --coverage
```

### Método 3: Pytest (Opcional)

```bash
# Instalar pytest-django
pip install pytest pytest-django pytest-cov

# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=GIGS --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_models.py
pytest tests/test_views.py::ClienteViewSetTest
pytest -k "test_crear_contrato"

# Ejecutar por marcadores
pytest -m "unit"
pytest -m "integration"
pytest -m "performance"
```

### Método 4: Tox (Múltiples Entornos)

```bash
# Instalar tox
pip install tox

# Ejecutar en todos los entornos
tox

# Ejecutar en entorno específico
tox -e py39
tox -e coverage
tox -e flake8

# Ejecutar pruebas específicas
tox -e unit
tox -e integration
tox -e performance
```

## 📊 Tipos de Pruebas

### 1. Pruebas de Modelos (`test_models.py`)

- **Creación y validación de modelos**
- **Métodos personalizados**
- **Restricciones de base de datos**
- **Cálculos automáticos**
- **Soft delete y restauración**

```python
# Ejemplo de ejecución
python manage.py test tests.test_models.ClienteModelTest
python manage.py test tests.test_models.ContratoModelTest.test_validar_conflictos_horarios
```

### 2. Pruebas de Vistas/API (`test_views.py`)

- **Endpoints CRUD**
- **Autenticación y permisos**
- **Filtros y búsquedas**
- **Acciones personalizadas**
- **Códigos de estado HTTP**

```python
# Ejemplo de ejecución
python manage.py test tests.test_views.ContratoViewSetTest
python manage.py test tests.test_views.ClienteViewSetTest.test_soft_delete
```

### 3. Pruebas de Serializadores (`test_serializers.py`)

- **Serialización y deserialización**
- **Validaciones personalizadas**
- **Campos calculados**
- **Relaciones entre modelos**

```python
# Ejemplo de ejecución
python manage.py test tests.test_serializers.ContratoSerializerTest
```

### 4. Pruebas de Integración (`test_integration.py`)

- **Flujos completos de usuario**
- **Interacciones entre componentes**
- **Escenarios de negocio complejos**
- **Manejo de errores end-to-end**

```python
# Ejemplo de ejecución
python manage.py test tests.test_integration.ContratoIntegrationTest
python manage.py test tests.test_integration.DatabaseIntegrityTest
```

### 5. Pruebas de Rendimiento (`test_performance.py`)

- **Optimización de consultas**
- **Tiempo de respuesta de API**
- **Uso de memoria**
- **Operaciones en lote**
- **Caché**

```python
# Ejemplo de ejecución
python manage.py test tests.test_performance.QueryPerformanceTest
python manage.py test tests.test_performance.APIPerformanceTest
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Para pruebas
export DJANGO_SETTINGS_MODULE=AgendaMusicos.settings
export TESTING=True

# Para base de datos de pruebas en memoria
export DATABASE_URL=sqlite:///:memory:
```

### Configuración de Base de Datos

Las pruebas utilizan una base de datos SQLite en memoria por defecto para mayor velocidad:

```python
# En settings.py para pruebas
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
```

## 📈 Cobertura de Código

### Generar Reporte de Cobertura

```bash
# Con coverage.py
coverage run --source='.' manage.py test tests
coverage report
coverage html

# Con pytest
pytest --cov=GIGS --cov-report=html --cov-report=term

# Con el script personalizado
python tests/test_runner.py --coverage
```

### Objetivos de Cobertura

- **Modelos**: > 95%
- **Vistas**: > 90%
- **Serializadores**: > 90%
- **Utilidades**: > 85%
- **Total del proyecto**: > 80%

## 🐛 Debugging de Pruebas

### Ejecutar con Debug

```bash
# Con pdb
python manage.py test tests.test_models.ContratoModelTest.test_calcular_tiempo_total --pdb

# Con verbosidad máxima
python manage.py test tests --verbosity=3

# Mantener base de datos para inspección
python manage.py test tests --keepdb --debug-mode
```

### Logs de Pruebas

```python
# En test_base.py o pruebas específicas
import logging
logging.basicConfig(level=logging.DEBUG)

# Para ver consultas SQL
from django.conf import settings
settings.LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📋 Datos de Prueba

### Fixtures Automáticas

La clase `BaseTestCase` en `test_base.py` proporciona:

- **Cliente de prueba** con datos válidos
- **Equipo de audio** configurado
- **Servicio de catering** básico
- **Peticiones musicales** de ejemplo
- **Repertorio** predefinido
- **Métodos helper** para crear datos

### Crear Datos Personalizados

```python
from tests.test_base import BaseTestCase

class MiPruebaTest(BaseTestCase):
    def test_mi_funcionalidad(self):
        # Usar datos base
        cliente = self.cliente
        
        # Crear datos personalizados
        cliente_custom = self.crear_cliente(
            nombre_cliente='Cliente Personalizado',
            telefono_cliente='555000111'
        )
        
        contrato = self.crear_contrato(
            titulo='Mi Evento',
            cliente=cliente_custom
        )
```

## 🚨 Mejores Prácticas

### 1. Nomenclatura

```python
# ✅ Bueno
def test_crear_contrato_con_datos_validos(self):
    pass

def test_validar_conflicto_horarios_mismo_dia(self):
    pass

# ❌ Malo
def test1(self):
    pass

def test_contrato(self):
    pass
```

### 2. Estructura de Pruebas

```python
def test_funcionalidad_especifica(self):
    # Arrange (Preparar)
    cliente = self.crear_cliente()
    
    # Act (Actuar)
    response = self.client.post('/api/clientes/', data)
    
    # Assert (Verificar)
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.data['nombre'], 'Test')
```

### 3. Aislamiento

- Cada prueba debe ser independiente
- No depender del orden de ejecución
- Limpiar datos después de cada prueba
- Usar `setUp()` y `tearDown()` apropiadamente

### 4. Mocking

```python
from unittest.mock import patch, Mock

@patch('GIGS.utils.enviar_email')
def test_confirmacion_contrato(self, mock_email):
    # Configurar mock
    mock_email.return_value = True
    
    # Ejecutar prueba
    contrato = self.crear_contrato()
    contrato.confirmar()
    
    # Verificar que se llamó
    mock_email.assert_called_once()
```

## 📊 Reportes y Métricas

### Reportes Automáticos

El script `test_runner.py` genera reportes en formato JSON:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "test_suites": {
    "tests.test_models": {
      "description": "Pruebas de Modelos",
      "tests_run": 25,
      "failures": 0,
      "errors": 0,
      "execution_time": 2.34,
      "success": true
    }
  },
  "summary": {
    "total_tests": 150,
    "passed": 148,
    "failed": 2,
    "errors": 0,
    "total_time": 45.67
  }
}
```

### Métricas de Rendimiento

- **Tiempo de ejecución por prueba**
- **Número de consultas SQL**
- **Uso de memoria**
- **Tiempo de respuesta de API**

## 🔄 Integración Continua

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage pytest pytest-django
    - name: Run tests
      run: |
        python tests/test_runner.py --coverage
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 🆘 Solución de Problemas

### Problemas Comunes

1. **Error de importación de módulos**
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **Base de datos bloqueada**
   ```bash
   python manage.py test tests --keepdb=False
   ```

3. **Pruebas lentas**
   ```bash
   python manage.py test tests --parallel --keepdb
   ```

4. **Memoria insuficiente**
   ```bash
   # Ejecutar pruebas por módulos
   python manage.py test tests.test_models
   python manage.py test tests.test_views
   ```

### Logs de Debug

```python
# Agregar en pruebas específicas
import logging
logger = logging.getLogger(__name__)
logger.debug("Información de debug")
```

## 📚 Recursos Adicionales

- [Documentación de Django Testing](https://docs.djangoproject.com/en/4.0/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Última actualización**: Enero 2024
**Mantenido por**: Equipo de Desarrollo AgendaMusicos
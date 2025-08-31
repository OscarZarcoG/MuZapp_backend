# Agenda Músicos - Backend

El backend de Agenda Músicos es un sistema robusto desarrollado con Django y Django REST Framework, diseñado para gestionar toda la información relacionada con eventos musicales, clientes, contratos y usuarios. Incluye una funcionalidad avanzada de conversión de música de YouTube a MP3.

## 🚀 Características Principales

- **Gestión de Gigs (Eventos)**: Creación, consulta, actualización y eliminación de eventos musicales.
- **Administración de Clientes**: Manejo de la información de los clientes.
- **Generación de Contratos**: Sistema avanzado para generar contratos en formatos DOCX y PDF con diferentes niveles de calidad y velocidad.
- **Autenticación de Usuarios**: Sistema completo de registro, inicio y cierre de sesión basado en tokens.
- **Conversión de Música**: Sistema de conversión de videos de YouTube a archivos MP3 de alta calidad.
- **API RESTful**: Una API bien estructurada para interactuar with el frontend y otros servicios.

## 🛠️ Tecnologías Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/Django%20REST-A30000?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## 📂 Estructura del Proyecto

El proyecto sigue una estructura modular basada en aplicaciones de Django, diseñada para una clara separación de responsabilidades:

```
AgendaMusicos/
├── AgendaMusicos/         # Configuración principal del proyecto Django.
├── GIGS/                  # App para la gestión de eventos, clientes y contratos.
├── AUTH/                  # App para la autenticación y gestión de usuarios.
├── MUSIC/                 # App para conversión de música de YouTube a MP3.
├── MEXICO/                # App para datos geográficos de México.
├── core/                  # Componentes transversales (excepciones, respuestas).
├── media/                 # Archivos multimedia (audio convertido, imágenes).
├── manage.py              # Script de gestión de Django.
└── requirements.txt       # Dependencias del proyecto.
```

- **`GIGS`**: Contiene toda la lógica de negocio relacionada con los eventos, contratos y clientes.
- **`AUTH`**: Gestiona la autenticación, registro y perfiles de usuario.
- **`core`**: Componentes transversales como manejadores de excepciones y respuestas personalizadas.

## 📋 Requisitos del Sistema

### Dependencias del Sistema

- **Python 3.8+**: Lenguaje de programación principal
- **PostgreSQL**: Base de datos (opcional, se puede usar SQLite para desarrollo)
- **FFmpeg**: Requerido para conversión de audio de YouTube

### Instalación de FFmpeg

#### Windows
```bash
# Usando winget (recomendado)
winget install ffmpeg

# O descargar desde https://ffmpeg.org/download.html
```

#### macOS
```bash
# Usando Homebrew
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Verificar instalación
```bash
ffmpeg -version
ffprobe -version
```

## ⚙️ Configuración del Entorno

1.  **Clonar el repositorio**:

    ```bash
    git clone https://github.com/OscarZarcoG/AgendaMusicos.git
    cd AgendaMusicos
    ```

2.  **Crear y activar un entorno virtual**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```

3.  **Instalar dependencias de Python**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la base de datos**:

    Asegúrate de que tu base de datos PostgreSQL esté en funcionamiento y actualiza la configuración en `AgendaMusicos/settings.py`:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'bd_agendamusico',
            'USER': 'postgres',
            'PASSWORD': 'tu_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

5.  **Aplicar migraciones**:

    ```bash
    python manage.py migrate
    ```

6.  **Iniciar el servidor de desarrollo**:

    ```bash
    python manage.py runserver
    ```

    El servidor estará disponible en `http://127.0.0.1:8000`.

## 📡 Endpoints de la API

La API está disponible bajo el prefijo `/api/`.

### Autenticación (`/api/user/`)

-   `POST /api/user/signup/`: Registro de un nuevo usuario.
-   `POST /api/user/login/`: Inicio de sesión. Devuelve un token de autenticación.
-   `POST /api/user/logout/`: Cierre de sesión. Requiere token de autenticación.

### Conversión de Música (`/api/music/api/conversions/`)

-   `POST /api/music/api/conversions/convert/`: Convierte un video de YouTube a MP3.
    ```json
    {
        "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "quality": "high"  // "high", "medium", "low"
    }
    ```
-   `GET /api/music/api/conversions/`: Lista todas las conversiones del usuario.
-   `GET /api/music/api/conversions/{id}/`: Obtiene detalles de una conversión específica.
-   `GET /api/music/api/conversions/{id}/download/`: Descarga el archivo MP3 convertido.
-   `DELETE /api/music/api/conversions/{id}/`: Elimina una conversión.

### Interfaz Web de Música

-   `GET /api/music/`: Página principal de conversión de música.
-   `GET /api/music/conversions/`: Lista de conversiones realizadas.

### Gigs y Contratos (`/api/`)

-   Endpoints para gestionar eventos, clientes, equipos, etc. (Consultar `GIGS/urls.py` para más detalles).
-   `GET /api/contratos/{id}/generar_pdf/`: Genera un PDF del contrato de forma rápida.
-   `GET /api/contratos/{id}/generar_pdf_docx2pdf/`: Genera un PDF de alta fidelidad a partir de un DOCX.
-   `GET /api/contratos/{id}/generar_docx/`: Genera un archivo DOCX del contrato.

## ✍️ Autor

Este proyecto fue desarrollado por **Oscar Zarco**.

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/OscarZarcoG)

## 🚀 Despliegue en Servidor

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Configuración de Django
SECRET_KEY=tu_clave_secreta_muy_segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,localhost

# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd

# Configuración de archivos estáticos y media
STATIC_ROOT=/ruta/a/archivos/estaticos
MEDIA_ROOT=/ruta/a/archivos/media

# Configuración de CORS (si es necesario)
CORS_ALLOWED_ORIGINS=https://tu-frontend.com,https://www.tu-frontend.com
```

### Configuración del Servidor Web

#### Usando Gunicorn + Nginx

1. **Instalar Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Crear archivo de servicio systemd** (`/etc/systemd/system/agendamusicos.service`):
   ```ini
   [Unit]
   Description=Agenda Musicos Django App
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/ruta/a/tu/proyecto
   Environment="PATH=/ruta/a/tu/venv/bin"
   ExecStart=/ruta/a/tu/venv/bin/gunicorn --workers 3 --bind unix:/ruta/a/tu/proyecto/agendamusicos.sock AgendaMusicos.wsgi:application
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Configurar Nginx** (`/etc/nginx/sites-available/agendamusicos`):
   ```nginx
   server {
       listen 80;
       server_name tu-dominio.com www.tu-dominio.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /ruta/a/tu/proyecto;
       }
       
       location /media/ {
           root /ruta/a/tu/proyecto;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/ruta/a/tu/proyecto/agendamusicos.sock;
       }
   }
   ```

### Comandos de Despliegue

```bash
# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Reiniciar servicios
sudo systemctl restart agendamusicos
sudo systemctl restart nginx
```

### Consideraciones de Seguridad

- Asegúrate de que FFmpeg esté instalado en el servidor
- Configura límites de tamaño de archivo para uploads
- Implementa rate limiting para las conversiones
- Usa HTTPS en producción
- Configura backups regulares de la base de datos

## ✅ Pruebas

El proyecto incluye un completo sistema de pruebas. Para ejecutar todas las pruebas, utiliza el siguiente comando:

```bash
python tests/test_runner.py
```

Esto ejecutará pruebas de modelos, vistas, serializadores, integración y rendimiento, generando un informe detallado en la consola.

## 🔧 Solución de Problemas

### Error: "ffprobe and ffmpeg not found"

**Solución**: Instala FFmpeg siguiendo las instrucciones en la sección "Instalación de FFmpeg".

### Error de conversión de YouTube

**Posibles causas**:
- URL de YouTube inválida
- Video privado o restringido geográficamente
- Problemas de conectividad
- FFmpeg no instalado correctamente

### Problemas de permisos en archivos media

**Solución**:
```bash
# En Linux/macOS
sudo chown -R www-data:www-data /ruta/a/media/
sudo chmod -R 755 /ruta/a/media/
```
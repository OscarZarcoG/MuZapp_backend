# Agenda Músicos - Backend

El backend de Agenda Músicos es un sistema robusto desarrollado con Django y Django REST Framework, diseñado para gestionar toda la información relacionada con eventos musicales, clientes, contratos y usuarios.

## 🚀 Características Principales

- **Gestión de Gigs (Eventos)**: Creación, consulta, actualización y eliminación de eventos musicales.
- **Administración de Clientes**: Manejo de la información de los clientes.
- **Generación de Contratos**: Sistema avanzado para generar contratos en formatos DOCX y PDF con diferentes niveles de calidad y velocidad.
- **Autenticación de Usuarios**: Sistema completo de registro, inicio y cierre de sesión basado en tokens.
- **API RESTful**: Una API bien estructurada para interactuar con el frontend y otros servicios.

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
├── userAPI/               # App para la autenticación y gestión de usuarios.
├── core/                  # Componentes transversales (excepciones, respuestas).
├── tests/                 # Pruebas unitarias, de integración y rendimiento.
├── manage.py              # Script de gestión de Django.
└── requirements.txt       # Dependencias del proyecto.
```

- **`GIGS`**: Contiene toda la lógica de negocio relacionada con los eventos, contratos y clientes.
- **`userAPI`**: Gestiona la autenticación, registro y perfiles de usuario.
- **`core`**: Componentes transversales como manejadores de excepciones y respuestas personalizadas.

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

3.  **Instalar dependencias**:

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

## Endpoints de la API

La API está disponible bajo el prefijo `/api/`.

### Autenticación (`/api/user/`)

-   `POST /api/user/signup/`: Registro de un nuevo usuario.
-   `POST /api/user/login/`: Inicio de sesión. Devuelve un token de autenticación.
-   `POST /api/user/logout/`: Cierre de sesión. Requiere token de autenticación.

## 👤 Autor

-   **Oscar Zarco G**
-   **GitHub:** [OscarZarcoG](https://github.com/OscarZarcoG)

### Gigs y Contratos (`/api/`)

-   Endpoints para gestionar eventos, clientes, equipos, etc. (Consultar `GIGS/urls.py` para más detalles).
-   `GET /api/contratos/{id}/generar_pdf/`: Genera un PDF del contrato de forma rápida.
-   `GET /api/contratos/{id}/generar_pdf_docx2pdf/`: Genera un PDF de alta fidelidad a partir de un DOCX.
-   `GET /api/contratos/{id}/generar_docx/`: Genera un archivo DOCX del contrato.

## ✍️ Autor

Este proyecto fue desarrollado por **Oscar Zarco**.

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/OscarZarcoG)

## ✅ Pruebas

El proyecto incluye un completo sistema de pruebas. Para ejecutar todas las pruebas, utiliza el siguiente comando:

```bash
python tests/test_runner.py
```

Esto ejecutará pruebas de modelos, vistas, serializadores, integración y rendimiento, generando un informe detallado en la consola.
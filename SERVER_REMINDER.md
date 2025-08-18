# RECORDATORIO IMPORTANTE DEL SERVIDOR

## ⚠️ COMANDO OBLIGATORIO PARA INICIAR EL SERVIDOR

**SIEMPRE usar este comando exacto:**

```bash
python manage.py runserver localhost:8000
```

### ❌ NO usar:
- `python manage.py runserver` (sin especificar host)
- `python manage.py runserver 127.0.0.1:8000`
- `python manage.py runserver 0.0.0.0:8000`

### ✅ SIEMPRE usar:
- `python manage.py runserver localhost:8000`

## Razón
Este proyecto está configurado específicamente para funcionar en `localhost:8000` y es importante mantener esta consistencia para evitar problemas de conectividad y configuración.

## URLs del proyecto:
- **Servidor de desarrollo:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **API Auth:** http://localhost:8000/api/user/auth/

---
**NOTA:** Este archivo sirve como recordatorio permanente. NO ELIMINAR.
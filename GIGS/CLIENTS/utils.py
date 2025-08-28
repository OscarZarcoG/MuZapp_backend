from .views import ClientViewSet
from .models import Client

import requests
from django.conf import settings


def autocompletar_inputs_de_direccion_por_codigo_postal(codigo_postal):
    """
    Autocompleta los campos de dirección (colonia, municipio, estado, país) usando el endpoint de MEXICO.
    """
    try:
        # Construir la URL del endpoint
        base_url = getattr(settings, 'MEXICO_API_URL', 'http://localhost:8000/api/mexico/')
        url = f"{base_url}codigo-postal/{codigo_postal}/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Si hay información completa (solo una colonia)
            if 'informacion_completa' in data:
                info = data['informacion_completa']
                return {
                    'colonia': info.get('colonia', ''),
                    'municipio': info.get('municipio', ''),
                    'estado': info.get('estado', ''),
                    'pais': info.get('pais', ''),
                    'ciudad': info.get('ciudad', ''),
                    'asentamiento': info.get('asentamiento', '')
                }
            # Si hay varias colonias, devolver la lista
            elif 'colonias' in data:
                return {
                    'colonias': data['colonias'],
                    'municipio': data['colonias'][0].get('municipio', '') if data['colonias'] else '',
                    'estado': data['colonias'][0].get('estado', '') if data['colonias'] else '',
                    'pais': data['colonias'][0].get('pais', '') if data['colonias'] else ''
                }
        return None
    except Exception:
        return None

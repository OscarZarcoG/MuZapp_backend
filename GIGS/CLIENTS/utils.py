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
            # Si hay colonias en la respuesta
            if 'colonias' in data and data['colonias']:
                colonias = data['colonias']
                if len(colonias) == 1:
                    # Solo una colonia, devolver información completa
                    colonia = colonias[0]
                    return {
                        'colonia': colonia.get('nombre', ''),
                        'municipio': colonia.get('municipio_nombre', ''),
                        'estado': colonia.get('estado_nombre', ''),
                        'pais': colonia.get('pais_nombre', '') or 'México',
                        'ciudad': colonia.get('ciudad', ''),
                        'asentamiento': colonia.get('asentamiento', '')
                    }
                else:
                    # Múltiples colonias, devolver la lista
                    return {
                        'colonias': colonias,
                        'municipio': colonias[0].get('municipio_nombre', '') if colonias else '',
                        'estado': colonias[0].get('estado_nombre', '') if colonias else '',
                        'pais': colonias[0].get('pais_nombre', '') or 'México' if colonias else 'México'
                    }
        return None
    except Exception:
        return None

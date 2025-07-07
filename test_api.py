import requests
import json
from datetime import datetime, time

# URL base de la API
BASE_URL = 'http://localhost:8000/api/agenda'

def test_api_endpoints():
    print("=== PROBANDO API REST ===\n")
    
    # 1. Probar GET de contratos
    print("1. Probando GET /contratos/")
    try:
        response = requests.get(f'{BASE_URL}/contratos/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Contratos encontrados: {len(data)}")
            if data:
                print(f"   Primer contrato ID: {data[0].get('id', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error de conexión: {e}")
    
    print()
    
    # 2. Probar GET de clientes
    print("2. Probando GET /clientes/")
    try:
        response = requests.get(f'{BASE_URL}/clientes/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Clientes encontrados: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error de conexión: {e}")
    
    print()
    
    # 3. Probar validaciones de conflictos horarios
    print("3. Probando validaciones de conflictos horarios")
    
    # Datos de prueba para crear un contrato
    test_contract = {
        "fecha_evento": "2025-08-21",
        "hora_inicio": "20:00:00",
        "hora_final": "24:00:00",
        "costo_hora": 1000,
        "pago_adelanto": 500,
        "cliente": 1,  # Asumiendo que existe un cliente con ID 1
        "lugar": "Lugar de prueba",
        "descripcion": "Evento de prueba para validaciones"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/contratos/', 
                               json=test_contract,
                               headers={'Content-Type': 'application/json'})
        print(f"   Status POST: {response.status_code}")
        if response.status_code == 201:
            print("   ✓ Contrato creado exitosamente")
            contract_id = response.json().get('id')
            
            # Intentar crear un contrato conflictivo
            conflict_contract = test_contract.copy()
            conflict_contract["hora_inicio"] = "19:00:00"
            conflict_contract["hora_final"] = "21:00:00"
            
            response2 = requests.post(f'{BASE_URL}/contratos/', 
                                    json=conflict_contract,
                                    headers={'Content-Type': 'application/json'})
            print(f"   Status POST conflictivo: {response2.status_code}")
            if response2.status_code == 400:
                print("   ✓ Validación de conflictos funcionando correctamente")
                print(f"   Error esperado: {response2.json()}")
            else:
                print("   ✗ La validación de conflictos no está funcionando")
                
            # Limpiar - eliminar el contrato de prueba
            if contract_id:
                requests.delete(f'{BASE_URL}/contratos/{contract_id}/')
                print("   Contrato de prueba eliminado")
                
        else:
            print(f"   Error al crear contrato: {response.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # 4. Probar otros endpoints
    endpoints = ['equipos-audio', 'catering', 'peticiones', 'repertorio', 'fotos-evento']
    
    for endpoint in endpoints:
        print(f"4.{endpoints.index(endpoint)+1} Probando GET /{endpoint}/")
        try:
            response = requests.get(f'{BASE_URL}/{endpoint}/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Registros encontrados: {len(data)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

if __name__ == "__main__":
    test_api_endpoints()
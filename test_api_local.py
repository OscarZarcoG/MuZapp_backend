import requests
import json
from datetime import datetime, time

# URL base de la API usando localhost
BASE_URL = 'http://localhost:8000/api/agenda'

def test_basic_endpoints():
    print("=== PROBANDO API REST (LOCALHOST) ===\n")
    
    # Lista de endpoints básicos para probar
    endpoints = [
        'contratos',
        'clientes', 
        'equipos-audio',
        'catering',
        'peticiones',
        'repertorio',
        'fotos-evento'
    ]
    
    for endpoint in endpoints:
        print(f"Probando GET /{endpoint}/")
        try:
            response = requests.get(f'{BASE_URL}/{endpoint}/', timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✓ Registros encontrados: {len(data)}")
                    if data and endpoint == 'contratos':
                        # Mostrar información del primer contrato si existe
                        primer_contrato = data[0]
                        print(f"   Primer contrato ID: {primer_contrato.get('id', 'N/A')}")
                        print(f"   Fecha: {primer_contrato.get('fecha_evento', 'N/A')}")
                        print(f"   Estado: {primer_contrato.get('estado_evento', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"   ✓ Respuesta recibida pero no es JSON válido")
            elif response.status_code == 404:
                print(f"   ⚠ Endpoint no encontrado")
            else:
                print(f"   ✗ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Detalle: {error_data}")
                except:
                    print(f"   Detalle: {response.text[:200]}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ✗ Error de conexión - Servidor no disponible")
            break
        except requests.exceptions.Timeout:
            print(f"   ✗ Timeout - Servidor no responde")
        except Exception as e:
            print(f"   ✗ Error inesperado: {e}")
        
        print()

def test_contract_validation():
    print("=== PROBANDO VALIDACIONES DE CONTRATOS ===\n")
    
    # Primero verificar si hay clientes disponibles
    try:
        response = requests.get(f'{BASE_URL}/clientes/', timeout=5)
        if response.status_code != 200:
            print("No se pueden obtener clientes para las pruebas")
            return
            
        clientes = response.json()
        if not clientes:
            print("No hay clientes disponibles para crear contratos de prueba")
            return
            
        cliente_id = clientes[0]['id']
        print(f"Usando cliente ID: {cliente_id}")
        
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        return
    
    # Datos de prueba para crear un contrato
    test_contract = {
        "fecha_evento": "2025-08-21",
        "hora_inicio": "20:00:00",
        "hora_final": "24:00:00",
        "costo_hora": 1000,
        "pago_adelanto": 500,
        "cliente": cliente_id,
        "lugar": "Lugar de prueba",
        "descripcion": "Evento de prueba para validaciones"
    }
    
    print("1. Creando contrato de prueba...")
    try:
        response = requests.post(f'{BASE_URL}/contratos/', 
                               json=test_contract,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            contract_data = response.json()
            contract_id = contract_data.get('id')
            print(f"   ✓ Contrato creado exitosamente (ID: {contract_id})")
            print(f"   Estado: {contract_data.get('estado_evento', 'N/A')}")
            print(f"   Tiempo total: {contract_data.get('tiempo_total', 'N/A')}")
            
            # Probar validación de conflictos
            print("\n2. Probando validación de conflictos horarios...")
            conflict_contract = test_contract.copy()
            conflict_contract["hora_inicio"] = "19:00:00"
            conflict_contract["hora_final"] = "21:00:00"
            
            response2 = requests.post(f'{BASE_URL}/contratos/', 
                                    json=conflict_contract,
                                    headers={'Content-Type': 'application/json'},
                                    timeout=10)
            print(f"   Status: {response2.status_code}")
            
            if response2.status_code == 400:
                error_data = response2.json()
                print("   ✓ Validación de conflictos funcionando correctamente")
                print(f"   Error esperado: {error_data}")
            else:
                print("   ✗ La validación de conflictos no está funcionando como esperado")
                if response2.status_code == 201:
                    # Si se creó, eliminarlo también
                    conflict_id = response2.json().get('id')
                    if conflict_id:
                        requests.delete(f'{BASE_URL}/contratos/{conflict_id}/', timeout=5)
            
            # Limpiar - eliminar el contrato de prueba
            print("\n3. Limpiando contrato de prueba...")
            if contract_id:
                delete_response = requests.delete(f'{BASE_URL}/contratos/{contract_id}/', timeout=5)
                if delete_response.status_code == 204:
                    print("   ✓ Contrato de prueba eliminado")
                else:
                    print(f"   ⚠ No se pudo eliminar el contrato (Status: {delete_response.status_code})")
                    
        else:
            print(f"   ✗ Error al crear contrato: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data}")
            except:
                print(f"   Detalle: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ✗ Error: {e}")

if __name__ == "__main__":
    test_basic_endpoints()
    print("\n" + "="*50 + "\n")
    test_contract_validation()
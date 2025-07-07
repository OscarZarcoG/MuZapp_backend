#!/usr/bin/env python
"""
Script para ejecutar todas las pruebas del proyecto AgendaMusicos
con diferentes configuraciones y generar reportes detallados.
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AgendaMusicos.settings')

import django
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import execute_from_command_line


class TestRunner:
    """Ejecutor de pruebas con diferentes configuraciones"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'skipped': 0,
                'total_time': 0
            }
        }
    
    def run_test_suite(self, test_path, description, verbosity=2):
        """Ejecuta una suite de pruebas específica"""
        
        print(f"\n{'='*60}")
        print(f"Ejecutando: {description}")
        print(f"Ruta: {test_path}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Ejecutar las pruebas usando Django test runner
            from django.test.runner import DiscoverRunner
            
            runner = DiscoverRunner(
                verbosity=verbosity,
                interactive=False,
                keepdb=False,
                reverse=False,
                debug_mode=False,
                debug_sql=False,
                parallel=0,
                tags=None,
                exclude_tags=None
            )
            
            # Configurar la base de datos de pruebas
            old_config = runner.setup_databases()
            
            # Ejecutar las pruebas
            suite = runner.build_suite([test_path])
            result = runner.run_suite(suite)
            
            # Limpiar
            runner.teardown_databases(old_config)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Guardar resultados
            suite_result = {
                'description': description,
                'test_path': test_path,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'execution_time': execution_time,
                'success': result.wasSuccessful()
            }
            
            self.results['test_suites'][test_path] = suite_result
            
            # Actualizar resumen
            self.results['summary']['total_tests'] += result.testsRun
            self.results['summary']['failed'] += len(result.failures)
            self.results['summary']['errors'] += len(result.errors)
            self.results['summary']['skipped'] += len(result.skipped) if hasattr(result, 'skipped') else 0
            self.results['summary']['total_time'] += execution_time
            
            if result.wasSuccessful():
                self.results['summary']['passed'] += result.testsRun
                print(f"✅ {description} - EXITOSO")
            else:
                print(f"❌ {description} - FALLÓ")
                
                # Mostrar detalles de fallos
                if result.failures:
                    print("\nFALLOS:")
                    for test, traceback in result.failures:
                        print(f"- {test}: {traceback}")
                
                if result.errors:
                    print("\nERRORES:")
                    for test, traceback in result.errors:
                        print(f"- {test}: {traceback}")
            
            print(f"Tiempo de ejecución: {execution_time:.2f} segundos")
            
            return result.wasSuccessful()
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"❌ Error ejecutando {description}: {str(e)}")
            
            suite_result = {
                'description': description,
                'test_path': test_path,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'execution_time': execution_time,
                'success': False,
                'error_message': str(e)
            }
            
            self.results['test_suites'][test_path] = suite_result
            self.results['summary']['errors'] += 1
            self.results['summary']['total_time'] += execution_time
            
            return False
    
    def run_all_tests(self):
        """Ejecuta todas las suites de pruebas"""
        
        print("🚀 Iniciando ejecución completa de pruebas para AgendaMusicos")
        print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Definir las suites de pruebas
        test_suites = [
            ('tests.test_models', 'Pruebas de Modelos'),
            ('tests.test_views', 'Pruebas de Vistas/API'),
            ('tests.test_serializers', 'Pruebas de Serializadores'),
            ('tests.test_integration', 'Pruebas de Integración'),
            ('tests.test_performance', 'Pruebas de Rendimiento')
        ]
        
        all_passed = True
        
        for test_path, description in test_suites:
            success = self.run_test_suite(test_path, description)
            if not success:
                all_passed = False
        
        # Calcular estadísticas finales
        total_tests = self.results['summary']['total_tests']
        if total_tests > 0:
            self.results['summary']['passed'] = (
                total_tests - 
                self.results['summary']['failed'] - 
                self.results['summary']['errors']
            )
        
        # Mostrar resumen final
        self.print_final_summary()
        
        # Guardar reporte
        self.save_report()
        
        return all_passed
    
    def print_final_summary(self):
        """Imprime el resumen final de todas las pruebas"""
        
        print("\n" + "="*80)
        print("📊 RESUMEN FINAL DE PRUEBAS")
        print("="*80)
        
        summary = self.results['summary']
        
        print(f"Total de pruebas ejecutadas: {summary['total_tests']}")
        print(f"✅ Exitosas: {summary['passed']}")
        print(f"❌ Fallidas: {summary['failed']}")
        print(f"🚫 Errores: {summary['errors']}")
        print(f"⏭️  Omitidas: {summary['skipped']}")
        print(f"⏱️  Tiempo total: {summary['total_time']:.2f} segundos")
        
        if summary['total_tests'] > 0:
            success_rate = (summary['passed'] / summary['total_tests']) * 100
            print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        print("\n📋 DETALLE POR SUITE:")
        print("-" * 80)
        
        for test_path, result in self.results['test_suites'].items():
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['description']}:")
            print(f"   Pruebas: {result['tests_run']}, "
                  f"Fallos: {result['failures']}, "
                  f"Errores: {result['errors']}, "
                  f"Tiempo: {result['execution_time']:.2f}s")
        
        print("\n" + "="*80)
        
        if summary['failed'] == 0 and summary['errors'] == 0:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        else:
            print("⚠️  ALGUNAS PRUEBAS FALLARON - Revisar detalles arriba")
        
        print("="*80)
    
    def save_report(self):
        """Guarda el reporte de pruebas en formato JSON"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'test_report_{timestamp}.json'
        report_path = os.path.join(project_dir, 'tests', 'reports', report_filename)
        
        # Crear directorio de reportes si no existe
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Reporte guardado en: {report_path}")
            
        except Exception as e:
            print(f"\n⚠️  Error guardando reporte: {str(e)}")
    
    def run_specific_test(self, test_path, description=None):
        """Ejecuta una prueba específica"""
        
        if description is None:
            description = f"Prueba específica: {test_path}"
        
        return self.run_test_suite(test_path, description)
    
    def run_coverage_analysis(self):
        """Ejecuta análisis de cobertura de código"""
        
        print("\n🔍 Ejecutando análisis de cobertura...")
        
        try:
            # Instalar coverage si no está disponible
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                         check=False, capture_output=True)
            
            # Ejecutar pruebas con coverage
            cmd = [
                sys.executable, '-m', 'coverage', 'run',
                '--source', '.',
                'manage.py', 'test', 'tests'
            ]
            
            result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Generar reporte de cobertura
                coverage_cmd = [sys.executable, '-m', 'coverage', 'report']
                coverage_result = subprocess.run(coverage_cmd, cwd=project_dir, 
                                               capture_output=True, text=True)
                
                print("📊 Reporte de Cobertura:")
                print(coverage_result.stdout)
                
                # Generar reporte HTML
                html_cmd = [sys.executable, '-m', 'coverage', 'html']
                subprocess.run(html_cmd, cwd=project_dir, capture_output=True)
                
                print("\n🌐 Reporte HTML generado en: htmlcov/index.html")
                
            else:
                print(f"❌ Error en análisis de cobertura: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️  Error ejecutando análisis de cobertura: {str(e)}")


def main():
    """Función principal"""
    
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        # Ejecutar prueba específica
        test_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else None
        
        success = runner.run_specific_test(test_path, description)
        
        if '--coverage' in sys.argv:
            runner.run_coverage_analysis()
        
        sys.exit(0 if success else 1)
    
    else:
        # Ejecutar todas las pruebas
        success = runner.run_all_tests()
        
        if '--coverage' in sys.argv:
            runner.run_coverage_analysis()
        
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
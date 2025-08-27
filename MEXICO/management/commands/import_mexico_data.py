import re
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from MEXICO.models import Pais, Estado, Municipio, Colonia


class Command(BaseCommand):
    help = 'Importa los datos de México desde el archivo SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sql-file',
            type=str,
            default='mexico-ciudades/mexico.sql',
            help='Ruta al archivo SQL (relativa al directorio del proyecto)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Tamaño del lote para inserción masiva'
        )

    def handle(self, *args, **options):
        sql_file = options['sql_file']
        batch_size = options['batch_size']
        
        # Construir la ruta completa al archivo SQL
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        sql_path = os.path.join(base_dir, sql_file)
        
        if not os.path.exists(sql_path):
            raise CommandError(f'El archivo SQL no existe: {sql_path}')
        
        self.stdout.write(f'Importando datos desde: {sql_path}')
        
        try:
            with transaction.atomic():
                self._import_data(sql_path, batch_size)
        except Exception as e:
            raise CommandError(f'Error durante la importación: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS('Datos importados exitosamente')
        )

    def _import_data(self, sql_path, batch_size):
        """Importa los datos desde el archivo SQL"""
        
        with open(sql_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Limpiar tablas existentes
        self.stdout.write('Limpiando tablas existentes...')
        Colonia.objects.all().delete()
        Municipio.objects.all().delete()
        Estado.objects.all().delete()
        Pais.objects.all().delete()
        
        # Importar países
        self._import_paises(content)
        
        # Importar estados
        self._import_estados(content)
        
        # Importar municipios
        self._import_municipios(content, batch_size)
        
        # Importar colonias
        self._import_colonias(content, batch_size)

    def _import_paises(self, content):
        """Importa los países"""
        self.stdout.write('Importando países...')
        
        # Buscar la sección de INSERT de países
        paises_pattern = r"INSERT INTO `paises` \(`id`, `nombre`\) VALUES\s+([^;]+);"
        match = re.search(paises_pattern, content, re.DOTALL)
        
        if match:
            values_str = match.group(1)
            # Extraer valores individuales
            values_pattern = r"\((\d+),'([^']+)'\)"
            matches = re.findall(values_pattern, values_str)
            
            paises = []
            for pais_id, nombre in matches:
                paises.append(Pais(id=int(pais_id), nombre=nombre))
            
            Pais.objects.bulk_create(paises)
            self.stdout.write(f'  - {len(paises)} países importados')

    def _import_estados(self, content):
        """Importa los estados"""
        self.stdout.write('Importando estados...')
        
        # Buscar la sección de INSERT de estados
        estados_pattern = r"INSERT INTO `estados` \(`id`, `nombre`, `pais`\) VALUES\s+([^;]+);"
        match = re.search(estados_pattern, content, re.DOTALL)
        
        if match:
            values_str = match.group(1)
            # Extraer valores individuales
            values_pattern = r"\((\d+),'([^']+)',(\d+)\)"
            matches = re.findall(values_pattern, values_str)
            
            # Obtener países para las relaciones
            paises_dict = {p.id: p for p in Pais.objects.all()}
            
            estados = []
            for estado_id, nombre, pais_id in matches:
                estados.append(Estado(
                    id=int(estado_id),
                    nombre=nombre,
                    pais=paises_dict[int(pais_id)]
                ))
            
            Estado.objects.bulk_create(estados)
            self.stdout.write(f'  - {len(estados)} estados importados')

    def _import_municipios(self, content, batch_size):
        """Importa los municipios"""
        self.stdout.write('Importando municipios...')
        
        # Buscar la sección de INSERT de municipios
        municipios_pattern = r"INSERT INTO `municipios` \(`id`, `nombre`, `estado`\) VALUES\s+([^;]+);"
        match = re.search(municipios_pattern, content, re.DOTALL)
        
        if match:
            values_str = match.group(1)
            # Extraer valores individuales
            values_pattern = r"\((\d+),'([^']+)',(\d+)\)"
            matches = re.findall(values_pattern, values_str)
            
            # Obtener estados para las relaciones
            estados_dict = {e.id: e for e in Estado.objects.all()}
            
            municipios = []
            count = 0
            
            for municipio_id, nombre, estado_id in matches:
                municipios.append(Municipio(
                    id=int(municipio_id),
                    nombre=nombre,
                    estado=estados_dict[int(estado_id)]
                ))
                
                count += 1
                if count % batch_size == 0:
                    Municipio.objects.bulk_create(municipios)
                    self.stdout.write(f'  - {count} municipios procesados...')
                    municipios = []
            
            # Insertar los municipios restantes
            if municipios:
                Municipio.objects.bulk_create(municipios)
            
            self.stdout.write(f'  - {count} municipios importados en total')

    def _import_colonias(self, content, batch_size):
        """Importa las colonias"""
        self.stdout.write('Importando colonias...')
        
        # Buscar la sección de INSERT de colonias
        colonias_pattern = r"INSERT INTO `colonias` \([^)]+\) VALUES\s+([^;]+);"
        matches = re.findall(colonias_pattern, content, re.DOTALL)
        
        if not matches:
            self.stdout.write('  - No se encontraron datos de colonias')
            return
        
        # Obtener municipios para las relaciones
        municipios_dict = {m.id: m for m in Municipio.objects.all()}
        
        colonias = []
        count = 0
        
        for match in matches:
            values_str = match
            # Patrón más flexible para colonias
            values_pattern = r"\((\d+),'([^']*)',(?:'([^']*)'|NULL),(\d+|NULL),(?:'([^']*)'|NULL),(\d+|NULL)\)"
            colonia_matches = re.findall(values_pattern, values_str)
            
            for colonia_data in colonia_matches:
                colonia_id, nombre, ciudad, municipio_id, asentamiento, codigo_postal = colonia_data
                
                # Procesar valores NULL
                ciudad = ciudad if ciudad else None
                municipio_id = int(municipio_id) if municipio_id and municipio_id != 'NULL' else None
                asentamiento = asentamiento if asentamiento else None
                codigo_postal = int(codigo_postal) if codigo_postal and codigo_postal != 'NULL' else None
                
                municipio = municipios_dict.get(municipio_id) if municipio_id else None
                
                colonias.append(Colonia(
                    id=int(colonia_id),
                    nombre=nombre,
                    ciudad=ciudad,
                    municipio=municipio,
                    asentamiento=asentamiento,
                    codigo_postal=codigo_postal
                ))
                
                count += 1
                if count % batch_size == 0:
                    Colonia.objects.bulk_create(colonias, ignore_conflicts=True)
                    self.stdout.write(f'  - {count} colonias procesadas...')
                    colonias = []
        
        # Insertar las colonias restantes
        if colonias:
            Colonia.objects.bulk_create(colonias, ignore_conflicts=True)
        
        self.stdout.write(f'  - {count} colonias importadas en total')
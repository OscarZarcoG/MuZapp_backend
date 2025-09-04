from django.core.management.base import BaseCommand
from GIGS.REPERTORIE.models import Generos


class Command(BaseCommand):
    help = 'Poblar la tabla de géneros con los géneros predefinidos'

    def handle(self, *args, **options):
        generos_data = [
            ('pop', 'Pop'),
            ('rock', 'Rock'),
            ('jazz', 'Jazz'),
            ('blues', 'Blues'),
            ('country', 'Country'),
            ('folk', 'Folk'),
            ('reggae', 'Reggae'),
            ('hip_hop', 'Hip Hop'),
            ('electronic', 'Electrónica'),
            ('classical', 'Clásica'),
            ('latin', 'Latina'),
            ('salsa', 'Salsa'),
            ('merengue', 'Merengue'),
            ('bachata', 'Bachata'),
            ('cumbia', 'Cumbia'),
            ('vallenato', 'Vallenato'),
            ('ranchera', 'Ranchera'),
            ('mariachi', 'Mariachi'),
            ('bolero', 'Bolero'),
            ('tango', 'Tango'),
            ('bossa_nova', 'Bossa Nova'),
            ('reggaeton', 'Reggaetón'),
            ('trap', 'Trap'),
            ('funk', 'Funk'),
            ('soul', 'Soul'),
            ('r_and_b', 'R&B'),
            ('gospel', 'Gospel'),
            ('indie', 'Indie'),
            ('alternative', 'Alternativo'),
            ('punk', 'Punk'),
            ('metal', 'Metal'),
            ('disco', 'Disco'),
            ('house', 'House'),
            ('techno', 'Techno'),
            ('ambient', 'Ambient'),
            ('instrumental', 'Instrumental'),
            ('otros', 'Otros'),
        ]

        created_count = 0
        for codigo, nombre in generos_data:
            genero, created = Generos.objects.get_or_create(
                nombre=nombre,
                defaults={'nombre': nombre}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Género creado: {nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Género ya existe: {nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. {created_count} géneros creados.'
            )
        )
# userAPI/management/commands/repair_profiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from userAPI.models import UserProfile


class Command(BaseCommand):
    help = 'Repairs missing user profiles'

    def handle(self, *args, **options):
        created_count = 0
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1

        if created_count:
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} missing profiles')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All profiles exist already')
            )
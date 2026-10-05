from django.core.management.base import BaseCommand

from gameapp.models import User, Word

WORDS = [
    'APPLE', 'BRAIN', 'CHAIR', 'DREAM', 'EARTH',
    'FLAME', 'GRAPE', 'HOUSE', 'IVORY', 'JUICE',
    'KNIFE', 'LEMON', 'MANGO', 'NIGHT', 'OCEAN',
    'PIANO', 'QUILT', 'RIVER', 'SMILE', 'TIGER',
]


class Command(BaseCommand):
    help = 'Seed the original WORD//TRACE demo data.'

    def handle(self, *args, **options):
        for value in WORDS:
            Word.objects.get_or_create(value=value)

        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        admin.role = User.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('Admin1*')
        admin.save()

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(WORDS)} words and admin/Admin1* demo access.'))

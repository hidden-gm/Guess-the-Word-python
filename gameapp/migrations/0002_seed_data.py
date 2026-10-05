from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone

WORDS = [
    'APPLE', 'BRAIN', 'CHAIR', 'DREAM', 'EARTH',
    'FLAME', 'GRAPE', 'HOUSE', 'IVORY', 'JUICE',
    'KNIFE', 'LEMON', 'MANGO', 'NIGHT', 'OCEAN',
    'PIANO', 'QUILT', 'RIVER', 'SMILE', 'TIGER',
]


def seed(apps, schema_editor):
    User = apps.get_model('gameapp', 'User')
    Word = apps.get_model('gameapp', 'Word')

    for value in WORDS:
        Word.objects.get_or_create(value=value)

    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            password=make_password('Admin1*'),
            role='ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            date_joined=timezone.now(),
        )


def unseed(apps, schema_editor):
    User = apps.get_model('gameapp', 'User')
    Word = apps.get_model('gameapp', 'Word')
    User.objects.filter(username='admin').delete()
    Word.objects.filter(value__in=WORDS).delete()


class Migration(migrations.Migration):
    dependencies = [('gameapp', '0001_initial')]
    operations = [migrations.RunPython(seed, unseed)]

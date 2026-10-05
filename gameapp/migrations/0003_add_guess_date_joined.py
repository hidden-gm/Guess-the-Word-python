from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gameapp', '0002_seed_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='guess',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

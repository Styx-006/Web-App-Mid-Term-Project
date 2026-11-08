from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_preserve_existing_progress'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerprogress',
            name='discovered_businesses',
            field=models.ManyToManyField(blank=True, related_name='discoverers', to='game.business'),
        ),
    ]

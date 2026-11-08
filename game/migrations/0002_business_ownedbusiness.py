import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('base_price', models.DecimalField(decimal_places=2, default=10, max_digits=24)),
                ('income_per_second', models.DecimalField(decimal_places=2, default=1, max_digits=24)),
            ],
        ),
        migrations.CreateModel(
            name='OwnedBusiness',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owners', to='game.business')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_businesses', to='game.playerprogress')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('player', 'business'), name='unique_player_business')],
            },
        ),
    ]

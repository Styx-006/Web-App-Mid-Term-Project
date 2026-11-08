import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_playerprogress_last_work_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerprogress',
            name='last_daily_claim_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AchievementClaim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=60)),
                ('claimed_at', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievement_claims', to='game.playerprogress')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('player', 'code'), name='unique_player_achievement')],
            },
        ),
    ]

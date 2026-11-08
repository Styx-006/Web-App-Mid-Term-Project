import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_playerprogress_last_daily_claim_at_achievementclaim'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownedbusiness',
            name='upgrade_level',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='achievement_points',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='most_business_types',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='run_earnings',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=24),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='total_businesses_purchased',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='total_daily_claims',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='total_points_earned',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='total_upgrades_purchased',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playerprogress',
            name='total_work_actions',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='GlobalUpgrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=60)),
                ('level', models.PositiveIntegerField(default=1)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='global_upgrades', to='game.playerprogress')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('player', 'code'), name='unique_player_global_upgrade')],
            },
        ),
    ]

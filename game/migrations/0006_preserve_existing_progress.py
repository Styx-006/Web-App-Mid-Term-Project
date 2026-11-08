from django.db import migrations


def preserve_progress(apps, schema_editor):
    Player = apps.get_model('game', 'PlayerProgress')
    Claim = apps.get_model('game', 'AchievementClaim')
    Owned = apps.get_model('game', 'OwnedBusiness')
    rewards = {'first-business': 5, 'ten-businesses': 10, 'fifty-businesses': 20,
               'first-thousand': 10, 'first-million': 40}
    for player in Player.objects.all():
        items = Owned.objects.filter(player_id=player.id)
        points = sum(rewards.get(code, 0) for code in Claim.objects.filter(player_id=player.id).values_list('code', flat=True))
        player.achievement_points = points
        player.total_points_earned = points
        player.total_businesses_purchased = sum(items.values_list('quantity', flat=True))
        player.most_business_types = items.count()
        player.run_earnings = player.lifetime_earnings
        player.total_daily_claims = 1 if player.last_daily_claim_at else 0
        player.save()


class Migration(migrations.Migration):
    dependencies = [('game', '0005_ownedbusiness_upgrade_level_and_more')]
    operations = [migrations.RunPython(preserve_progress, migrations.RunPython.noop)]

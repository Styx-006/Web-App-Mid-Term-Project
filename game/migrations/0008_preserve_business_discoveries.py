from django.db import migrations


def backfill(apps, schema_editor):
    Player = apps.get_model('game', 'PlayerProgress')
    Owned = apps.get_model('game', 'OwnedBusiness')
    for player in Player.objects.all():
        player.discovered_businesses.add(*Owned.objects.filter(player_id=player.id).values_list('business_id', flat=True))


class Migration(migrations.Migration):
    dependencies = [('game', '0007_playerprogress_discovered_businesses')]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]

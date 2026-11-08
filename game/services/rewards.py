from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from ..models import Business

DAILY_REWARD = Decimal('100.00')

ACHIEVEMENTS = [
    ('first-business', 'Open for business', 'Businesses purchased', 'purchases', 1, 5),
    ('ten-businesses', 'Growing empire', 'Businesses purchased', 'purchases', 10, 10),
    ('fifty-businesses', 'Business magnate', 'Businesses purchased', 'purchases', 50, 20),
    ('first-thousand', 'First thousand', 'Lifetime cash earned', 'earnings', 1000, 10),
    ('first-million', 'Millionaire', 'Lifetime cash earned', 'earnings', 1000000, 40),
]
for target, points in [(100,5),(10000,15),(100000,25),(10000000,60),(100000000,80),
                       (1000000000,110),(10000000000,150),(100000000000,200),(1000000000000,300),(10000000000000,450)]:
    ACHIEVEMENTS.append((f'earn-{target}', f'Fortune: ${target:,}', 'Lifetime cash earned', 'earnings', target, points))
for metric, label, tiers in [
    ('purchases', 'Businesses purchased', [(25,15),(100,30),(250,50),(500,80),(1000,120),(2500,200)]),
    ('types', 'Different businesses owned at once', [(2,5),(3,10),(4,15),(6,25),(8,40),(10,60),(12,100)]),
    ('work', 'Work actions completed', [(10,5),(50,10),(100,15),(500,30),(1000,50),(5000,100)]),
    ('upgrades', 'Business upgrades purchased', [(1,5),(5,10),(10,20),(25,40),(50,70),(100,120)]),
    ('daily', 'Daily rewards collected', [(1,5),(3,10),(7,20),(14,35),(30,60)]),
    ('prestige', 'Prestiges completed', [(1,30),(2,50),(3,80),(5,150),(10,300)]),
]:
    for target, points in tiers:
        ACHIEVEMENTS.append((f'{metric}-{target}', f'{label}: {target:,}', label, metric, target, points))


def achievement_status(player):
    ownership = list(player.owned_businesses.select_related('business'))

    metrics = {'purchases': max(player.total_businesses_purchased, sum(item.quantity for item in ownership)),
               'earnings': player.lifetime_earnings, 'types': max(player.most_business_types, len(ownership)),
               'work': player.total_work_actions, 'upgrades': player.total_upgrades_purchased,
               'daily': player.total_daily_claims, 'prestige': player.prestige_count}
    claimed = set(player.achievement_claims.values_list('code', flat=True))
    results = []
    for code, name, description, metric, target, points in ACHIEVEMENTS:
        value = metrics[metric]
        results.append(dict(code=code, name=name, category=metric, description=description,
                            progress=str(min(value, target)), target=str(target), points=points,
                            eligible=value >= target or code in claimed, claimed=code in claimed))
    owned_ids = {item.business_id for item in ownership} | set(player.discovered_businesses.values_list('id', flat=True))
    for index, business in enumerate(sorted(Business.objects.all(), key=lambda item: (item.base_price, item.id))):
        code = f'business-{business.id}'
        done = business.id in owned_ids or code in claimed
        results.append(dict(code=code, name=f'Open {business.name}', category='discovery',
                            description=f'Own a {business.name}.', progress='1' if done else '0', target='1',
                            points=5 * (index + 1) ** 2, eligible=done, claimed=code in claimed))
    return results


def daily_status(player):
    now = timezone.now()
    next_claim = player.last_daily_claim_at + timedelta(hours=24) if player.last_daily_claim_at else None
    return {'amount': format(DAILY_REWARD, '.2f'), 'available': next_claim is None or now >= next_claim,
            'next_claim_at': next_claim.isoformat() if next_claim else None}

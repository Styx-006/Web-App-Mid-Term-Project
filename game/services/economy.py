from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from .progression import multipliers



MAX_CASH = Decimal('9999999999999999999999.99')


def unit_income(business, level, multiplier):
    return min(MAX_CASH, (business.income_per_second * (2 ** level) * multiplier).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP))


def income_rate(player):
    multiplier = multipliers(player)
    total = Decimal('0.00')
    for owned in player.owned_businesses.select_related('business'):
        total += unit_income(owned.business, owned.upgrade_level, multiplier) * owned.quantity
    return min(MAX_CASH, total)


def credit_cash(player, amount):
    player.money = min(MAX_CASH, player.money + amount)
    player.lifetime_earnings = min(MAX_CASH, player.lifetime_earnings + amount)
    player.run_earnings = min(MAX_CASH, player.run_earnings + amount)


def settle_income(player, now):

    seconds = max(0, int((now - player.last_income_at).total_seconds()))
    earned = min(MAX_CASH - player.money, income_rate(player) * seconds)
    credit_cash(player, earned)
    player.last_income_at += timedelta(seconds=seconds)
    return earned


def purchase_price(business, quantity_owned):
    return (business.base_price * Decimal('1.15') ** quantity_owned).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP,
    )


def bulk_quote(business, owned, money, mode):

    quantity = 0
    total = Decimal('0.00')
    limit = None
    if mode == '1':
        limit = 1
    elif mode == '10':
        limit = 10
    while limit is None or quantity < limit:
        price = purchase_price(business, owned + quantity)
        if price <= 0:
            break
        if limit is None and total + price > money:
            break
        total += price
        quantity += 1
    return {'quantity': quantity, 'cost': format(total, '.2f')}


def snapshot(player):
    from ..models import Business
    from .rewards import achievement_status, daily_status
    from .progression import global_status, prestige_status, unlock_requirement, upgrade_cost, MAX_UPGRADE_LEVEL
    owned = {item.business_id: item for item in player.owned_businesses.select_related('business')}
    discovered = set(player.discovered_businesses.values_list('id', flat=True))
    multiplier = multipliers(player)
    businesses = []
    for business in sorted(Business.objects.all(), key=lambda item: (item.base_price, item.id)):
        item = owned.get(business.id)
        quantity = item.quantity if item else 0
        level = item.upgrade_level if item else 0
        unlocked = player.lifetime_earnings >= unlock_requirement(business) or item is not None or business.id in discovered
        businesses.append({
            'id': business.id,
            'name': business.name,
            'description': business.description,
            'quantity': quantity,
            'unlocked': unlocked,
            'unlock_at': format(unlock_requirement(business), '.2f'),
            'upgrade_level': level,
            'upgrade_cost': format(upgrade_cost(item), '.2f') if item and level < MAX_UPGRADE_LEVEL else None,
            'max_upgrade_level': MAX_UPGRADE_LEVEL,
            'quotes': {mode: bulk_quote(business, quantity, player.money, mode) for mode in ('1', '10', 'max')},
            'next_price': format(purchase_price(business, quantity), '.2f'),
            'income_per_second': format(unit_income(business, level, multiplier), '.2f'),
        })
    achievements = achievement_status(player)
    globals_ = global_status(player)
    return {
        'username': player.user.username,
        'money': format(player.money, '.2f'),
        'lifetime_earnings': format(player.lifetime_earnings, '.2f'),
        'last_income_at': player.last_income_at.isoformat(),
        'prestige_count': player.prestige_count,
        'achievement_points': player.achievement_points,
        'income_per_second': format(income_rate(player), '.2f'),
        'income_multiplier': format(multiplier, '.2f'),
        'achievements': achievements,
        'daily_reward': daily_status(player),
        'businesses': businesses,
        'global_upgrades': globals_,
        'prestige': prestige_status(player),
        'statistics': {
            'lifetime_earnings': format(player.lifetime_earnings, '.2f'),
            'run_earnings': format(player.run_earnings, '.2f'),
            'total_businesses_purchased': player.total_businesses_purchased,
            'businesses_owned': sum(item.quantity for item in owned.values()),
            'total_upgrades_purchased': player.total_upgrades_purchased,
            'total_work_actions': player.total_work_actions,
            'total_daily_claims': player.total_daily_claims,
            'achievements_claimed': sum(item['claimed'] for item in achievements),
            'achievements_total': len(achievements),
            'total_points_earned': player.total_points_earned,
            'points_spent': player.total_points_earned - player.achievement_points,
            'global_upgrade_levels': sum(item['level'] for item in globals_),
            'prestige_count': player.prestige_count,
        },
    }

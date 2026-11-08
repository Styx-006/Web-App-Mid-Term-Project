from decimal import Decimal

MAX_UPGRADE_LEVEL = 10
GLOBAL_UPGRADES = [
    ('training', 'Company Training', 10, 10),
    ('marketing', 'Brand Marketing', 20, 20),
    ('automation', 'Smart Automation', 35, 30),
    ('logistics', 'Worldwide Logistics', 60, 50),
    ('research', 'Advanced Research', 100, 75),
    ('galactic', 'Galactic Network', 175, 100),
]


def global_status(player):
    levels = dict(player.global_upgrades.values_list('code', 'level'))
    upgrades = []
    for code, name, base_cost, bonus in GLOBAL_UPGRADES:
        level = levels.get(code, 0)
        upgrades.append({
            'code': code,
            'name': name,
            'level': level,
            'max_level': 3,
            'bonus_percent': bonus,
            'next_cost': base_cost * (2 ** level),
        })
    return upgrades


def multipliers(player):
    bonus = sum(item['level'] * item['bonus_percent'] for item in global_status(player))
    return (Decimal('1') + Decimal(bonus) / 100) * (Decimal('1') + Decimal(player.prestige_count) / 4)


def unlock_requirement(business):
    return Decimal('0') if business.base_price <= 10 else business.base_price / 10


def is_unlocked(player, business):
    if player.lifetime_earnings >= unlock_requirement(business):
        return True
    if player.discovered_businesses.filter(pk=business.pk).exists():
        return True
    return player.owned_businesses.filter(business=business).exists()


def upgrade_cost(owned):
    return owned.business.base_price * 10 * (3 ** owned.upgrade_level)


def prestige_status(player):
    threshold = Decimal(1000000) * (10 ** min(player.prestige_count, 15))
    return {
        'available': player.run_earnings >= threshold,
        'requirement': format(threshold, '.2f'),
        'run_earnings': format(player.run_earnings, '.2f'),
        'current_multiplier': format(Decimal('1') + Decimal(player.prestige_count) / 4, '.2f'),
        'next_multiplier': format(Decimal('1') + Decimal(player.prestige_count + 1) / 4, '.2f'),
    }

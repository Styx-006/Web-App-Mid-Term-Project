from django.core.management.base import BaseCommand
from game.models import Business

BUSINESSES = [
    ('Lemonade Stand', 10, 1),
    ('Hot Dog Cart', 100, 5),
    ('Coffee Shop', 1000, 25),
    ('Pizza Restaurant', 10000, 125),
    ('Grocery Store', 100000, 625),
    ('Car Dealership', 1000000, 3125),
    ('Hotel', 10000000, 15625),
    ('Shopping Mall', 100000000, 78125),
    ('Tech Company', 1000000000, 390625),
    ('Space Tourism Company', 10000000000, 1953125),
    ('Lunar Mining Colony', 100000000000, 9765625),
    ('Galactic Trading Empire', 1000000000000, 48828125),
]


class Command(BaseCommand):
    help = 'Add the 12 starting business types without changing existing ones.'

    def handle(self, *args, **options):
        for name, price, income in BUSINESSES:
            Business.objects.get_or_create(name=name, defaults={
                'base_price': price, 'income_per_second': income,
            })
        self.stdout.write(self.style.SUCCESS('Business catalog is ready.'))

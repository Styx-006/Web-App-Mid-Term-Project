import game.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_preserve_business_discoveries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='base_price',
            field=game.fields.MoneyField(decimal_places=2, default=10, max_digits=24),
        ),
        migrations.AlterField(
            model_name='business',
            name='income_per_second',
            field=game.fields.MoneyField(decimal_places=2, default=1, max_digits=24),
        ),
        migrations.AlterField(
            model_name='playerprogress',
            name='lifetime_earnings',
            field=game.fields.MoneyField(decimal_places=2, default=0, max_digits=24),
        ),
        migrations.AlterField(
            model_name='playerprogress',
            name='money',
            field=game.fields.MoneyField(decimal_places=2, default=0, max_digits=24),
        ),
        migrations.AlterField(
            model_name='playerprogress',
            name='run_earnings',
            field=game.fields.MoneyField(decimal_places=2, default=0, max_digits=24),
        ),
    ]

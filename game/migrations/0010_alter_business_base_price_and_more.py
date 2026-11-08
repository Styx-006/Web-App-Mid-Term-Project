import django.core.validators
import game.fields
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_alter_business_base_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='base_price',
            field=game.fields.MoneyField(decimal_places=2, default=10, max_digits=24, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='business',
            name='income_per_second',
            field=game.fields.MoneyField(decimal_places=2, default=1, max_digits=24, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='globalupgrade',
            name='level',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)]),
        ),
        migrations.AlterField(
            model_name='ownedbusiness',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='ownedbusiness',
            name='upgrade_level',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AddConstraint(
            model_name='business',
            constraint=models.CheckConstraint(condition=models.Q(('base_price__gte', Decimal('0.01'))), name='positive_business_price'),
        ),
        migrations.AddConstraint(
            model_name='business',
            constraint=models.CheckConstraint(condition=models.Q(('income_per_second__gte', Decimal('0.00'))), name='nonnegative_business_income'),
        ),
        migrations.AddConstraint(
            model_name='globalupgrade',
            constraint=models.CheckConstraint(condition=models.Q(('level__gte', 1), ('level__lte', 3)), name='global_upgrade_limit'),
        ),
        migrations.AddConstraint(
            model_name='ownedbusiness',
            constraint=models.CheckConstraint(condition=models.Q(('quantity__gte', 1)), name='positive_owned_quantity'),
        ),
        migrations.AddConstraint(
            model_name='ownedbusiness',
            constraint=models.CheckConstraint(condition=models.Q(('upgrade_level__lte', 10)), name='business_upgrade_limit'),
        ),
    ]

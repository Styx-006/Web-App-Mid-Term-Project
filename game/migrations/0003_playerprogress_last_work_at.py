from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_business_ownedbusiness'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerprogress',
            name='last_work_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

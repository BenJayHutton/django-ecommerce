# Generated by Django 5.0.6 on 2025-04-06 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_total',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='sub_total',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
    ]

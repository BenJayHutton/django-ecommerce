# Generated by Django 5.0.6 on 2024-12-08 21:37

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_alter_product_vat_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='vat_rate',
            field=models.DecimalField(choices=[(Decimal('0.20'), 'Standard Rate 20%'), (Decimal('0.05'), 'Reduced Rate 5%'), (Decimal('0.00'), 'Zero Rate 0%')], decimal_places=2, max_digits=10),
        ),
    ]
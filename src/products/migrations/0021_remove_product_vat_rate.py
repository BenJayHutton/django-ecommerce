# Generated by Django 5.0.6 on 2024-12-20 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_alter_product_price_alter_product_vat_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='vat_rate',
        ),
    ]
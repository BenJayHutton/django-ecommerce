# Generated by Django 5.0.6 on 2024-06-02 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('public', models.BooleanField(default=False)),
                ('blurb', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('price', models.FloatField(default=0.0, max_length=2)),
                ('vat', models.FloatField(default=0.0, max_length=2)),
                ('image', models.ImageField(blank=True, default='products/150x150.png', null=True, upload_to='products/')),
                ('featured', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('is_digital', models.BooleanField(default=False)),
                ('weight_in_grams', models.FloatField(default=0.0, max_length=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('tags', models.ManyToManyField(blank=True, to='tags.tag')),
            ],
        ),
    ]

# Generated by Django 3.1 on 2023-07-08 09:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0003_productgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='offer',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]

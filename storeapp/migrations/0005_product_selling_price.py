# Generated by Django 3.1 on 2023-07-08 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0004_product_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='selling_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

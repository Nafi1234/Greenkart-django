# Generated by Django 3.1 on 2023-07-09 13:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_code', models.CharField(max_length=50, unique=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_spend', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_to', models.DateTimeField()),
            ],
        ),
    ]

# Generated by Django 3.1 on 2023-07-11 20:15

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20230708_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('is_valid', models.BooleanField(default=True)),
                ('generated_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generated_coupons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

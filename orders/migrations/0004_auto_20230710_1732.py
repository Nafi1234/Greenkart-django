# Generated by Django 3.1 on 2023-07-10 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20230630_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pendind', 'Pending'), ('Accepted', 'Accepted'), ('shipped', 'shipped'), (' Completed', ' Completed'), ('Cancelled', 'Cancelled')], default='New', max_length=10),
        ),
    ]

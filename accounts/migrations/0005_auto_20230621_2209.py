# Generated by Django 3.1 on 2023-06-21 16:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_userprofile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='users',
            new_name='user',
        ),
    ]

# Generated by Django 3.2.5 on 2022-07-15 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cat',
            old_name='bread',
            new_name='breed',
        ),
    ]
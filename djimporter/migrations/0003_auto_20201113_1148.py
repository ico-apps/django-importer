# Generated by Django 2.2.13 on 2020-11-13 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djimporter', '0002_importlog_percent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importlog',
            old_name='percent',
            new_name='progress',
        ),
    ]

# Generated by Django 4.0.1 on 2022-02-23 10:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Research', '0002_experiment_dataset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experiment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='database',
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='experiment',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
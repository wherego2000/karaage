# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-31 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kgusage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cpujob',
            name='software',
            field=models.ManyToManyField(blank=True, to='kgsoftware.SoftwareVersion'),
        ),
    ]

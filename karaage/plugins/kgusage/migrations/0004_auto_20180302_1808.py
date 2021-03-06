# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-02 18:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kgusage', '0003_auto_20180131_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cpujob',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='karaage.Account'),
        ),
        migrations.AlterField(
            model_name='cpujob',
            name='machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='karaage.Machine'),
        ),
        migrations.AlterField(
            model_name='cpujob',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='karaage.Project'),
        ),
        migrations.AlterField(
            model_name='cpujob',
            name='queue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kgusage.Queue'),
        ),
    ]

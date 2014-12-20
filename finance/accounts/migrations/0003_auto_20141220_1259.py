# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20141219_1334'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accounttype',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='accounttype',
            name='name',
            field=models.CharField(max_length=20),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='accounttype',
            unique_together=set([('name', 'profile')]),
        ),
    ]

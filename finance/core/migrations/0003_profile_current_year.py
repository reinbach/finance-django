# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20141220_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='current_year',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]

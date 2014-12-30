# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20141226_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='summary',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]

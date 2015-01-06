# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_accounttype_default_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttype',
            name='yearly',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

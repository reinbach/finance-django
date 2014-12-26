# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20141224_1917'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['account_type', 'name']},
        ),
    ]

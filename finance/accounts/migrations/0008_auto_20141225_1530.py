# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20141225_1451'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set([]),
        ),
    ]

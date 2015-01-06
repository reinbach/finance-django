# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20141230_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounttype',
            name='default_type',
            field=models.CharField(
                default=b'DEBIT',
                max_length=20,
                choices=[(b'DEBIT', b'Debit'), (b'CREDIT', b'Credit')]
            ),
            preserve_default=True,
        ),
    ]

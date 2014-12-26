# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20141220_1259'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='account',
            name='is_category',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='parent',
            field=models.ForeignKey(blank=True, to='accounts.Account',
                                    null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='description',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='account_credit',
            field=models.ForeignKey(related_name='credit',
                                    verbose_name=b'credit',
                                    to='accounts.Account'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='account_debit',
            field=models.ForeignKey(related_name='debit',
                                    verbose_name=b'debit',
                                    to='accounts.Account'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.CharField(max_length=250, blank=True),
            preserve_default=True,
        ),
    ]

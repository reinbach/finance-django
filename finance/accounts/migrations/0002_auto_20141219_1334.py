# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['date']},
        ),
        migrations.AddField(
            model_name='account',
            name='profile',
            field=models.ForeignKey(to='core.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accounttype',
            name='profile',
            field=models.ForeignKey(to='core.Profile'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='account',
            name='description',
            field=models.CharField(max_length=250),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='name',
            field=models.CharField(unique=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='accounttype',
            name='name',
            field=models.CharField(unique=True, max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.CharField(max_length=250),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='summary',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]

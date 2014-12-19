# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=b'50')),
                ('description', models.CharField(max_length=b'250')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=b'20')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=8,
                                               decimal_places=2)),
                ('summary', models.CharField(max_length=b'50')),
                ('description', models.CharField(max_length=b'250')),
                ('date', models.DateField()),
                ('account_credit', models.ForeignKey(related_name='credit',
                                                     to='accounts.Account')),
                ('account_debit', models.ForeignKey(related_name='debit',
                                                    to='accounts.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='account',
            name='account_type',
            field=models.ForeignKey(to='accounts.AccountType'),
            preserve_default=True,
        ),
    ]

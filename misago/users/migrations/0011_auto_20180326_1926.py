# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-26 19:26
from __future__ import unicode_literals

from django.db import migrations, models
import misago.core.pgutils


class Migration(migrations.Migration):

    dependencies = [
        ('misago_users', '0010_user_profile_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_deleting_account',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='user',
            index=misago.core.pgutils.PgPartialIndex(fields=['is_deleting_account'], name='misago_user_delete__8d97e7_part', where={'is_deleting_account': True}),
        ),
    ]
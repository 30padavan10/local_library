# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-07-24 12:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20190724_1648'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': (('can_mark_return', 'Set boo as returned'),)},
        ),
    ]
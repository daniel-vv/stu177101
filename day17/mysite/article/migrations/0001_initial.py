# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-01 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_created=True)),
                ('title', models.CharField(max_length=100)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('content', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date_time'],
            },
        ),
    ]

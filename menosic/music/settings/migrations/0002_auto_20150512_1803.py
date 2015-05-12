# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musicsettings',
            name='ordering',
            field=models.CharField(choices=[('sortname', 'By Artist (sortname)'), ('name', 'By Artist (full)')], default='sortname', max_length=20),
        ),
        migrations.AlterField(
            model_name='musicsettings',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]

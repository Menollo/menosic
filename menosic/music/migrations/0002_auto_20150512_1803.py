# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='albumstatus',
            field=models.ManyToManyField(to='music.AlbumStatus'),
        ),
        migrations.AlterField(
            model_name='album',
            name='albumtypes',
            field=models.ManyToManyField(to='music.AlbumType'),
        ),
        migrations.AlterField(
            model_name='album',
            name='artists',
            field=models.ManyToManyField(to='music.Artist'),
        ),
        migrations.AlterField(
            model_name='album',
            name='genres',
            field=models.ManyToManyField(to='music.Genre'),
        ),
        migrations.AlterField(
            model_name='album',
            name='labels',
            field=models.ManyToManyField(to='music.Label'),
        ),
        migrations.AlterField(
            model_name='artist',
            name='genres',
            field=models.ManyToManyField(to='music.Genre'),
        ),
        migrations.AlterField(
            model_name='track',
            name='artists',
            field=models.ManyToManyField(to='music.Artist'),
        ),
    ]

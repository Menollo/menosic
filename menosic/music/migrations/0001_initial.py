# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion

from django.conf import settings
import music.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, db_index=True)),
                ('date', models.CharField(max_length=15, null=True, db_index=True)),
                ('path', models.CharField(max_length=255, null=True, db_index=True)),
                ('musicbrainz_albumid', music.fields.UUIDField(max_length=32, blank=True, null=True)),
                ('musicbrainz_releasegroupid', music.fields.UUIDField(max_length=32, blank=True, null=True)),
            ],
            options={
                'ordering': ['date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlbumStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlbumType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('sortname', models.CharField(max_length=255, db_index=True)),
                ('path', models.CharField(max_length=255, null=True, db_index=True)),
                ('musicbrainz_artistid', music.fields.UUIDField(max_length=32, blank=True, null=True)),
            ],
            options={
                'ordering': ['sortname'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('backend', models.CharField(max_length=1, choices=[('T', 'Tags'), ('F', 'Files'), ('R', 'Remote')])),
                ('location', models.CharField(max_length=255)),
                ('sendfile_location', models.CharField(max_length=255, blank=True, null=True)),
                ('disabled', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LastPlayed',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('file_path', models.CharField(max_length=255, null=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('collection', models.ForeignKey(to='music.Collection', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['-time'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=1, choices=[('B', 'Browser'), ('E', 'External'), ('C', 'Client')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaylistTrack',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('file_path', models.CharField(max_length=255, null=True)),
                ('sort_order', models.IntegerField()),
                ('collection', models.ForeignKey(to='music.Collection', on_delete=django.db.models.deletion.CASCADE)),
                ('playlist', models.ForeignKey(to='music.Playlist', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('discnumber', models.PositiveIntegerField(null=True)),
                ('tracknumber', models.PositiveIntegerField(null=True)),
                ('title', models.CharField(max_length=255)),
                ('length', models.PositiveIntegerField(null=True)),
                ('bitrate', models.PositiveIntegerField(null=True)),
                ('filetype', models.CharField(max_length=15, null=True)),
                ('filesize', models.PositiveIntegerField(null=True)),
                ('mtime', models.DateTimeField(null=True)),
                ('path', models.CharField(max_length=255, db_index=True)),
                ('musicbrainz_trackid', music.fields.UUIDField(max_length=32, blank=True, null=True)),
                ('album', models.ForeignKey(null=True, to='music.Album', on_delete=django.db.models.deletion.CASCADE)),
                ('artists', models.ManyToManyField(null=True, to='music.Artist')),
                ('collection', models.ForeignKey(to='music.Collection', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['discnumber', 'tracknumber'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='track',
            unique_together=set([('collection', 'path')]),
        ),
        migrations.AddField(
            model_name='playlisttrack',
            name='tags_track',
            field=models.ForeignKey(null=True, to='music.Track', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='playlist',
            field=models.OneToOneField(to='music.Playlist', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='player',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lastplayed',
            name='tags_track',
            field=models.ForeignKey(null=True, to='music.Track', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lastplayed',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='collection',
            field=models.ForeignKey(to='music.Collection', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='country',
            field=models.ForeignKey(null=True, to='music.Country', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='genres',
            field=models.ManyToManyField(null=True, to='music.Genre'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='artist',
            unique_together=set([('collection', 'name'), ('collection', 'path')]),
        ),
        migrations.AddField(
            model_name='album',
            name='albumstatus',
            field=models.ManyToManyField(null=True, to='music.AlbumStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='albumtypes',
            field=models.ManyToManyField(null=True, to='music.AlbumType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='artists',
            field=models.ManyToManyField(null=True, to='music.Artist'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='collection',
            field=models.ForeignKey(to='music.Collection', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='country',
            field=models.ForeignKey(null=True, to='music.Country', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='genres',
            field=models.ManyToManyField(null=True, to='music.Genre'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='labels',
            field=models.ManyToManyField(null=True, to='music.Label'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='album',
            unique_together=set([('collection', 'path'), ('collection', 'musicbrainz_albumid')]),
        ),
    ]

# Generated by Django 5.1.5 on 2025-02-17 02:36

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SongDetail',
            fields=[
                ('song_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('artists', models.JSONField()),
                ('lyrics', models.TextField(null=True)),
                ('lyrics_last_updated', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('spotify_refresh_token', models.TextField(null=True)),
                ('spotify_access_token', models.TextField(null=True)),
                ('token_expires_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ListeningContext',
            fields=[
                ('context_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('context', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='songsmith.profile')),
            ],
        ),
        migrations.CreateModel(
            name='PlayHistory',
            fields=[
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('liked', models.BooleanField(null=True)),
                ('order_in_list', models.IntegerField()),
                ('played_at', models.DateTimeField(auto_now_add=True)),
                ('context', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='songsmith.listeningcontext')),
                ('song', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='songsmith.songdetail')),
            ],
            options={
                'ordering': ['-played_at'],
            },
        ),
    ]

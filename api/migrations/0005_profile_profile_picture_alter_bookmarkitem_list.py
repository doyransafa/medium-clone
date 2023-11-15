# Generated by Django 4.2.7 on 2023-11-14 21:51

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_bookmarkitem_list_alter_follow_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.get_upload_path),
        ),
        migrations.AlterField(
            model_name='bookmarkitem',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='api.list'),
        ),
    ]
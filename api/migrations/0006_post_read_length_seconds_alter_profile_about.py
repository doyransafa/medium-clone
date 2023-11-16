# Generated by Django 4.2.7 on 2023-11-15 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_profile_profile_picture_alter_bookmarkitem_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='read_length_seconds',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='about',
            field=models.TextField(blank=True, default='', max_length=5000),
        ),
    ]

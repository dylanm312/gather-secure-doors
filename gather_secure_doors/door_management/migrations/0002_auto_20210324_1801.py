# Generated by Django 3.1.7 on 2021-03-25 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('door_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='door',
            name='door_name',
            field=models.CharField(default='door', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='room_name',
            field=models.CharField(default='room', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workspace',
            name='workspace_name',
            field=models.CharField(default='workspace', max_length=200),
            preserve_default=False,
        ),
    ]
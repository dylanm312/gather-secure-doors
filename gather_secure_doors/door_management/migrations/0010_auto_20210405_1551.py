# Generated by Django 3.1.7 on 2021-04-05 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('door_management', '0009_remove_door_door_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='door',
            name='closed_image',
            field=models.ImageField(blank=True, null=True, upload_to='doors'),
        ),
        migrations.AlterField(
            model_name='door',
            name='open_image',
            field=models.ImageField(blank=True, null=True, upload_to='doors'),
        ),
        migrations.AlterField(
            model_name='workspace',
            name='api_key',
            field=models.CharField(help_text='Get one here: https://gather.town/apiKeys', max_length=200),
        ),
        migrations.AlterField(
            model_name='workspace',
            name='workspace_id',
            field=models.CharField(help_text='Last two segments of gather URL separated by one backslash. ie. BMcBcCSENP5Duahv\ryantest1', max_length=200),
        ),
    ]

# Generated by Django 3.2 on 2023-04-07 04:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0010_auto_20230407_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
    ]
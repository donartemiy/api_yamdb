# Generated by Django 3.2 on 2023-04-07 04:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0011_remove_title_rating'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='title',
            name='title_unique',
        ),
    ]

# Generated by Django 2.1 on 2018-10-21 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='tickets',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
# Generated by Django 5.1.7 on 2025-03-25 07:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('word_collection', '0002_rename_theme_category_rename_theme_word_categories_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='created_date_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 25, 7, 38, 31, 309735, tzinfo=datetime.timezone.utc)),
        ),
    ]

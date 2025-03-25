# Generated by Django 5.1.7 on 2025-03-25 07:38

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('word_collection', '0003_alter_word_created_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='created_date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

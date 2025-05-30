# Generated by Django 5.1.7 on 2025-04-11 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('word_collection', '0007_word_part_of_speech'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='word',
            name='example',
        ),
        migrations.RemoveField(
            model_name='word',
            name='translation',
        ),
        migrations.AddField(
            model_name='word',
            name='examples',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='word',
            name='other_forms',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='word',
            name='translations',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='word',
            name='usage_variants',
            field=models.JSONField(default=dict),
        ),
    ]

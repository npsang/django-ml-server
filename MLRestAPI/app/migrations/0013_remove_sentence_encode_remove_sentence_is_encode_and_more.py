# Generated by Django 4.1.5 on 2023-02-11 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_sentence_content_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentence',
            name='encode',
        ),
        migrations.RemoveField(
            model_name='sentence',
            name='is_encode',
        ),
        migrations.AddField(
            model_name='document',
            name='encode',
            field=models.BinaryField(editable=True, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='is_encode',
            field=models.BooleanField(default=False),
        ),
    ]
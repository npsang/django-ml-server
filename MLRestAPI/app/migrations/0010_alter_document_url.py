# Generated by Django 4.1.5 on 2023-02-11 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_document_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='url',
            field=models.URLField(null=True),
        ),
    ]

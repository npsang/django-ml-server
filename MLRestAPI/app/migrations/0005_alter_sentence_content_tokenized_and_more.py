# Generated by Django 4.1.5 on 2023-02-04 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_document_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentence',
            name='content_tokenized',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='encode',
            field=models.BinaryField(null=True),
        ),
    ]

# Generated by Django 3.1.6 on 2021-10-01 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_auto_20210929_2222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liveequityresult',
            name='date',
            field=models.DateTimeField(),
        ),
    ]

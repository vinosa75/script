# Generated by Django 3.1.6 on 2021-10-11 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_livesegment_change_perc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livesegment',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='livesegment',
            name='time',
            field=models.TimeField(),
        ),
    ]
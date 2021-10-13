# Generated by Django 3.1.6 on 2021-10-14 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_auto_20211011_0200'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestEquityResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('date', models.DateTimeField()),
                ('symbol', models.CharField(default='', max_length=20)),
                ('open', models.CharField(default='', max_length=20)),
                ('high', models.CharField(default='', max_length=20)),
                ('low', models.CharField(default='', max_length=20)),
                ('prev_day_close', models.CharField(default='', max_length=20)),
                ('ltp', models.CharField(max_length=20)),
                ('strike', models.CharField(max_length=20)),
                ('opencrossed', models.CharField(default='', max_length=20)),
            ],
        ),
    ]

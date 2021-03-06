# Generated by Django 3.1.6 on 2021-09-23 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_liveequityresult_opencrossed'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveOIPercentChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('call1', models.CharField(default='', max_length=20)),
                ('call2', models.CharField(default='', max_length=20)),
                ('put1', models.CharField(default='', max_length=20)),
                ('put2', models.CharField(default='', max_length=20)),
                ('callstrike', models.CharField(max_length=20)),
                ('putstrike', models.CharField(max_length=20)),
                ('symbol', models.CharField(max_length=20)),
                ('expiry', models.DateField()),
                ('strikegap', models.CharField(default='', max_length=20)),
            ],
        ),
    ]

# Generated by Django 3.1.6 on 2021-09-20 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryOIChange',
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
            ],
        ),
        migrations.CreateModel(
            name='HistoryOITotal',
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
            ],
        ),
        migrations.CreateModel(
            name='LiveEquityResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('date', models.DateField(blank=True, null=True)),
                ('symbol', models.CharField(default='', max_length=20)),
                ('open', models.CharField(default='', max_length=20)),
                ('high', models.CharField(default='', max_length=20)),
                ('low', models.CharField(default='', max_length=20)),
                ('prev_day_close', models.CharField(default='', max_length=20)),
                ('ltp', models.CharField(max_length=20)),
                ('strike', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='LiveOIChange',
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
            ],
        ),
        migrations.CreateModel(
            name='LiveOITotal',
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
            ],
        ),
        migrations.CreateModel(
            name='LiveOITotalAllSymbol',
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
                ('callone', models.CharField(default='', max_length=20)),
                ('putone', models.CharField(default='', max_length=20)),
                ('callhalf', models.CharField(default='', max_length=20)),
                ('puthalf', models.CharField(default='', max_length=20)),
            ],
        ),
    ]

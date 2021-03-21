# Generated by Django 3.1.7 on 2021-03-21 12:09

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('poly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=3035)),
                ('type', models.CharField(choices=[('CTRY', 'Country'), ('REG', 'Region'), ('CNTY', 'County/Unitary Authority'), ('LA', 'Local Authority District')], default='LA', max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('cluster_id', models.UUIDField(primary_key=True, serialize=False)),
                ('area', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('points_in_cluster', models.IntegerField(default=0)),
            ],
        ),
    ]

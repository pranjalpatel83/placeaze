# Generated by Django 5.0 on 2024-03-14 17:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place_aze', '0013_test'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('spid', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=55)),
                ('mob', models.IntegerField(max_length=10)),
                ('interestedCourse', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=255)),
                ('picture', models.ImageField(upload_to='studentPics/')),
                ('spUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

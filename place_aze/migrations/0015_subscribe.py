# Generated by Django 4.2.6 on 2024-03-18 07:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('place_aze', '0014_studentprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('sUid', models.BigAutoField(primary_key=True, serialize=False)),
                ('stid', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('subscribeDate', models.DateTimeField(auto_now_add=True)),
                ('sUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

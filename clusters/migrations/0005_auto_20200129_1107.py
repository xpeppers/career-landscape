# Generated by Django 3.0.2 on 2020-01-29 10:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("clusters", "0004_auto_20200129_1059"),
    ]

    operations = [
        migrations.AlterField(
            model_name="score",
            name="date",
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]

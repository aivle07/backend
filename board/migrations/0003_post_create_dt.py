# Generated by Django 4.2 on 2023-12-20 06:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0002_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="create_dt",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="CREATE DT"
            ),
        ),
    ]
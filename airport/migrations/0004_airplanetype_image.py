# Generated by Django 5.1.7 on 2025-06-28 10:39

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0003_order_customer"),
    ]

    operations = [
        migrations.AddField(
            model_name="airplanetype",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airport.models.movie_image_file_path
            ),
        ),
    ]

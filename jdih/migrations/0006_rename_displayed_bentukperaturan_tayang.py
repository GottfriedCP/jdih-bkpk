# Generated by Django 4.2.9 on 2024-05-07 06:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jdih", "0005_bentukperaturan_displayed_alter_peraturan_mencabuts"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bentukperaturan",
            old_name="displayed",
            new_name="tayang",
        ),
    ]

# Generated by Django 5.1.5 on 2025-02-04 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_address_customuser_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_username_change',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

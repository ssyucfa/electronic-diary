# Generated by Django 3.2.6 on 2021-08-18 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnevnik', '0003_user_is_in_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_in_class',
            field=models.BooleanField(default=False),
        ),
    ]
# Generated by Django 3.2.6 on 2021-08-17 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnevnik', '0007_alter_user_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]